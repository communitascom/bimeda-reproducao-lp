"""Remonta a foto de familia da Linha Bimeda Reproducao.

Regra dura: nenhum pixel dos produtos e alterado. Os pack shots entram
exatamente como vieram do banco da Bimeda, so recorte lossless (bbox do
alfa) e reescala (LANCZOS). Nenhuma limpeza de alfa toca o produto: a
funcao de sombra so mexe em pixels comprovadamente fora de um halo de
protecao ao redor de qualquer pixel opaco, entao rotulo, texto e detalhe
fino nunca sao tocados.

O fundo e branco puro, igual ao resto do site. Foi testado gerar uma chapa
de estudio via IA (Higgsfield / Nano Banana) para servir de fundo, mas o
resultado ficou "montado" demais numa pagina que ja e branca do começo ao
fim: descartado. A propria tentativa de IA compor os produtos foi
descartada antes disso, por um motivo mais serio: o modelo reescreve texto
pequeno de rotulo, e reescreve errado (viu-se "ECC, PHEC" no lugar de
"ECG, PMSG", "USG VETERINARIO" no lugar de "USO VETERINARIO", dosagem
trocada). Produto veterinario regulado nao pode correr esse risco, entao a
montagem final e 100% compositing de pixel real, sem generativa nenhuma
tocando produto.

Proporcao entre os produtos: nao inventada. Vem da propria foto que a
Bimeda ja aprovou (a que estava no ar antes desta rodada), medida por
altura solida de cada cartucho. O eCG, que nao existia naquela foto, e a
unica estimativa visual do script.

Para regerar:
    python3 tools/monta-foto-familia.py
"""
from PIL import Image, ImageFilter, ImageDraw
import numpy as np, os

B = os.path.expanduser('~/Library/CloudStorage/GoogleDrive-communitas@communitas.com.br/'
                       'Drives compartilhados/Communitas Com./BIMEDA')
AQUI = os.path.dirname(__file__)
SAIDA = os.path.join(AQUI, '..', 'assets', 'img')

H, BASE = 1050, 900

# alturas medidas na foto ja aprovada pelo cliente (energect = referencia 601px = 1.0)
#   biprogest 708/601=1.178 | clocio-caixa 512/601=0.852 | sincroben-caixa 426/601=0.709
REF_H = 700  # altura de referencia do Energect na arte final, em px

PECAS = [
  # chave        arquivo                                                                razao  folga  avanco
  ('ecg',        os.path.join(AQUI, 'ecg-recorte-limpo.png'),                           0.62,  -70,  14),
  ('biprogest',  B+'/imagens/produtos/Biprogest/Embalagem + Produto Biprogest.png',      1.178, -330,  0),
  ('energect',   B+'/materiais enviados/2025/Energect/Materiais do Folheto Energect/'
                   'Cartucho - Energect FC 1000 mL - Direita.png',                      1.000, -46,   0),
  ('sincroben',  B+'/imagens/produtos/Sincroben/Frasco + Cartucho - Sincroben 50 mL.png',0.709, -58,  12),
  ('clocio',     B+'/imagens/produtos/Clocio/Frasco + Cartucho - Clocio 20 mL.png',      0.852,   0,  20),
]
ORDEM_Z = ['biprogest', 'energect', 'ecg', 'sincroben', 'clocio']

def carregar_sem_tocar(path):
    """Recorte lossless (so bbox do alfa). Nenhum pixel de produto e alterado aqui."""
    im = Image.open(path).convert('RGBA')
    return im.crop(im.split()[3].getbbox())

def cartucho(im):
    """Extensao vertical da peca mais alta da unidade (o cartucho ou o sache)."""
    a = np.array(im)[:, :, 3] > 190
    Wd, Hd = im.size
    tops = np.array([(np.where(a[:, x])[0][0] if a[:, x].any() else Hd) for x in range(Wd)])
    cols = np.where(tops <= tops.min() + 0.10*Hd)[0]
    ys = np.where(a[:, cols.min():cols.max()+1].any(axis=1))[0]
    return int(ys.min()), int(ys.max())

def sombra_segura(im, protecao_px):
    """Apaga a sombra de estudio solta, sem nunca reduzir alfa de nada que
    esteja a menos de `protecao_px` de um pixel opaco. Isso garante que
    rotulo, texto e detalhe fino do produto nunca sao tocados: so o halo
    difuso de sombra do proprio estudio original, quando existe e esta
    claramente desconectado do produto, e que some.

    A dilatacao (MaxFilter) roda numa mascara reduzida por velocidade: ela
    so decide ONDE a sombra pode ser apagada, nunca altera o pixel do
    produto, entao trabalhar em resolucao menor no calculo da mascara nao
    tira precisao de rotulo nenhuma."""
    a = np.array(im)[:, :, 3]
    opaco = a > 200
    escala = min(1.0, 900 / max(im.size))
    peq = Image.fromarray((opaco*255).astype(np.uint8))
    if escala < 1.0:
        peq = peq.resize((max(1, round(im.width*escala)), max(1, round(im.height*escala))), Image.NEAREST)
    kernel = max(3, round(protecao_px*escala)*2+1)
    peq = peq.filter(ImageFilter.MaxFilter(kernel))
    if escala < 1.0:
        peq = peq.resize(im.size, Image.NEAREST)
    protegido = np.array(peq) > 0
    novo = a.copy()
    novo[~protegido] = 0        # so aqui, fora da zona protegida, a sombra do arquivo original some
    out = np.array(im).copy()
    out[:, :, 3] = novo
    return Image.fromarray(out)

unidades = []
for chave, path, razao, folga, avanco in PECAS:
    im_orig = carregar_sem_tocar(path)
    protecao = max(6, round(im_orig.height * 0.012))
    im = sombra_segura(im_orig, protecao)
    top, bot = cartucho(im)
    alvo = REF_H * razao
    k = alvo / (bot - top)
    im2 = im.resize((max(1, round(im.width*k)), max(1, round(im.height*k))), Image.LANCZOS)
    unidades.append(dict(chave=chave, im=im2, cart_bot=round(bot*k), folga=folga, avanco=avanco))
    print(f'{chave:10s} razao={razao:.3f}  tamanho final {im2.size}')

MARGEM = 60
x = MARGEM
for u in unidades:
    u['x'] = x
    x += u['im'].width + u['folga']
W = x - unidades[-1]['folga'] + MARGEM

canvas = Image.new('RGBA', (W, H), (255, 255, 255, 255))

# sombra de contato procedural, unica luz, mesma pra todos os produtos
sh = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(sh)
for u in unidades:
    im, x0 = u['im'], u['x']
    a = np.array(im)[:, :, 3] > 190
    ys = np.where(a.any(axis=1))[0]
    if not len(ys): continue
    pe = ys.max()
    faixa = a[max(0, pe-round(im.height*0.05)):pe+1]
    xs = np.where(faixa.any(axis=0))[0]
    if not len(xs): continue
    cx0, cx1 = x0 + xs.min(), x0 + xs.max()
    largura = cx1 - cx0
    y = BASE + u['avanco'] + (pe - u['cart_bot'])
    desloc = round(largura * 0.06)
    d.ellipse([cx0 + round(largura*0.04) + desloc, y - round(largura*0.04),
               cx1 - round(largura*0.04) + desloc, y + round(largura*0.05)], fill=255)
sh = sh.filter(ImageFilter.GaussianBlur(round(W*0.006)))
sh = sh.point(lambda v: int(v*0.20))
canvas.paste(Image.new('RGBA', (W, H), (58, 68, 86, 255)), (0, 0), sh)

for chave in ORDEM_Z:
    u = next(u for u in unidades if u['chave'] == chave)
    canvas.alpha_composite(u['im'], (u['x'], BASE + u['avanco'] - u['cart_bot']))

canvas = canvas.crop((0, 0, W, H))
canvas.save(os.path.join(SAIDA, 'produtos-familia.png'), optimize=True)
canvas.save(os.path.join(SAIDA, 'produtos-familia.webp'), quality=90, method=6)
print('arte final', canvas.size)
