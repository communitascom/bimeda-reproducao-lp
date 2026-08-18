"""Remonta a foto de familia da Linha Bimeda Reproducao.

Cada peca vem do pack shot original do banco da Bimeda, e nao recortada da
foto antiga. O script limpa a sombra de estudio que vem gravada em cada
arquivo (cada uma de uma luz diferente), harmoniza a escala e devolve uma
unica sombra de contato por produto, todas da mesma luz.
"""
from PIL import Image, ImageFilter, ImageDraw
import numpy as np, os, json, sys

B = os.path.expanduser('~/Library/CloudStorage/GoogleDrive-communitas@communitas.com.br/'
                       'Drives compartilhados/Communitas Com./BIMEDA')
SAIDA = os.path.join(os.path.dirname(__file__), '..', 'assets', 'img')

H, BASE = 1000, 880          # altura da arte e linha de chao
LIGHT_DX = 0.055             # luz vem da esquerda alta: a sombra escorre um pouco pra direita
SH_ALPHA = 0.20              # sombra discretissima
SH_BLUR  = 0.055             # desfoque, em fracao da largura do produto

# ordem = a do texto da secao: eCG, Biprogest, Energect, Sincroben, Clocio
PECAS = [
  # chave        arquivo                                                                 altura  folga  avanco
  ('ecg',        os.path.join(os.path.dirname(__file__), 'ecg-recorte-limpo.png'),                                                        500,  -34,  16),
  ('biprogest',  B+'/imagens/produtos/Biprogest/Embalagem Biprogest.png',                    820,  -46,   0),
  ('energect',   B+'/materiais enviados/2025/Energect/Materiais do Folheto Energect/'
                   'Cartucho - Energect FC 1000 mL - Direita.png',                          790,  -52,   0),
  ('sincroben',  B+'/imagens/produtos/Sincroben/Frasco + Cartucho - Sincroben 50 mL.png',   490,  -58,  12),
  ('clocio',     B+'/imagens/produtos/Clocio/Frasco + Cartucho - Clocio 20 mL.png',         425,    0,  20),
]

# quem esta na frente: as pecas baixas das pontas avancam, as altas do meio recuam
ORDEM_Z = ['biprogest', 'energect', 'ecg', 'sincroben', 'clocio']

def limpar(path):
    """Tira a sombra difusa gravada no arquivo, mantendo a borda do produto."""
    im = Image.open(path).convert('RGBA')
    a  = np.array(im)[:, :, 3]
    core = a > 200
    fill = np.zeros_like(core)
    for x in range(core.shape[1]):
        ys = np.where(core[:, x])[0]
        if len(ys):
            fill[ys.min():ys.max()+1, x] = True
    m = Image.fromarray((fill*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    out = np.array(im)
    out[:, :, 3] = (a.astype(np.float32) * (np.array(m)/255.0)).astype(np.uint8)
    im = Image.fromarray(out)
    return im.crop(im.split()[3].getbbox())

def cartucho(im):
    """Extensao vertical da peca mais alta da unidade (o cartucho ou o sache)."""
    a = np.array(im)[:, :, 3] > 190
    W, Hh = im.size
    tops = np.array([ (np.where(a[:, x])[0][0] if a[:, x].any() else Hh) for x in range(W) ])
    cols = np.where(tops <= tops.min() + 0.10*Hh)[0]
    ys = np.where(a[:, cols.min():cols.max()+1].any(axis=1))[0]
    return int(ys.min()), int(ys.max())

unidades = []
for chave, path, alvo, folga, avanco in PECAS:
    im = limpar(path)
    top, bot = cartucho(im)
    k = alvo / (bot - top)
    im = im.resize((max(1, round(im.width*k)), max(1, round(im.height*k))), Image.LANCZOS)
    unidades.append(dict(chave=chave, im=im, cart_bot=round(bot*k), folga=folga, avanco=avanco))
    print(f'{chave:10s} {im.size}  base do cartucho em {round(bot*k)}')

MARGEM = 40
x = MARGEM
for u in unidades:
    u['x'] = x
    x += u['im'].width + u['folga']
W = x - unidades[-1]['folga'] + MARGEM

canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))

# 1) as sombras primeiro, todas da mesma luz
sh = Image.new('L', (W, H), 0)
d  = ImageDraw.Draw(sh)
for u in unidades:
    im, x0 = u['im'], u['x']
    a  = np.array(im)[:, :, 3] > 190
    ys = np.where(a.any(axis=1))[0]
    pe = ys.max()                                    # ponto mais baixo da peca
    faixa = a[max(0, pe-round(im.height*0.05)):pe+1] # largura do produto junto ao chao
    xs = np.where(faixa.any(axis=0))[0]
    if not len(xs): continue
    cx0, cx1 = x0 + xs.min(), x0 + xs.max()
    largura  = cx1 - cx0
    y = BASE + u['avanco'] + (pe - u['cart_bot'])    # o chao de cada peca segue a base do cartucho
    desloc = round(largura * LIGHT_DX)
    d.ellipse([cx0 + round(largura*0.04) + desloc, y - round(largura*0.045),
               cx1 - round(largura*0.04) + desloc, y + round(largura*0.052)], fill=255)
sh = sh.filter(ImageFilter.GaussianBlur(round(W*SH_BLUR/10)))
sh = sh.point(lambda v: int(v*SH_ALPHA))
canvas.paste(Image.new('RGBA', (W, H), (58, 68, 86, 255)), (0, 0), sh)

# 2) os produtos, da esquerda para a direita, cada um a frente do anterior
for chave in ORDEM_Z:
    u = next(u for u in unidades if u['chave'] == chave)
    canvas.alpha_composite(u['im'], (u['x'], BASE + u['avanco'] - u['cart_bot']))

canvas = canvas.crop(canvas.getbbox())
canvas.save(os.path.join(SAIDA, 'produtos-familia.png'), optimize=True)
canvas.save(os.path.join(SAIDA, 'produtos-familia.webp'), quality=90, method=6)
print('arte final', canvas.size)
