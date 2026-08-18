"""Exporta os 5 pack shots da Linha Bimeda Reproducao como um PSD em
camadas separadas, ja limpos (sombra de estudio solta removida) e na
escala relativa validada em Clientes/Bimeda/README.md, mas SEM
posicionamento definitivo: cada camada entra numa fileira simples, sem
sobrepor, pronta pra ser arrastada e reposicionada a mao no Photoshop.

Por que existe: depois de varias rodadas tentando acertar espacamento e
profundidade por codigo (tools/monta-foto-familia.py), o cliente pediu
pra montar ele mesmo. Este script prepara a materia-prima (pack shots
limpos, na escala certa, sem sombra pra nao atrapalhar o ajuste manual);
tools/aplica-sombra-psd.py le o PSD ja reposicionado e gera o
produtos-familia.png/webp final.

Regra dura, igual em toda etapa: nenhum pixel de produto e alterado. Os
pack shots entram exatamente como vieram do banco da Bimeda, so recorte
lossless (bbox do alfa) e reescala.

Bug de ambiente: escreve com Compression.raw porque a versao instalada do
pytoshop (1.2.1) nao comprime RLE nesta maquina (o submodulo
pytoshop/packbits.pyx nunca foi compilado). Raw funciona, so gera arquivo
maior; o Photoshop recomprime normal ao salvar de volta.

Para rodar:
    python3 tools/exporta-psd-embalagens.py
"""
from PIL import Image, ImageFilter
import numpy as np, os
from pytoshop import enums
from pytoshop.user import nested_layers
from pytoshop.user.nested_layers import Image as PSDImage

B = os.path.expanduser('~/Library/CloudStorage/GoogleDrive-communitas@communitas.com.br/'
                       'Drives compartilhados/Communitas Com./BIMEDA')
AQUI = os.path.dirname(__file__)

REF_H = 700

# nome de exibicao, arquivo, razao de altura relativa ao Energect
PECAS = [
  ('eCG BR',      os.path.join(AQUI, 'ecg-recorte-limpo.png'), 0.85),
  ('Biprogest',   B+'/imagens/produtos/Biprogest/Embalagem + Produto Biprogest.png', 1.178),
  ('Energect FC', B+'/materiais enviados/2025/Energect/Materiais do Folheto Energect/'
                    'Cartucho - Energect FC 1000 mL - Direita.png', 1.000),
  ('Sincroben',   B+'/imagens/produtos/Sincroben/Frasco + Cartucho - Sincroben 50 mL.png', 0.78),
  ('Clocio',      B+'/imagens/produtos/Clocio/Frasco + Cartucho - Clocio 20 mL.png', 0.78),
]

def carregar_sem_tocar(path):
    im = Image.open(path).convert('RGBA')
    return im.crop(im.split()[3].getbbox())

def cartucho(im):
    a = np.array(im)[:, :, 3] > 190
    Wd, Hd = im.size
    tops = np.array([(np.where(a[:, x])[0][0] if a[:, x].any() else Hd) for x in range(Wd)])
    cols = np.where(tops <= tops.min() + 0.10*Hd)[0]
    ys = np.where(a[:, cols.min():cols.max()+1].any(axis=1))[0]
    return int(ys.min()), int(ys.max())

def sombra_segura(im, protecao_px):
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
    novo[~protegido] = 0
    out = np.array(im).copy()
    out[:, :, 3] = novo
    return Image.fromarray(out)

processadas = []
for nome, path, razao in PECAS:
    im_orig = carregar_sem_tocar(path)
    protecao = max(6, round(im_orig.height * 0.012))
    im = sombra_segura(im_orig, protecao)
    top, bot = cartucho(im)
    k = (REF_H * razao) / (bot - top)
    im2 = im.resize((max(1, round(im.width*k)), max(1, round(im.height*k))), Image.LANCZOS)
    processadas.append((nome, im2))
    print(f'{nome:14s} {im2.size}')

MARGEM, GAP = 60, 50
alturas = [im.height for _, im in processadas]
H = max(alturas) + MARGEM*2
x = MARGEM
layers = []
for nome, im in processadas:
    y = MARGEM + (max(alturas) - im.height)   # todos assentados na mesma linha de chao
    a = np.array(im)
    layers.append(PSDImage(
        name=nome, top=y, left=x, bottom=y+im.height, right=x+im.width,
        channels={
            enums.ChannelId.red: a[:, :, 0],
            enums.ChannelId.green: a[:, :, 1],
            enums.ChannelId.blue: a[:, :, 2],
            enums.ChannelId.transparency: a[:, :, 3],
        }))
    x += im.width + GAP
W = x - GAP + MARGEM

# ordem de camadas no PSD: topo da lista = topo do painel de camadas do Photoshop
layers = list(reversed(layers))

psd = nested_layers.nested_layers_to_psd(
    layers, enums.ColorMode.rgb, compression=enums.Compression.raw, size=(H, W))
out = os.path.expanduser('~/Library/CloudStorage/GoogleDrive-jr@communitas.com.br/Meu Drive/'
                          'Cérebro Communitas/Clientes/Bimeda/human-output/'
                          'bimeda-linha-producao-embalagens.psd')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'wb') as f:
    psd.write(f)
print('PSD salvo em', out, '| canvas', (W, H))
