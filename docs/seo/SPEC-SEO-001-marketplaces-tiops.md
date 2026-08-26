# SPEC-SEO-001 — Tornar o site indexável e disputar "IA para marketplaces"

**Para:** agente de desenvolvimento
**Solicitante:** Itamar Rocha · TiOps
**Data:** 14/ago/2026
**Documento de origem:** `docs/seo/auditoria-seo-ia-para-marketplaces.md`

---

## 0. Contexto em um parágrafo

`marketplaces.tiops.com.br` é um SPA React/Vite renderizado 100% no cliente. O HTML servido tem **306 bytes de `<body>`**, contendo apenas `<noscript>`, um `<iframe>` e `<div id="root">`. Nenhum `<h1>`, nenhum texto. O robô do Google recebe uma página vazia. O concorrente que ocupa o 1º lugar entrega 299.915 bytes com 31.261 caracteres de texto no HTML servido. **Enquanto isso não mudar, nenhuma outra otimização de SEO produz efeito.**

## 1. Stack detectada

| Item | Valor observado |
|---|---|
| Build | Vite (`<script type="module" src="/assets/index-[hash].js">`) |
| Framework | React (`<div id="root">`) |
| Renderização | Client-side only, sem SSR/SSG |
| `index.html` servido | ~6.250 bytes totais, `<body>` com 306 bytes |
| robots.txt | presente e correto |
| sitemap.xml | presente, **2 URLs** |
| canonical | presente e correto |

> Se a stack real divergir do observado, ajustar a implementação mantendo os **critérios de aceite** da seção 10 — eles são a definição de pronto, não a técnica.

## 2. Objetivo mensurável

Ao final desta spec, para toda rota pública:

```bash
curl -s https://marketplaces.tiops.com.br/vendas | grep -c "<h1"
# deve retornar >= 1
```

Hoje retorna `0`.

## 3. Escopo

**Dentro:** rotas públicas de marketing de `marketplaces.tiops.com.br` — `/`, `/vendas`, `/planos`, `/termos`, `/privacidade`, `/docs/api.html` e a nova `/ia-para-marketplaces`. Metadados, sitemap, JSON-LD. Ajuste de textos em `tiops.com.br`.

**Fora:** a área logada (`/app`, `/auth`, `/api`, dashboard de integrações). Ela continua SPA puro e **deve permanecer `noindex`**. Não migrar o app inteiro para SSR.

---

## SPEC-01 — Pré-renderizar as rotas públicas
**Prioridade: P0. Bloqueia todo o resto.**

Gerar HTML estático completo, em tempo de build, para cada rota pública listada no escopo. A hidratação do React continua normalmente depois do carregamento.

**Abordagem sugerida** (escolher uma, na ordem de preferência):

1. `vite-react-ssg` — integra com Vite, gera um `.html` por rota, exige React Router com rotas declarativas.
2. `vite-plugin-prerender` / `puppeteer-prerender-plugin` — roda um headless no build e salva o DOM renderizado. Menos invasivo, não exige refatorar o roteamento.
3. Extrair as páginas de marketing para um projeto estático separado (Astro ou similar) servido no mesmo domínio, mantendo o app React em `/app`. Maior esforço, melhor resultado a longo prazo.

**Requisitos:**

- O HTML servido de cada rota pública deve conter o texto visível completo — headings, parágrafos, listas, FAQ.
- Não usar `<noscript>` como substituto de conteúdo.
- A hidratação não pode causar mudança visual perceptível (evitar flash de conteúdo).
- A área logada continua sendo servida como SPA.

**Critério de aceite:**
```bash
for p in / /vendas /planos /ia-para-marketplaces; do
  echo -n "$p → "
  curl -s "https://marketplaces.tiops.com.br$p" \
    | sed 's/<script[^>]*>.*<\/script>//g' \
    | sed 's/<[^>]*>/ /g' | tr -s ' ' | wc -c
done
# cada rota deve retornar > 3000 caracteres de texto (hoje: 1)
```

---

## SPEC-02 — Metadados únicos por rota, no HTML servido
**Prioridade: P0**

Hoje `/planos` carrega o `<title>` da home. Os metadados são trocados por JavaScript, então algumas rotas atualizam e outras não — e o Google pode nunca ver a troca.

Cada rota pública precisa ter, **no HTML servido** (não injetado por JS):

- `<title>` único, 50–60 caracteres
- `<meta name="description">` única, 140–160 caracteres
- `<link rel="canonical">` absoluto e autorreferente
- `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
- `twitter:card = summary_large_image`

**Valores a aplicar:**

| Rota | Title | Description |
|---|---|---|
| `/` | Marketplace Connect — API MCP para IA nos Marketplaces \| TiOps | API MCP que conecta Claude, ChatGPT e Codex a Mercado Livre, Shopee, Magalu, Amazon, Shein, Bling e Olist. 260+ ações. Ative em 5 minutos. |
| `/vendas` | Gerencie Shopee e Mercado Livre com IA \| TiOps | Crie, edite e pause anúncios, atualize preço e estoque e responda clientes com IA no Mercado Livre e na Shopee. Sem planilha, sem copiar e colar. |
| `/planos` | Planos e Preços — Marketplace Connect \| TiOps | Conecte Mercado Livre, Shopee, Magalu, Amazon, Shein, Bling e Olist. Planos por número de contas conectadas e volume de uso. |
| `/ia-para-marketplaces` | IA para Marketplaces — Mercado Livre, Shopee e Magalu \| TiOps | Conecte IA (Claude, ChatGPT ou Codex) direto ao Mercado Livre, Shopee, Magalu, Amazon, Shein, Bling e Olist. Anúncios, preço, estoque e atendimento em segundos. |

**Critério de aceite:** `curl -s <url> | grep -o '<title>[^<]*</title>'` retorna o título correto e distinto para cada rota.

---

## SPEC-03 — Sitemap completo e automático
**Prioridade: P0**

O `sitemap.xml` atual lista 2 URLs (`/` e `/docs/api.html`) e **não inclui `/vendas`**, que é a melhor página comercial do site.

**Requisitos:**

- Gerar o sitemap no build, a partir da mesma lista de rotas usada pela pré-renderização — nunca manter à mão.
- Incluir todas as rotas públicas, com `<lastmod>` real.
- Excluir rotas autenticadas e `/api/`.
- Manter `Sitemap:` no `robots.txt` (já está correto).
- Fazer o mesmo em `tiops.com.br`, cujo sitemap hoje tem **1 URL**.

**Critério de aceite:** `curl -s https://marketplaces.tiops.com.br/sitemap.xml | grep -c "<loc>"` retorna ≥ 6, e a saída contém `/vendas`, `/planos` e `/ia-para-marketplaces`.

---

## SPEC-04 — Criar a rota `/ia-para-marketplaces`
**Prioridade: P1** (depende de SPEC-01)

Página nova de conteúdo, pré-renderizada, com esta estrutura semântica exata:

```
H1  IA para marketplaces: seu agente operando Mercado Livre, Shopee e Magalu
    [parágrafo de abertura — ver copy abaixo]
H2  O que é IA para marketplaces
H2  Prompt não é integração: a diferença que muda o resultado
H2  O que a IA faz na sua operação
    H3  Anúncios
    H3  Preço e estoque
    H3  Atendimento
    H3  Ads
    H3  Financeiro
H2  Marketplaces e ERPs suportados
    H3  Mercado Livre
    H3  Shopee
    H3  Magalu
    H3  Amazon
    H3  Shein
    H3  Bling
    H3  Olist
H2  Como funciona o MCP
H2  Como ativar em 5 minutos
H2  Quanto custa
H2  Perguntas frequentes
```

**Parágrafo de abertura (usar literalmente — os primeiros 150 caracteres pesam muito):**

> IA para marketplaces não é gerar título com prompt. É o seu agente de IA conectado por API aos marketplaces onde você vende — lendo pedidos, corrigindo preço, ajustando estoque e respondendo cliente na sua conta real, em segundos. O Marketplace Connect faz essa ponte para Mercado Livre, Shopee, Magalu, Amazon, Shein, Bling e Olist, e ativa em 5 minutos.

**Regras de conteúdo:**

- Um H3 por marketplace, com pelo menos um parágrafo próprio cada. É isso que faz a página ranquear também para "IA para Shopee", "IA para Magalu" etc.
- Mínimo de 1.200 palavras de texto real. A página do concorrente tem 3.315.
- Embutir um vídeo do canal do YouTube (`@tiopstecnologia`) na seção "Como ativar em 5 minutos".
- Links internos para `/vendas`, `/planos` e `/docs/api.html`.

**FAQ — usar estas perguntas literalmente** (foram extraídas do bloco "As pessoas também perguntam" do Google, o que aumenta a chance de a página aparecer ali):

1. O que é IA para marketplaces?
2. Qual a melhor IA para vendas?
3. Precisa saber programar para usar?
4. Funciona com mais de uma conta no mesmo marketplace?
5. A IA acessa meus dados reais ou só sugere texto?
6. Funciona com Claude, ChatGPT e Codex?
7. Quanto tempo leva para integrar?
8. É seguro dar acesso das minhas contas para uma IA?

---

## SPEC-05 — Dados estruturados (JSON-LD)
**Prioridade: P1**

Já existe `SoftwareApplication` na home. Adicionar, **no HTML servido**:

| Tipo | Onde |
|---|---|
| `FAQPage` | `/ia-para-marketplaces` e `/vendas` (ambas têm FAQ) |
| `BreadcrumbList` | todas as rotas públicas exceto a home |
| `Organization` | home, com `name`, `url`, `logo`, `sameAs` (YouTube, Instagram, LinkedIn) |
| `Product` ou `Offer` | `/planos` |

**Critério de aceite:** todas as URLs passam sem erro no Rich Results Test do Google e no validador do schema.org.

---

## SPEC-06 — Reposicionar `tiops.com.br`
**Prioridade: P1** — mudança de texto, sem impacto técnico

O domínio raiz é o único que já renderiza no servidor corretamente (12.755 bytes de `<body>`), ou seja, é o de maior autoridade — e está posicionado como consultoria de Cloud/DevOps, não como IA para e-commerce.

**Trocar:**

| Campo | De | Para |
|---|---|---|
| `<title>` | TiOps Tecnologia \| Cloud, IA Generativa & DevOps \| Consultoria AWS, Azure, GCP | TiOps — IA aplicada a e-commerce, varejo e negócios |
| `<h1>` | Transformamos sua infraestrutura com Cloud & IA | IA aplicada a e-commerce, varejo e negócios |
| `meta description` | Consultoria especializada em Cloud Computing, IA Generativa, DevOps, FinOps e MLOps… AWS, Azure e GCP | IA conectada à sua operação: Mercado Livre, Shopee, Magalu, Amazon, Bling e Olist. Marketplace Connect, GestorPro e integrações complexas. |

Manter a seção de Cloud/DevOps na página — o serviço existe — mas **abaixo**, como uma das ofertas, não como o posicionamento principal.

---

## SPEC-07 — Interlinking entre os subdomínios
**Prioridade: P2**

Há cinco propriedades separadas (`tiops`, `marketplaces`, `gestorpro`, `prompts`, `docspace`) e a autoridade está fragmentada.

Adicionar um **rodapé padronizado em todos os cinco**, com links para os produtos e para as páginas-chave, usando texto âncora descritivo — "IA para marketplaces", "Marketplace Connect", "GestorPro", "prompts de IA para Mercado Livre" — nunca "clique aqui" ou "saiba mais".

---

## SPEC-08 — Search Console
**Prioridade: P2**

Registrar e verificar as 5 propriedades no Google Search Console, enviar o sitemap de cada uma e habilitar relatórios de cobertura. Sem isso não há como medir o efeito de nada nesta spec.

---

## 9. Guardrails — o que NÃO fazer

- **Não** colocar `noindex` em rota pública por engano ao configurar a pré-renderização.
- **Não** indexar `/app`, `/auth`, `/api` nem qualquer rota autenticada.
- **Não** trocar URLs de páginas já indexadas (`/vendas`, `/planos`) — se for inevitável, usar redirect **301**, nunca 302.
- **Não** criar um subdomínio novo para o blog. Se houver blog, é em pasta: `tiops.com.br/blog/`.
- **Não** usar texto escondido, keyword stuffing ou conteúdo gerado sem revisão. O ganho é temporário e o risco de penalidade é real.
- **Não** remover o JSON-LD `SoftwareApplication` que já existe.

---

## 10. Definição de pronto

A spec está concluída quando **todos** os comandos abaixo passam:

```bash
BASE=https://marketplaces.tiops.com.br

# 1. HTML servido tem H1 em toda rota pública
for p in / /vendas /planos /ia-para-marketplaces; do
  n=$(curl -s "$BASE$p" | grep -c "<h1")
  echo "$p h1=$n"; [ "$n" -ge 1 ] || echo "FALHOU"
done

# 2. Conteúdo real no HTML servido (> 3000 chars de texto)
for p in / /vendas /planos /ia-para-marketplaces; do
  c=$(curl -s "$BASE$p" | sed 's/<script[^>]*>.*<\/script>//g' | sed 's/<[^>]*>/ /g' | tr -s ' ' | wc -c)
  echo "$p chars=$c"; [ "$c" -gt 3000 ] || echo "FALHOU"
done

# 3. Títulos únicos
for p in / /vendas /planos /ia-para-marketplaces; do
  curl -s "$BASE$p" | grep -o '<title>[^<]*</title>'
done | sort | uniq -d
# saída vazia = nenhum título duplicado

# 4. Sitemap completo
curl -s "$BASE/sitemap.xml" | grep -c "<loc>"          # >= 6
curl -s "$BASE/sitemap.xml" | grep -q "/vendas" && echo OK

# 5. Rotas privadas fora do índice
curl -s "$BASE/app" | grep -o 'name="robots"[^>]*'      # deve conter noindex
```

E, no Google Rich Results Test: `/ia-para-marketplaces` e `/vendas` retornam `FAQPage` válido.

---

## 11. Ordem de execução sugerida

```
SPEC-01 (pré-renderização)  ──┬──▶ SPEC-02 (metadados)
                              ├──▶ SPEC-03 (sitemap)
                              └──▶ SPEC-04 (página nova) ──▶ SPEC-05 (JSON-LD)

SPEC-06 (textos do tiops.com.br)   ← independente, pode ir em paralelo
SPEC-07 (rodapé)                   ← depois que a página nova existir
SPEC-08 (Search Console)           ← independente, fazer já
```

SPEC-06 e SPEC-08 não dependem de nada e podem ser feitas hoje.
