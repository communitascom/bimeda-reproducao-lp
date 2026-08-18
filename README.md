# Linha Bimeda Reprodução | Landing Page

**Communitas Com.** para Bimeda · Peça de origem: `BR_MR26_0024`
Destino final: `saudeanimal.bimeda.com.br`

---

## Em validação agora: a estrutura

👉 **[`wireframe/index.html`](wireframe/index.html)** é a versão de baixa fidelidade da LP, para o cliente
validar a **ordem das seções, o conteúdo de cada uma e a hierarquia da informação**. Cores, fotos e
tipografia finais não fazem parte desta etapa.

Para abrir, servir a pasta e acessar `/wireframe/`:

```bash
python3 -m http.server 4321
```

### Sequência proposta

| # | Seção | O que entra |
|---|-------|-------------|
| 01 | Abertura | Logo da linha, assinatura, 2 CTAs |
| 02 | Vídeo institucional | Vídeo de 1:40 e três destaques |
| 03 | eCG BR | O lançamento, com o pack shot inteiro e o gráfico de folículos |
| 04 | A linha completa | Foto de família e índice dos 5 produtos |
| 05 | Por que IATF | Texto de abertura e as 8 vantagens |
| 06 | Biprogest | Produto, diferenciais e os 2 gráficos |
| 07 | Energect FC | Produto, molécula BCAA e a figura das vias metabólicas |
| 08 | Sincroben | Produto e o papel dele no protocolo |
| 09 | Clocio | Produto e o papel dele no protocolo |
| 10 | Protocolos | Os 4 protocolos em abas, CTA para falar com consultores |
| 11 | A Bimeda | Institucional e os grandes números da empresa |
| 12 | Conversão | Formulário: folheto em PDF ou contato com consultor |
| 13 | Referências e rodapé | Fontes dos estudos e aviso de uso veterinário |

**Princípio da estrutura:** cada produto carrega o próprio resultado. Não existe uma seção de
"resultados" separada, porque solta do produto ela não convence.

---

## Estado do repositório

| Branch | O que tem |
|---|---|
| `master` | O wireframe (em validação) e a primeira versão da LP navegável |
| `lp-v2` | A LP em refinamento, já na linguagem visual do folheto. **Não subir ainda** |

A LP final entra em `master` depois que a estrutura for aprovada e o layout, afinado.

---

## Pendências com a Bimeda

1. **Pack shot do eCG BR em alta.** O recorte em uso na seção do produto e na foto de família da
   linha foi extraído do PDF do folheto, onde a imagem tem 764x431 px, e teve a sombra difusa do
   estúdio removida para bater com o restante da foto de família, que é recorte limpo. Sobram
   414x327 px de produto. Serve nas duas aplicações atuais, mas um arquivo de origem em resolução
   maior deixaria a peça pronta para qualquer uso.
   O mesmo vale para a foto de família: a versão em uso tem 2000x761 px, e existe uma de
   2780x1259 px em `BIMEDA/materiais enviados/Linha Reprodução/Bimeda Repro 2/(Gravação)/Produtos.png`,
   que vale adotar se a montagem for refeita.
2. **URLs das redes sociais.** Instagram, LinkedIn e Facebook estão presumidos a partir de `@bimedabrasil`.
3. **Link da política de privacidade** para o aceite do formulário.
4. **Hospedagem do vídeo.** Hoje o arquivo tem 18 MB e é servido pela própria página. Para produção,
   subir em YouTube ou Vimeo e trocar por embed.

## Pendências técnicas

- **Formulário → RD Station.** O ponto de integração está marcado em `assets/js/main.js`, no bloco
  `=== INÍCIO: substituir em produção ===`. Hoje o protótipo apenas valida no cliente e dispara o
  download do PDF.

---

## A foto de família da linha

O posicionamento final é **manual, no Photoshop**, não calculado por código. Depois de várias
rodadas tentando acertar espaçamento e profundidade por algoritmo (histórico abaixo), o resultado
seguia estranho aos olhos de quem entende de composição, o Junior pediu pra montar ele mesmo.

**Fluxo atual:**

1. `tools/exporta-psd-embalagens.py` prepara os 5 pack shots (recorte lossless, sombra de
   estúdio solta removida, escala relativa) e exporta um PSD com uma camada por produto, sem
   sobrepor e sem sombra, pronto pra arrastar.
2. O Junior reposiciona as camadas à mão no Photoshop e salva por cima do mesmo arquivo:
   `human-output/bimeda-linha-producao-embalagens.psd` (no Drive, fora do git, é `human-output/`).
3. `tools/aplica-sombra-psd.py` lê esse PSD, adiciona só a sombra de contato (o PSD entregue não
   tem, de propósito, pra não atrapalhar o ajuste manual) e gera `produtos-familia.png`/`.webp`.
   Para regerar depois de reajustar o PSD:

   ```bash
   python3 tools/aplica-sombra-psd.py
   ```

**Regra dura, em qualquer uma das duas etapas: nenhum pixel de produto é alterado.** Os pack shots
entram exatamente como vieram do banco da Bimeda, só recorte lossless (bbox do alfa) e reescala.
Isso não é só cuidado, é a lição de uma tentativa que não deu certo: testamos compor a foto inteira
no Higgsfield (Nano Banana 2), com os cinco pack shots reais como referência de imagem, e o
resultado tinha luz e sombra ótimas, mas reescrevia o texto miúdo dos rótulos, e reescrevia errado
("ECC, PHEC" no lugar de "ECG, PMSG", "USG VETERINÁRIO" no lugar de "USO VETERINÁRIO", dosagem
trocada no Sincroben). Para produto veterinário regulado isso é inaceitável.

**Bug de ambiente:** a versão instalada do `pytoshop` (1.2.1) não lê RLE, porque o submódulo
`pytoshop/packbits.pyx` nunca foi compilado nesta máquina. `aplica-sombra-psd.py` usa `psd-tools`
(`pip3 install psd-tools`) em vez disso, que lê PSD real do Photoshop sem esse problema.

**Sombra.** Discretíssima de propósito, uma luz só (vem de cima à esquerda) pra não deixar os
produtos "flutuando". A primeira versão nasceu estreita demais (a elipse ficava do tamanho da base
do produto, então quase toda escondida embaixo dele) e ficou invisível; a versão final alarga a
elipse além da silhueta do produto (`ALARGAMENTO`) pra ela realmente aparecer.

### Histórico: as tentativas por código que não vingaram

- **Fileira por silhueta**, encostando cada produto no vizinho pela borda visual real (não pela
  caixa delimitadora): resolveu o vão morto entre peças, mas ainda ficava tudo numa linha só, sem
  profundidade.
- **Profundidade calculada**, com eCG e Energect posicionados atrás do Biprogest por fórmula: o
  resultado tecnicamente fazia o que foi pedido, mas continuava "errado" pro olho, prova de que
  esse tipo de decisão de composição precisa mesmo de alguém olhando, não de coordenada calculada.

## Conteúdo

Todo o texto, os dados e os protocolos vieram do folheto
`Linha_BR_CATALOG_DIGITAL_BR_MR26_0024.pdf`, conferidos item a item:

- **Biprogest:** 63,4% de prenhez (156/246) contra 59,6% do controle positivo (168/282), SBTE 2026
- **eCG BR:** 6,3 folículos contra 1,6 do controle, n=12 por grupo
- **Curva de P4:** 1º, 2º e 3º uso, de 0h a 192h após a inserção
- **Protocolos:** os quatro da página 7, com doses e dias

Os gráficos são recriados em SVG, não são imagens do PDF.
