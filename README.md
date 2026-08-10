# Linha Bimeda Reprodução — Landing Page

Protótipo da landing page da linha reprodutiva da Bimeda, para aprovação antes de subir em
`saudeanimal.bimeda.com.br`.

**Communitas Com.** · Código da peça de origem: `BR_MR26_0024`

---

## Como rodar

Site estático, sem build. Basta servir a pasta:

```bash
python3 -m http.server 4321
```

E abrir `http://localhost:4321`.

---

## Estrutura da página

| # | Seção | O que faz |
|---|-------|-----------|
| 1 | Hero | Assinatura da linha + 2 CTAs + faixa de números |
| 2 | Vídeo | Institucional de 1:40 (`#video`) |
| 3 | Por que IATF | Os 8 benefícios do folheto |
| 4 | Produtos | Biprogest e eCG BR em cards largos; Sincroben, Clocio e Energect FC em trio |
| 5 | Protocolos | 4 protocolos em abas com timeline Dia 0 → Dia 10 |
| 6 | Resultados | 3 gráficos em SVG, animados na entrada |
| 7 | A Bimeda | Institucional + contadores (80 países, 8 P&D, 7 labs, 9 fábricas, 6 países) |
| 8 | Folheto | Formulário de captura → download do PDF |
| 9 | Referências | Fontes dos estudos + aviso de uso veterinário |

---

## O que precisa ser trocado antes de publicar

### 1. Formulário → RD Station
`assets/js/main.js` tem o bloco marcado `=== INÍCIO: substituir em produção ===`.
Hoje o protótipo apenas valida no cliente, loga o lead no console e dispara o download.
Trocar pelo envio ao RD Station (`conversion_identifier`) ou ao endpoint da Bimeda,
e disparar o evento de analytics.

### 2. Vídeo
`assets/video/bimeda-reproducao.mp4` — 18 MB, 1280×720, recomprimido do master
`Bimeda Reprodução Final6.mov` (1920×1080, 145 MB).
**Para produção, subir no YouTube/Vimeo e trocar por embed**, para não servir 18 MB do próprio
servidor. O `poster` já está em `assets/img/video-poster.jpg`.

### 3. Imagens de produto
Os recortes foram extraídos do material enviado:

| Arquivo | Origem |
|---|---|
| `prod-biprogest`, `prod-clocio`, `prod-sincroben`, `prod-energect`, `produtos-familia` | recorte de `Produtos.png` (fundo transparente, alta resolução) |
| `prod-ecgbr` | página 6 do folheto em PDF, 400 dpi |
| `hero-bovinos` | `Links/Vaca DNA 6.png` (5504×3204) |
| `fabrica-envase` | página 2 do folheto |
| `logo-br-branco`, `logo-bimeda-branco` | PNGs do projeto de After Effects |

**Pendência:** o eCG BR é o único produto sem recorte com fundo transparente — saiu da página do
PDF, com o gradiente azul de fundo. Por isso ele ganhou o card escuro (que também funciona como
destaque de lançamento). Se a Bimeda enviar o render original do pack em PNG com transparência,
é só substituir o arquivo.

### 4. Links de rodapé
Os perfis de Instagram, LinkedIn e Facebook estão com URLs presumidas a partir de `@bimedabrasil`.
Confirmar com a Bimeda.

### 5. Política de privacidade
O checkbox aponta para `bimeda.com.br`. Trocar pela URL real da política.

---

## Conteúdo — de onde veio cada dado

Tudo foi extraído do folheto `Linha_BR_CATALOG_DIGITAL_BR_MR26_0024.pdf` (8 páginas), incluindo:

- **Biprogest:** 63,4% de prenhez (156/246) vs. 59,6% do controle positivo (168/282), +3,8 p.p. — SBTE, 2026
- **eCG BR:** 6,3 folículos vs. 1,6 do controle (n=12 por grupo)
- **Curva de P4:** 1º, 2º e 3º uso, 0h a 192h após a inserção
- **Protocolos:** os quatro da página 7, com doses e dias conferidos um a um

Os gráficos foram **recriados em SVG** (não são imagens do PDF), para ficarem nítidos em qualquer
tela e animarem na entrada.

---

## Acessibilidade e performance

- Abas de protocolo com `role="tablist"`, navegação por setas, Home e End
- `prefers-reduced-motion` respeitado em todas as animações
- Texto do hero animado por CSS, sem depender de JS (protege o LCP)
- Imagens em WebP com fallback PNG/JPG; `loading="lazy"` fora do hero
- Vídeo com `preload="none"`
- Sem dependências externas além do Google Fonts (Inter + Barlow Condensed)

---

## Estrutura de arquivos

```
index.html
assets/
  css/style.css
  js/main.js
  img/            imagens otimizadas (WebP + fallback)
  video/          vídeo recomprimido para web
  docs/           folheto em PDF, servido no download
```
