# Mudança na contagem de views do YouTube — 24/ago/2026

**Documento de referência.** Toda análise de YouTube neste projeto feita antes de
24/ago/2026 usa uma régua de views diferente da que vale depois. Este doc registra
a mudança, a linha de corte congelada e como comparar sem se enganar.

## O que muda

A partir de **24/ago/2026** o YouTube conta uma view **no momento do play, sem
tempo mínimo de exibição**, para todos os formatos — vídeo longo e transmissão ao
vivo inclusive. A regra já valia para Shorts desde 2025; agora é padronizada.

Efeito prático: **o número de views sobe sem que nada tenha melhorado.** Não é
crescimento, é troca de régua.

## Onde cada métrica vive

| Métrica | Fonte | Régua |
|---|---|---|
| `statistics.viewCount` | YouTube Data API v3 | **NOVA** (conta no play) |
| `views` | YouTube Analytics API | **NOVA** |
| `engagedViews` (`engaged_views` em bulk) | YouTube Analytics API / Reporting | **ANTIGA** — "Visualizações Intencionais" |

A Data API pública **não expõe mais a régua antiga**. `engagedViews` exige ser dono
do canal ou ter autorização — o escopo `yt-analytics.readonly` do token já cobre.

**Regra de ouro:** para comparar com qualquer número anterior a 24/ago/2026, use
`engagedViews`. Usar `views` gera crescimento fantasma e derruba artificialmente o
custo por view das campanhas pagas.

## Linha de corte congelada — 18/ago/2026 (pré-cutover)

Snapshot de 116 vídeos salvo em `snapshot_youtube_2026-08-18.json` / `.csv`
(gerado por `scripts/snapshot_views.py` da skill `youtube-api`).

| | Valor |
|---|---|
| Inscritos | 1.490 |
| `viewCount` do canal (Data API) | 126.833 |
| Soma de `views` por vídeo (Analytics, vitalício) | 134.345 |
| Soma de `engagedViews` (vitalício) | **53.979** |
| Inflação views vs intencionais | **+149%** |

Ou seja: **só ~40% das views vitalícias do canal são intencionais.** Os outros 60%
já eram alcance raso — Shorts e tráfego pago, que já contavam na régua nova.

### Por formato (vitalício)

| Formato | views | engagedViews | infla |
|---|---|---|---|
| Shorts (≤3 min) | 56.343 | 8.619 | +554% |
| Longos (>3 min) | 77.357 | 44.764 | +73% |

O +73% dos longos **não** é a mudança de metodologia (ela ainda não entrou) — é
tráfego pago. Confirmação vídeo a vídeo: os campeões de gap são exatamente os
promovidos.

| Vídeo | views | intencionais | gap |
|---|---|---|---|
| Claude Code 24h na Nuvem (14min) | 31.068 | 7.359 | +322% |
| Agentes de IA gerenciando empresa (Short) | 29.959 | 517 | +5.695% |
| Porque aprender AWS (Short) | 13.652 | 305 | +4.376% |
| Automatizei meu Instagram com IA (28min) | 4.206 | 1.352 | +211% |
| Seu concorrente já usa IA no marketplace (44min) | 7.487 | 7.483 | **+0%** |
| Claude criou meu anúncio Shopee/ML (6min) | 3.402 | 3.400 | **+0%** |

Os dois de gap zero são os orgânicos — audiência real. É a prova mais limpa que já
tivemos de que o "31k" do Claude Code na nuvem vale ~7,4k de gente de verdade, e
que os Shorts pagos de AWS/Agentes são praticamente vazios.

### Por fonte de tráfego (28 dias, 21/jul → 18/ago/2026)

| Fonte | views | engagedViews | infla | min assistidos |
|---|---|---|---|---|
| Feed Shorts | 7.987 | 3.687 | +117% | 1.868 |
| Anúncios | 3.753 | 2.618 | +43% | 6.109 |
| **Pesquisa YouTube** | 2.729 | **2.595** | **+5%** | **11.785** |
| Inscritos | 1.330 | 1.306 | +2% | 6.866 |
| Externo | 1.064 | 1.055 | +1% | 2.803 |
| Sugeridos | 550 | 549 | +0% | 4.610 |
| **TOTAL** | **19.761** | **13.918** | **+42%** | — |

Confirma a tese central do plano de otimização: **a busca é a alavanca.** Pesquisa
YouTube tem 14% das views mas 28% do watch time e gap de apenas 5% — é a única
fonte em volume cujo número é quase todo real.

## O que fazer com isso

1. **Métrica-mãe do canal passa a ser `engagedViews`,** não views. Views servem só
   para prova social e alcance.
2. **Custo por view das campanhas precisa ser recalculado em engagedViews.** O
   R$0,04–0,08/view registrado em `analise-promocoes-youtube.md` está medido na régua
   que estava inflando só para Shorts/Ads; em views intencionais o custo real é bem
   mais alto. As campanhas de meta "Visualizações" ficam ainda menos defensáveis.
3. **Depois de 24/ago, esperar salto artificial nas views de vídeo longo e live** —
   especialmente nas fontes hoje com gap ~0% (busca, sugeridos, inscritos). Não
   comemorar, não usar em comparação mês a mês.
4. **Rodar `snapshot_views.py` periodicamente** para manter a série histórica em
   engagedViews, independente do que o Studio mostrar na tela.

## Ferramental

Skill `youtube-api` atualizada em 18/ago/2026:

- `scripts/snapshot_views.py` — congela views + engagedViews por vídeo (JSON + CSV).
- `scripts/stats.py` — canal/vídeo com as duas réguas lado a lado.
- `scripts/analytics.py` — relatório com views e intencionais, ⚠ nos vídeos que
  inflam mais de 2x, e aviso quando o período consultado atravessa 24/ago.

Token OAuth reautorizado em 18/ago/2026 com `yt-analytics.readonly` ativo
(`~/.hermes/credentials/youtube_token.pickle`).

Fonte: comunicado da Equipe do YouTube + documentação de métricas da YouTube
Analytics API (`engagedViews`: "número de vezes que os vídeos do canal foram
assistidos além dos segundos iniciais").
