"""Le o PSD com as 5 embalagens da Linha Bimeda Reproducao (montado a mao
no Photoshop, uma camada por produto, sem sombra), adiciona uma sombra de
contato procedural com luz unica, e exporta o produtos-familia.png/webp.

Por que existe: depois de varias rodadas tentando acertar espacamento e
profundidade por codigo (tools/monta-foto-familia.py), o cliente pediu pra
posicionar as embalagens ele mesmo no Photoshop, entregue como PSD em
camadas separadas (ver human-output/bimeda-linha-producao-embalagens.psd
no Drive). Esse script parte do PSD ja ajustado a mao: le a posicao real
de cada camada, adiciona so a sombra (que o PSD entregue nao tinha, de
proposito, pra nao atrapalhar o ajuste manual), e gera os arquivos finais.

Nao mexe em nenhum pixel de produto, mesma regra de sempre: a sombra e
desenhada num canvas separado, por baixo, os produtos entram por cima
exatamente como vieram do PSD.

Bug de ambiente: a versao instalada do pytoshop (1.2.1) nao le RLE porque
o submodulo pytoshop/packbits.pyx nunca foi compilado nesta maquina. Por
isso este script usa psd-tools (`pip3 install psd-tools`), que le PSD real
do Photoshop sem esse problema.

Para regerar depois de reajustar o PSD:
    python3 tools/aplica-sombra-psd.py
"""
from PIL import Image, ImageFilter, ImageDraw
from psd_tools import PSDImage
import numpy as np, os

PSD = os.path.expanduser('~/Library/CloudStorage/GoogleDrive-jr@communitas.com.br/Meu Drive/'
                          'Cérebro Communitas/Clientes/Bimeda/human-output/'
                          'bimeda-linha-producao-embalagens.psd')
AQUI = os.path.dirname(__file__)
SAIDA = os.path.join(AQUI, '..', 'assets', 'img')

# sombra: uma luz so, discreta, alargada o bastante pra nao ficar toda
# escondida embaixo do proprio produto (objetos estreitos como frascos
# tem pouca area de contato; sem alargar, a sombra nasce mais estreita
# que o produto e some por baixo dele)
OPACIDADE = 0.32
ALARGAMENTO = 0.16   # fracao da largura do produto que a sombra ganha pra cada lado
DESLOCAMENTO = 0.05  # fracao da largura: quanto a sombra escorre pra direita (luz da esquerda)

psd = PSDImage.open(PSD)
W, H = psd.width, psd.height

camadas = []
for layer in psd:
    im = layer.composite()
    l, t = layer.bbox[0], layer.bbox[1]
    camadas.append((layer.name, im, l, t))
    print(f'{layer.name:14s} {im.size}  em ({l}, {t})')

canvas = Image.new('RGBA', (W, H), (255, 255, 255, 255))

sh = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(sh)
for nome, im, x0, y0 in camadas:
    a = np.array(im)[:, :, 3] > 190
    ys = np.where(a.any(axis=1))[0]
    if not len(ys):
        continue
    pe = ys.max()
    faixa = a[max(0, pe - round(im.height * 0.06)):pe + 1]
    xs = np.where(faixa.any(axis=0))[0]
    if not len(xs):
        continue
    cx0, cx1 = x0 + xs.min(), x0 + xs.max()
    largura = max(cx1 - cx0, 40)
    y = y0 + pe
    desloc = round(largura * DESLOCAMENTO)
    alarga = round(largura * ALARGAMENTO)
    d.ellipse([cx0 - alarga + desloc, y - round(largura * 0.05),
               cx1 + alarga + desloc, y + round(largura * 0.11)], fill=255)
sh = sh.filter(ImageFilter.GaussianBlur(round(W * 0.0045)))
sh = sh.point(lambda v: int(v * OPACIDADE))
canvas.paste(Image.new('RGBA', (W, H), (52, 62, 80, 255)), (0, 0), sh)

for nome, im, x0, y0 in camadas:
    canvas.alpha_composite(im, (x0, y0))

canvas = canvas.crop(canvas.getbbox())
canvas.save(os.path.join(SAIDA, 'produtos-familia.png'), optimize=True)
canvas.save(os.path.join(SAIDA, 'produtos-familia.webp'), quality=90, method=6)
print('arte final', canvas.size)
