# Plano de Otimização — YouTube Itamar Rocha
**Coletado do YouTube Studio em 11/ago/2026** · Canal UC4mEWT48J1erkqlbHqfHpEg · Nicho: IA, Marketplace, Conector MCP, Claude Code

> ⚠️ **Quebra de metodologia — views a partir de 24/ago/2026.** Os números de
> *view* deste documento estão na régua antiga. Desde 24/ago o YouTube conta view
> no play, sem tempo mínimo de exibição, em todos os formatos — as views vão subir
> sozinhas. Para comparar com este doc, use `engagedViews` ("Visualizações
> Intencionais"). Linha de corte congelada e tabelas comparativas em
> `docs/youtube/mudanca-metricas-views-youtube-2026.md`.

## Números-chave
- 1.384 inscritos, **+378 em 28 dias (+88%)** — canal em aceleração.
- 16,4 mil views / 659 h de exibição (28d). Público mensal 6,7 mil.
- 27 vídeos longos, 60 itens no total (com Shorts).
- *Atualização 18/ago:* 1.490 inscritos; 116 itens no total. Em 28 dias: 19,8 mil
  views mas **13,9 mil intencionais** (+42% de inflação). Vitalício: 134,3 mil
  views contra **54,0 mil intencionais** — só ~40% da audiência do canal é real.

## Público (persona-alvo)
- Gênero: **92,9% masculino**. Idade: 25–44 = **72,8%** (35–44: 36,8%; 25–34: 36%; 45–54: 15,9%).
- Local: **Brasil 82%**. Dispositivo: **Desktop 48,7%**, celular 34%, TV 16%.
- **Persona:** homem 25–44, brasileiro, vendedor de marketplace / empreendedor de e-commerce / maker, assiste no computador buscando implementar algo.
- **Ponto fraco:** 90,1% novos espectadores, recorrentes <0,1%, 79,4% do watch time de não-inscritos, sino só 8% (média 10–30%). Ótimo em atrair, fraco em reter.

## Fontes de tráfego (28d) — a busca é a alavanca
- Feed Shorts: 38,2% views mas só 4% do watch time (alcance raso).
- **Pesquisa YouTube: 16,5% views / 29,4% do watch time / retenção 4:27 / CTR 14,5%** ← forte e escalável.
- Ads 13,4%; Navegação/sugeridos 7,6% (17,3% watch); Externa 6,4%.

**Confirmação por `engagedViews` (28d até 18/ago)** — quanto de cada fonte é real:

| Fonte | views | intencionais | infla |
|---|---|---|---|
| Feed Shorts | 7.987 | 3.687 | +117% |
| Anúncios | 3.753 | 2.618 | +43% |
| **Pesquisa YouTube** | 2.729 | **2.595** | **+5%** |
| Inscritos | 1.330 | 1.306 | +2% |
| Sugeridos | 550 | 549 | +0% |

A busca é a única fonte em volume cujo número é quase todo gente de verdade. Reforça
a prioridade de SEO abaixo.

## Palavras-chave reais de busca (365d, total 6.655 views, CTR 16,4%)
Padrão: **"claude" + [mercado livre / marketplace / shopee / ecommerce / whatsapp / code / mcp / api]**.
- claude mercado livre (184, 6:07) · claude marketplace (79, 8:13) · claude shopee (25) · claude ecommerce (24, 8:43) · claude e commerce (20, 9:57) · claude para ecommerce (14) · claude whatsapp (12) · claude code (10, 5:31) · api mercado livre (8) · **mcp mercado livre (8)** · claude code ecommerce (6, **18:44**) · claude no mercado livre (5, 10:27).

### 6 clusters
1. Claude + Mercado Livre (forte) 2. Claude + Marketplace/Shopee (forte) 3. Claude + E-commerce (maior retenção) 4. Claude Code 5. **Conector MCP (tendência 2026, aberto)** 6. IA + Atendimento/WhatsApp.

## Conteúdo — o que converte
- Maior gerador de inscritos: **"Seu concorrente já usa IA no marketplace" (44min) = 63 dos 378 inscritos + 33% do watch time.** Em intencionais: 7.483 de 7.487 views — audiência 100% real, o vídeo mais limpo do canal.
- Vídeo longo demonstrativo converte inscrito; Short gera view mas quase nenhum inscrito.
- **"Claude Code na nuvem" (31k) teve views de PROMOÇÃO PAGA (Ads), não orgânicas** — não usar como prova de demanda orgânica. Maior orgânico real: ~7,2k. *Confirmado em intencionais: 7.359 contra 31.068 de fachada (+322%).*

## Problemas de SEO (quick wins)
Vídeos de 3k+ views **SEM descrição/tags**: Automatizei Instagram com IA (4.202), Claude criou anúncio Shopee/ML (3.348), Skill Claude WhatsApp (3.087). Também: keyword nem sempre no início do título; erros de digitação ("Markeplace"); sem playlists por cluster; poucos capítulos.

## Plano de ação
**A. SEO on-page (semana 1):** preencher descrição (keyword nas 2 primeiras linhas) + 10–15 tags do cluster + capítulos + playlists + comentário fixado + tela final. Reescrever títulos com keyword no começo + promessa de resultado.
**B. Pauta (4–6 semanas):** "O que é MCP e como conectar no Mercado Livre", série "Claude Code na Nuvem" (testar 1 antes), "Claude no e-commerce: 5 automações", "Responder clientes ML/Shopee com IA", "Claude vs ChatGPT para marketplace".
**C. Crescimento:** Shorts como isca apontando para longos; séries numeradas; playlists por cluster; CTA de inscrição após o 1º "uau"; 1 longo mão-na-massa/semana + 2–3 Shorts.

### Fazer já (3 coisas):
1. Preencher descrição+tags dos vídeos de 3k+ views vazios.
2. Criar 4 playlists (Mercado Livre, Marketplace/Shopee, Claude Code, MCP).
3. Publicar "O que é MCP e como conectar no Mercado Livre" para ocupar o termo cedo.

## Nota técnica
~~Token OAuth da API do YouTube (projeto gen-lang-client-0236201276) expirado e sem escopo Analytics~~ — **resolvido em 18/ago/2026.** Token reautorizado com
`youtube.upload`, `youtube.readonly` e `yt-analytics.readonly`, salvo em
`~/.hermes/credentials/youtube_token.pickle`. Relatórios automáticos já rodam pela
API (skill `youtube-api`): `stats.py`, `analytics.py` e `snapshot_views.py`, todos
com views e `engagedViews` lado a lado.
