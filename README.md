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

## Conteúdo

Todo o texto, os dados e os protocolos vieram do folheto
`Linha_BR_CATALOG_DIGITAL_BR_MR26_0024.pdf`, conferidos item a item:

- **Biprogest:** 63,4% de prenhez (156/246) contra 59,6% do controle positivo (168/282), SBTE 2026
- **eCG BR:** 6,3 folículos contra 1,6 do controle, n=12 por grupo
- **Curva de P4:** 1º, 2º e 3º uso, de 0h a 192h após a inserção
- **Protocolos:** os quatro da página 7, com doses e dias

Os gráficos são recriados em SVG, não são imagens do PDF.
