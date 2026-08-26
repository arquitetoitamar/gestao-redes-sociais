# Auditoria SEO — meta: 1º lugar no Google para "IA para marketplaces"
**Coletado ao vivo em 14/ago/2026** · SERP pt-BR/Brasil · HTML servido, sitemaps e robots verificados diretamente nos servidores

---

## Veredito em uma frase

**Você não está perdendo a disputa — você não entrou nela.** O site que fala de marketplaces entrega ao Google uma página de **306 bytes sem nenhum texto**, enquanto o 1º colocado entrega **299.915 bytes com 31 mil caracteres de conteúdo**. Não é questão de palavra-chave. É que não há página para o Google ler.

---

## 1. O achado principal: o Google não vê o seu site

`marketplaces.tiops.com.br` é uma aplicação **100% renderizada no navegador (SPA sem SSR)**. Baixei o HTML cru direto do servidor, sem JavaScript, que é o que o robô do Google recebe primeiro:

| Medida | marketplaces.tiops.com.br | gobots.ai (1º lugar) |
|---|---|---|
| Bytes de `<body>` no HTML servido | **306** | **299.915** |
| Texto legível no HTML servido | **1 caractere** | **31.261 caracteres** |
| Tags `<h1>` no HTML servido | **0** | presente |
| Palavras na página renderizada | 902 (`/vendas`) | 3.315 |
| Tecnologia | SPA client-side | WordPress (renderizado no servidor) |

O Google até consegue executar JavaScript, mas isso acontece numa **segunda passada**, dias ou semanas depois, com orçamento limitado e sem garantia. Para uma palavra-chave comercial disputada, é uma desvantagem estrutural. Tudo o que o Google enxerga hoje do seu site de marketplaces é o `<title>` e a `<meta description>` — nada mais.

**Isso explica por que a página aparece no `site:` com a descrição certa, mas não ranqueia para nada competitivo.**

---

## 2. A página boa existe — e está escondida

`marketplaces.tiops.com.br/vendas` é uma página de verdade: **902 palavras**, H1 "Gerencie Shopee e Mercado Livre com IA" e uma estrutura correta de H2 — *Como o Marketplace Connect funciona · Assim fica a sua rotina · Tudo que você fazia manualmente, agora em segundos · Funcionalidades completas · Feito para quem vende de verdade · Perguntas frequentes*.

O problema é que ela está:

- **Invisível no HTML servido** (mesmo problema acima)
- **Fora do sitemap.xml** — o sitemap do subdomínio tem exatamente **2 URLs**: `/` e `/docs/api.html`. A sua melhor página comercial não está listada.

E `/planos` **não tem título próprio** — carrega o título genérico da home ("Tiops Marketplace Connect — API para IA integrar Mercado Livre, Shopee, Shein, Bling, Olist | MCP Server"). Como o título é trocado por JavaScript, algumas rotas atualizam e outras não.

---

## 3. O domínio forte está apontado para o mercado errado

`tiops.com.br` (a raiz, o domínio com mais autoridade) é o **único** que renderiza no servidor de verdade — 12.755 bytes de `<body>`, 4.865 caracteres de texto, H1 presente no HTML. O Google lê tudo.

Só que ele diz:

- **Title:** "TiOps Tecnologia | Cloud, IA Generativa & DevOps | Consultoria AWS, Azure, GCP"
- **H1:** "Transformamos sua infraestrutura com Cloud & IA"
- **Description:** "Consultoria especializada em Cloud Computing, IA Generativa, DevOps, FinOps e MLOps… AWS, Azure e GCP"

É o mesmo problema de legado que o canal do YouTube tinha até hoje de manhã: **o ativo mais forte está posicionado como consultoria de Cloud/DevOps, não como IA para e-commerce.** E o sitemap dele tem **1 URL**.

---

## 4. Cinco subdomínios dividindo a autoridade

Você tem `tiops.com.br`, `marketplaces.`, `gestorpro.`, `prompts.` e `docspace.` — cinco propriedades. O Google trata subdomínio praticamente como site separado, então em vez de uma autoridade somando, você tem cinco frações competindo entre si. A GoBots concentra tudo em um domínio só.

---

## 5. O tamanho real do concorrente

Puxei o sitemap da GoBots:

| | GoBots | TiOps (marketplaces) |
|---|---|---|
| Posts de blog | **350** | 0 |
| Páginas | **275** | ~5 |
| Categorias / tags | 33 / 317 | 0 |
| **Total no sitemap** | **975 URLs** | **2 URLs** |

O título da home deles é **exact match** para o termo que você quer: *"Plataforma de Atendimento em Marketplaces com IA | GoBots"*. E eles não ranqueiam só com a home — em "IA para Mercado Livre" e "IA para Shopee" quem aparece são **posts do blog** deles (`/blog/a-ferramenta-de-ia-que-responde...`, `/br-integracoes-shopee`).

É assim que se ganha um termo de cabeça: não com uma página, com um cluster.

---

## 6. Onde você está hoje nas buscas do seu nicho

| Busca | Posição da TiOps | Quem domina |
|---|---|---|
| **IA para marketplaces** | ausente do orgânico · **presente no carrossel de vídeos** ("YouTube · Itamar Rocha", 31/mai) | GoBots (2 entradas), Base.com, Loopia |
| **MCP mercado livre** | **página 1**, ~9ª posição | GitHub, Mercado Pago, LobeHub |
| **IA para Mercado Livre** | ausente | Mercado Livre oficial, MELI IA, GoBots (blog) |
| **IA para Shopee** | ausente | GoBots, MundoSeller, Shopee oficial |

Dois fatos úteis aqui:

1. **Você já ocupa espaço na página de "IA para marketplaces"** — pelo vídeo. Esse bloco fica acima de boa parte do orgânico. É o seu ativo mais barato de reforçar.
2. **"MCP mercado livre" é a sua fruta madura.** Você já está na primeira página competindo com GitHub e Mercado Pago, e é uma busca de altíssima intenção. Top 3 é questão de semanas, não de meses.

---

## 7. O que fazer, em ordem de impacto

### Fase 1 — Destravar (sem isso, nada mais funciona)

| # | Ação | Por quê |
|---|---|---|
| 1 | **Renderizar no servidor as páginas públicas** de `marketplaces.tiops.com.br` — `/`, `/vendas`, `/planos` e as futuras landing pages. Pré-renderização estática já resolve; não precisa migrar o app inteiro. | É o gargalo. Enquanto o HTML servido tiver 306 bytes, nenhuma outra otimização tem efeito. |
| 2 | **Corrigir o sitemap.xml** — incluir `/vendas`, `/planos` e todas as landing pages. Hoje tem 2 URLs. | O Google não sabe que suas melhores páginas existem. |
| 3 | **Dar título e description próprios a cada rota** (`/planos` está com o título da home). | Título duplicado faz o Google escolher uma página só e ignorar as outras. |
| 4 | **Google Search Console em todos os 5 subdomínios**, com sitemap enviado. | Sem isso você está otimizando às cegas. |

### Fase 2 — Entrar na disputa (2 a 6 semanas)

| # | Ação |
|---|---|
| 5 | **Criar `/ia-para-marketplaces`** com esse H1 exato — o texto está escrito na seção 8 abaixo. Hoje não existe alvo para o Google apontar. |
| 6 | **Otimizar a página que já está perto**: reforçar `/` e `/docs` para "MCP Mercado Livre", "conector MCP marketplace", "API MCP Mercado Livre". É onde você converte mais rápido. |
| 7 | **Reposicionar `tiops.com.br`** — trocar title, description e H1 de "Cloud, DevOps, AWS/Azure/GCP" para IA aplicada a e-commerce e varejo, e linkar dali para as landing pages dos produtos. É o domínio com mais autoridade e hoje ele não passa força nenhuma para o resto. |
| 8 | **Linkar os subdomínios entre si** de forma consistente (rodapé com links para todos os produtos, em todos eles). |

### Fase 3 — Construir o moat (3 a 12 meses)

| # | Ação |
|---|---|
| 9 | **Blog no domínio raiz**, em pasta (`tiops.com.br/blog/`), não em subdomínio novo. 2 posts por semana no cluster: "como conectar IA no Mercado Livre", "IA para responder perguntas na Shopee", "o que é MCP", "IA para Magalu", "automatizar estoque com IA". Foi assim que a GoBots chegou a 350 posts. |
| 10 | **Transformar cada vídeo do YouTube em post** — você já tem 85 vídeos. Transcrição editada + print da tela + link para o vídeo = 85 páginas de conteúdo real com quase zero custo marginal. |
| 11 | **Consolidar subdomínios em pastas** quando for viável (`tiops.com.br/marketplaces`, `/gestorpro`), com redirecionamento 301. É a mudança de maior impacto de longo prazo e a mais trabalhosa. |
| 12 | **Backlinks**: E-Commerce Brasil, Ecommerce na Prática, podcasts do setor, e o programa de parceiros do Mercado Livre/Bling/Olist. A GoBots tem anos disso. |

### Expectativa honesta

Ninguém garante 1º lugar, e quem garante está vendendo. O que dá pra dizer com base nos números acima:

- **"MCP mercado livre" no top 3**: realista em 4 a 8 semanas, depois da Fase 1.
- **"IA para marketplaces" na primeira página**: realista em 4 a 8 meses, com as três fases andando.
- **1º lugar orgânico nesse termo**: possível, mas exige vencer um concorrente com 975 páginas indexadas e anos de vantagem. É meta de 12 a 18 meses.
- **Aparecer na página 1 desse termo já na semana que vem**: possível pelo **carrossel de vídeos**, onde você já está. É o caminho mais curto e o mais subestimado.

---

## 8. A página nova — texto pronto

**URL:** `https://marketplaces.tiops.com.br/ia-para-marketplaces`
*(ideal: `tiops.com.br/ia-para-marketplaces`, se a consolidação de domínios acontecer)*

**Title (61 caracteres):**
```
IA para Marketplaces — Mercado Livre, Shopee e Magalu | TiOps
```

**Meta description:**
```
Conecte IA (Claude, ChatGPT ou Codex) direto ao Mercado Livre, Shopee, Magalu, Amazon, Shein, Bling e Olist. Anúncios, preço, estoque e atendimento em segundos. Ative em 5 minutos.
```

**H1:**
```
IA para marketplaces: seu agente operando Mercado Livre, Shopee e Magalu
```

**Abertura (primeiro parágrafo — o Google pesa muito os primeiros 150 caracteres):**

> IA para marketplaces não é gerar título com prompt. É o seu agente de IA conectado por API aos marketplaces onde você vende — lendo pedidos, corrigindo preço, ajustando estoque e respondendo cliente na sua conta real, em segundos. O Marketplace Connect faz essa ponte para Mercado Livre, Shopee, Magalu, Amazon, Shein, Bling e Olist, e ativa em 5 minutos.

**Estrutura de H2 (nessa ordem):**

1. `O que é IA para marketplaces` — define o termo. É o que faz o Google entender que a página é *sobre* isso.
2. `Prompt não é integração: a diferença que muda o resultado` — seu diferencial real contra ferramenta de texto.
3. `O que a IA faz na sua operação` — subseções em H3: **Anúncios** (criar, editar, pausar, clonar) · **Preço e estoque** (multiconta, em tempo real) · **Atendimento** (perguntas e mensagens) · **Ads** (ROAS diário) · **Financeiro** (repasses, notas, margem)
4. `Marketplaces e ERPs suportados` — Mercado Livre, Shopee, Magalu, Amazon, Shein, Bling, Olist. Um H3 por plataforma, com um parágrafo cada. **É isso que faz você ranquear também para "IA para Shopee", "IA para Magalu" etc.**
5. `Como funciona o MCP` — explica o protocolo. Você já está na página 1 desse termo; essa seção reforça.
6. `Como ativar em 5 minutos` — passo a passo numerado.
7. `Quanto custa` — link para /planos.
8. `Perguntas frequentes` — com schema FAQPage.

**FAQ (as perguntas vieram do "As pessoas também perguntam" do Google — usar o texto delas aumenta a chance de aparecer nesse bloco):**

- O que é IA para marketplaces?
- Qual a melhor IA para vendas?
- Precisa saber programar para usar?
- Funciona com mais de uma conta no mesmo marketplace?
- A IA acessa meus dados reais ou só sugere texto?
- Funciona com Claude, ChatGPT e Codex?
- Quanto tempo leva para integrar?
- É seguro dar acesso das minhas contas para uma IA?

**Schema a incluir na página:** `SoftwareApplication` (já existe na home — reaproveitar), `FAQPage`, `BreadcrumbList` e `Organization`.

**Elementos que a GoBots tem e você não — e que pesam:**

- **Case com nome e número** (eles usam a Britânia). Um cliente real com resultado medido vale mais que dez parágrafos.
- **Bloco de resultados quantificados** ("clientes obtêm resultados como…").
- **Vídeo embutido na página** — e aqui você tem vantagem: tem 85 vídeos e já aparece no carrossel do Google. Embutir o vídeo certo nessa página conecta os dois ativos.

---

## 9. Checklist técnico rápido

| Item | Status hoje |
|---|---|
| `robots.txt` em marketplaces | ✅ correto (Allow /, bloqueia /api/ e /auth/, aponta sitemap) |
| `sitemap.xml` em marketplaces | ⚠️ só 2 URLs — faltam /vendas, /planos e as futuras |
| `sitemap.xml` em tiops.com.br | ⚠️ 1 URL |
| `canonical` | ✅ presente e correto nas páginas checadas |
| `lang="pt-BR"` | ✅ |
| `meta robots` | ✅ index, follow, max-image-preview:large |
| Schema JSON-LD | ✅ SoftwareApplication na home — falta FAQPage e Breadcrumb |
| Renderização no servidor | ❌ **ausente em marketplaces, gestorpro e prompts** |
| Título único por rota | ❌ /planos usa o título da home |
| H1 no HTML servido | ❌ zero |

---

### Nota sobre o método
Todos os números vieram de verificação direta: HTML cru baixado dos servidores sem execução de JavaScript (para reproduzir o que o robô do Google recebe), `robots.txt` e `sitemap.xml` lidos nos endereços reais, e as SERPs consultadas no Google pt-BR com localidade Brasil em 14/ago/2026. Posições de busca variam por localização e histórico — trate os números como ordem de grandeza, não como medida exata.
