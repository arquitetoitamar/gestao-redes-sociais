# Gestão de Redes Sociais — TiOps / @tiopstecnologia

Documentação de estratégia, análise e operação dos canais **YouTube**, **Instagram**
e do **SEO** dos sites da TiOps. Exportado do projeto Claude *"Gestão Redes Sociais"*
em 26/ago/2026.

---

## Índice

### 📺 YouTube — `docs/youtube/`

| Documento | O que é | Data dos dados |
|---|---|---|
| [`mudanca-metricas-views-youtube-2026.md`](docs/youtube/mudanca-metricas-views-youtube-2026.md) | **Leia primeiro.** A régua de views mudou em 24/ago/2026. Define `engagedViews` como métrica-mãe e congela a linha de corte pré-cutover. | 18/ago/2026 |
| [`plano-otimizacao-youtube.md`](docs/youtube/plano-otimizacao-youtube.md) | Diagnóstico do canal, persona, fontes de tráfego, palavras-chave de busca e plano de SEO on-page + pauta. | 11 e 18/ago/2026 |
| [`analise-promocoes-youtube.md`](docs/youtube/analise-promocoes-youtube.md) | As 20 promoções pagas (≈R$964): o que gerou inscrito, o que só comprou view rasa. | 11 e 18/ago/2026 |

### 📱 Instagram — `docs/instagram/`

| Documento | O que é | Data dos dados |
|---|---|---|
| [`analise-instagram-vs-youtube.md`](docs/instagram/analise-instagram-vs-youtube.md) | Diagnóstico comparado dos dois canais, posicionamento, papel de cada um, plano de 7 dias + 4 semanas e status de execução. | 14/ago/2026 |

### 💼 LinkedIn — `docs/linkedin/`

| Documento | O que é | Data dos dados |
|---|---|---|
| _(ainda sem documentos)_ | — | — |

### 🔍 SEO — `docs/seo/`

| Documento | O que é | Data dos dados |
|---|---|---|
| [`auditoria-seo-ia-para-marketplaces.md`](docs/seo/auditoria-seo-ia-para-marketplaces.md) | Auditoria completa: por que o Google não vê o site, tamanho do concorrente (GoBots), posições atuais e roadmap em 3 fases. Inclui o texto pronto da página nova. | 14/ago/2026 |
| [`SPEC-SEO-001-marketplaces-tiops.md`](docs/seo/SPEC-SEO-001-marketplaces-tiops.md) | Spec de implementação para o agente de desenvolvimento: SPEC-01 a SPEC-08, com critérios de aceite verificáveis por `curl`. | 14/ago/2026 |

### ⚙️ Operação e agentes — `docs/operacao/`

| Documento | O que é |
|---|---|
| [`agente-cortes-pipeline.md`](docs/operacao/agente-cortes-pipeline.md) | O agente autônomo que publica Shorts no YouTube e Reels no Instagram: workflow, comandos, estrutura do `clipes_status.json`, calendário e pitfalls. |
| [`skill-youtube-api.md`](docs/operacao/skill-youtube-api.md) | A skill `youtube-api`: scripts de snapshot, stats e analytics; credenciais e escopos. |

---

## As 3 conclusões que atravessam tudo

1. **O crescimento dos dois canais é majoritariamente pago e raso.** ~1.274 dos
   1.384 inscritos do YouTube vieram de anúncio; os Reels de 5–12 mil views têm
   0–6 likes. Só ~40% das views vitalícias do canal são intencionais.
2. **A busca é a única alavanca orgânica real.** Pesquisa do YouTube tem 14% das
   views mas 28% do watch time, CTR 14,5% e gap de apenas 5% entre views e
   intencionais. O cluster é `claude + [mercado livre | marketplace | shopee | ecommerce]`.
3. **O site não está na disputa de SEO — ele não entrou nela.** O HTML servido de
   `marketplaces.tiops.com.br` tem 306 bytes e nenhum `<h1>`. Enquanto isso não
   mudar, nenhuma outra otimização produz efeito.

---

## ⚠️ Segurança

O documento original do agente de publicação continha um **token de API em texto
plano**. Nesta versão ele foi substituído por `${CHATIOPS_TOKEN}` e os demais
segredos por placeholders — ver [`.env.example`](.env.example).

**Antes de dar `git push`:**

- Confirme que o `.env` real nunca foi commitado (`git log --all -- .env`).
- Se o token do Chatiops já circulou em algum repositório ou doc compartilhado,
  **rotacione-o** — ele dá acesso de envio de WhatsApp pela API.

---

## Convenções

- Todo documento carrega a **data de coleta** dos dados no cabeçalho. Análise de
  rede social envelhece rápido — número sem data não vale nada.
- Comparação de views só é válida em `engagedViews` quando cruza 24/ago/2026.
- Documento novo entra na pasta do canal correspondente e é adicionado a este índice.
