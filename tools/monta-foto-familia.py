"""Remonta a foto de familia da Linha Bimeda Reproducao.

Regra dura: nenhum pixel dos produtos e alterado. Os pack shots entram
exatamente como vieram do banco da Bimeda, so recorte lossless (bbox do
alfa) e reescala (LANCZOS). Nenhuma limpeza de alfa toca o produto: a
funcao de sombra so mexe em pixels comprovadamente fora de um halo de
protecao ao redor de qualquer pixel opaco, entao rotulo, texto e detalhe
fino nunca sao tocados.

O fundo e branco puro, igual ao resto do site. Duas vias generativas foram
testadas e descartadas antes desta: (1) compor os cinco produtos inteiros
no Higgsfield (Nano Banana 2), com os pack shots reais como referencia de
imagem, luz e sombra saiam otimas mas o modelo reescrevia o texto miudo do
rotulo, e reescrevia errado ("ECC, PHEC" no lugar de "ECG, PMSG", "USG
VETERINARIO" no lugar de "USO VETERINARIO", dosagem trocada no Sincroben);
(2) gerar so uma chapa de estudio vazia via IA para servir de fundo, e
compor os produtos reais por cima, descartado por deixar a composicao
"montada" demais numa pagina que ja e branca do inicio ao fim. A montagem
final e 100% compositing de pixel real, sem generativa nenhuma tocando
produto.

Composicao: o Biprogest e o produto-heroi, centralizado. eCG e Energect
ficam DE PROPOSITO atras dele (sobreposicao explicita, nao por evitar
colisao: o Biprogest, pintado por cima, cobre a parte de tras). Sincroben
e Clocio ficam no mesmo tamanho, encostados um no outro na frente, a
direita, usando o encaixe por silhueta (esse sim evita colisao de
verdade: calcula, linha por linha no eixo Y do canvas final, a borda
visual real de cada produto, e nao a largura da caixa delimitadora, que
para pecas com apendice fino e diagonal como o aplicador do Biprogest e
bem maior que o produto em si).

As constantes ECG_VISIVEL_PX e ENERGECT_ESCONDIDO_FRAC foram calibradas
olhando o resultado: visivel o bastante pra ler "eCG" e "ENERGECT FC"
por inteiro, escondido o bastante pra ler como "atras" e nao "do lado".

Proporcao entre os produtos: nao inventada, exceto onde o cliente pediu
o contrario. Biprogest, Energect e a proporcao original vem da propria
foto que a Bimeda ja aprovou antes desta rodada, medida por altura solida
de cada cartucho. Sincroben e Clocio, que naquela foto tinham tamanhos
diferentes, foram igualados a pedido do cliente. O eCG, que nao existia
naquela foto, e a unica estimativa visual do script.

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
REF_H = 700   # altura de referencia do Energect na arte final, em px

# chave -> (arquivo, razao de altura relativa ao Energect, avanco vertical em px)
PECAS = {
  'ecg':       (os.path.join(AQUI, 'ecg-recorte-limpo.png'), 0.85, 14),
  'biprogest': (B+'/imagens/produtos/Biprogest/Embalagem + Produto Biprogest.png', 1.178, 0),
  'energect':  (B+'/materiais enviados/2025/Energect/Materiais do Folheto Energect/'
                  'Cartucho - Energect FC 1000 mL - Direita.png', 1.000, 0),
  'sincroben': (B+'/imagens/produtos/Sincroben/Frasco + Cartucho - Sincroben 50 mL.png', 0.78, 12),
  'clocio':    (B+'/imagens/produtos/Clocio/Frasco + Cartucho - Clocio 20 mL.png', 0.78, 20),
}
ECG_VISIVEL_PX = 710             # quanto do eCG fica visivel a esquerda do biprogest
ENERGECT_ESCONDIDO_FRAC = 0.27   # fracao do energect que fica atras do biprogest
GAP_FRENTE = -16                 # leve sobreposicao de contato entre pecas da frente (sincroben/clocio)

ORDEM_Z = ['ecg', 'energect', 'biprogest', 'sincroben', 'clocio']  # pintura: ultimo = mais na frente

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

def borda_saco(im, frac_topo=0.6):
    """Borda esquerda e direita reais do corpo principal do saco do Biprogest
    (sem o apendice fino do aplicador, que fica so na parte de baixo e alarga
    a caixa delimitadora bem mais que o produto em si)."""
    a = np.array(im)[:, :, 3] > 190
    topo = a[:round(im.height*frac_topo)]
    cols = np.where(topo.any(axis=0))[0]
    return int(cols.min()), int(cols.max())

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

def perfil_esq_dir(im):
    """Para cada linha local (y), a coluna mais a esquerda e mais a direita
    com pixel opaco, ou -1 se a linha nao tem conteudo. E o que permite
    encostar duas silhuetas de verdade em vez de usar a largura da caixa
    delimitadora."""
    a = np.array(im)[:, :, 3] > 190
    esq = np.full(im.height, -1, dtype=int)
    dir_ = np.full(im.height, -1, dtype=int)
    for y in range(im.height):
        xs = np.where(a[y])[0]
        if len(xs):
            esq[y] = xs.min()
            dir_[y] = xs.max()
    return esq, dir_

def encaixar(prev, cur, gap):
    """Posiciona `cur` encostando na silhueta real de `prev`, sem colidir:
    calcula, linha por linha, o deslocamento minimo que respeita `gap`
    (negativo = leve sobreposicao) em toda a faixa de Y onde os dois tem
    conteudo."""
    y0 = max(prev['oy'], cur['oy'])
    y1 = min(prev['oy'] + len(prev['dir_']), cur['oy'] + len(cur['esq']))
    dx = None
    for y in range(y0, y1):
        pd = prev['dir_'][y - prev['oy']]
        ce = cur['esq'][y - cur['oy']]
        if pd < 0 or ce < 0:
            continue
        necessario = (prev['x'] + pd + gap) - ce
        dx = necessario if dx is None else max(dx, necessario)
    return dx if dx is not None else prev['x'] + prev['im'].width + gap

unidades = {}
for chave, (path, razao, avanco) in PECAS.items():
    im_orig = carregar_sem_tocar(path)
    protecao = max(6, round(im_orig.height * 0.012))
    im = sombra_segura(im_orig, protecao)
    top, bot = cartucho(im)
    alvo = REF_H * razao
    k = alvo / (bot - top)
    im2 = im.resize((max(1, round(im.width*k)), max(1, round(im.height*k))), Image.LANCZOS)
    cart_bot = round(bot*k)
    oy = BASE + avanco - cart_bot
    esq, dir_ = perfil_esq_dir(im2)
    unidades[chave] = dict(chave=chave, im=im2, oy=oy, esq=esq, dir_=dir_)
    print(f'{chave:10s} razao={razao:.3f}  tamanho final {im2.size}')

MARGEM = 60
biprogest = unidades['biprogest']
saco_esq, saco_dir = borda_saco(biprogest['im'])

# biprogest: reserva espaco a esquerda para o eCG espiar ate a borda real do saco
biprogest['x'] = MARGEM + ECG_VISIVEL_PX - saco_esq

# eCG: sobreposicao explicita ate a borda real do saco, ele fica atras (pintado antes)
ecg = unidades['ecg']
pouch_esq = biprogest['x'] + saco_esq
ecg['x'] = pouch_esq - ECG_VISIVEL_PX

# energect: sobreposicao explicita do outro lado, tambem pela borda real do saco
pouch_dir = biprogest['x'] + saco_dir
energect = unidades['energect']
energect['x'] = pouch_dir - round(energect['im'].width * ENERGECT_ESCONDIDO_FRAC)

# sincroben, clocio: encaixe por silhueta (evita colisao de verdade), a frente
sincroben = unidades['sincroben']
sincroben['x'] = encaixar(energect, sincroben, GAP_FRENTE)
clocio = unidades['clocio']
clocio['x'] = encaixar(sincroben, clocio, GAP_FRENTE)

xmax = max(u['x'] + u['im'].width for u in unidades.values())
xmin = min(u['x'] for u in unidades.values())
DESLOC = MARGEM - xmin
for u in unidades.values():
    u['x'] += DESLOC
W = xmax + DESLOC + MARGEM

canvas = Image.new('RGBA', (W, H), (255, 255, 255, 255))

# sombra de contato procedural, unica luz, mesma pra todos os produtos
sh = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(sh)
for u in unidades.values():
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
    y = u['oy'] + pe
    desloc = round(largura * 0.06)
    d.ellipse([cx0 + round(largura*0.04) + desloc, y - round(largura*0.04),
               cx1 - round(largura*0.04) + desloc, y + round(largura*0.05)], fill=255)
sh = sh.filter(ImageFilter.GaussianBlur(round(W*0.006)))
sh = sh.point(lambda v: int(v*0.20))
canvas.paste(Image.new('RGBA', (W, H), (58, 68, 86, 255)), (0, 0), sh)

for chave in ORDEM_Z:
    u = unidades[chave]
    canvas.alpha_composite(u['im'], (u['x'], u['oy']))

canvas = canvas.crop((0, 0, W, H))
canvas.save(os.path.join(SAIDA, 'produtos-familia.png'), optimize=True)
canvas.save(os.path.join(SAIDA, 'produtos-familia.webp'), quality=90, method=6)
print('arte final', canvas.size)
