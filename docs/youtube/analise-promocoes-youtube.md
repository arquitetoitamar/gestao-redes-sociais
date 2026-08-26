# Análise das Promoções Pagas — YouTube Itamar Rocha
**Coletado do Studio em 11/ago/2026** · 20 promoções · Gasto total ≈ R$ 964

> ⚠️ **Quebra de metodologia — views a partir de 24/ago/2026.** Todos os números
> de *view* deste documento estão na régua antiga (com tempo mínimo de exibição
> para vídeo longo). Desde 24/ago o YouTube conta view no play, sem tempo mínimo,
> em todos os formatos: os custos por view abaixo **não são comparáveis** com
> nada coletado depois dessa data. Para comparar, use `engagedViews`
> ("Visualizações Intencionais"). Detalhes e linha de corte congelada em
> `docs/youtube/mudanca-metricas-views-youtube-2026.md`.
>
> Correção adicional já medida (18/ago): as views compradas eram ainda mais rasas
> do que este doc registrou. Em `engagedViews`, o Short "Porque aprender AWS" tem
> **305 views intencionais** contra 13.652 de fachada, e "Claude Code 24h na
> nuvem" tem **7.359** contra 31.068. O custo por view real das campanhas de
> "Visualizações" é múltiplos do R$0,04–0,08 registrado aqui.

## Descoberta central
Das ~1.384 inscrições do canal, **~1.274 são atribuídas a promoções pagas**. O crescimento é fortemente pago, não orgânico. E **675 dessas (53%) vieram de UMA promoção fora do nicho**: um Short "Porque aprender AWS…" (R$99,73 → 675 inscritos). Isso explica o problema de retenção visto na análise de público (recorrentes <0,1%, sino 8%, 79% do watch time de não-inscritos): boa parte do público foi comprada e parte é off-nicho (carreira AWS, não marketplace/Claude/MCP).

## Campanhas de INSCRITOS (meta "Crescimento do público") — o que deu resultado
| Vídeo promovido | Custo | Inscritos | Custo/inscrito | Nicho |
|---|---|---|---|---|
| Porque aprender AWS (Short) | R$99,73 | 675 | **R$0,15** | ❌ fora do nicho |
| Claude criou meu anúncio Shopee (29/jul) | R$49,54 | 145 | R$0,34 | ✅ |
| Claude criou meu anúncio Shopee (1/mai) | R$49,92 | 126 | R$0,40 | ✅ |
| Claude criou meu anúncio Shopee (17/mai) | R$49,68 | 121 | R$0,41 | ✅ |
| Claude Code 24h na nuvem (12/mai) | R$29,89 | 100 | R$0,30 | ✅ |
| Podcast "IA: substituído ou potencializado" | R$25,86 | 83 | R$0,31 | ✅ |
| Skill Claude envia WhatsApp | R$50,00 | 17 | R$2,94 | ⚠️ caro |

**Campeão on-nicho:** "Claude criou meu anúncio na Shopee" — rodado 3x, ~392 inscritos a ~R$0,38 cada. É a criativo de aquisição mais confiável. "Claude Code 24h" e o "Podcast" também convertem a ~R$0,30.

*(Custo por inscrito não é afetado pela mudança de views — inscrito é inscrito.
Estas linhas seguem válidas.)*

## Campanhas de VIEWS (meta "Visualizações") — inflam view, ~0 inscrito
Custo/view ~R$0,04–0,08 **na régua antiga**; inscritos ≈ 0 em quase todas. Ex.: ChatGPT ML/Shopee R$49,99→1.235 views (R$0,04); Bling ERP R$50→1.008; Responder clientes ML R$50→1.052. **Compram audiência rasa** — não constroem canal.

Medido em `engagedViews` (18/ago), o quadro fica pior: no acumulado do canal, as
views de anúncio inflam +43% sobre as intencionais, e os Shorts promovidos
chegam a inflar mais de 40x. O custo por espectador real dessas campanhas é
ordens de grandeza acima do que a métrica de fachada sugeria.

## Campanhas de SITE (meta "Visitas ao site") — medir off-YouTube
- Claude Code 24h: **R$199,43 → 3.155 visitas ao site** + 7.132 views (maior gasto único).
- Agentes gerenciando empresa (Short): R$49,88 → 804 visitas.
- Automatizei Instagram: R$49,71 → 621 visitas.
ROI real depende da conversão em marketplaces.tiops.com.br / gestorpro (checar no GA4 — existe token ga4).

## Recomendações
1. **Parar de impulsionar conteúdo fora do nicho (AWS) para inscritos** — infla número mas polui o público e derruba retenção/sino.
2. **Dobrar nas campanhas de "Crescimento do público" com vídeos on-nicho comprovados**: "Claude anúncio Shopee/ML", "Claude Code", "Podcast IA". ~R$0,30–0,40/inscrito relevante é eficiente.
3. **Reduzir campanhas de "Visualizações"** — compram views sem inscritos; usar só para prova social em lançamento. Depois de 24/ago essa métrica fica ainda mais inflada e ainda menos informativa.
4. **Medir as campanhas de "Visitas ao site" no GA4/vendas** — é onde pode estar o ROI de negócio real (leads/assinaturas), não nas métricas do YouTube.
5. **Adotar `engagedViews` como métrica de aceitação de campanha de views.** Se uma campanha não move views intencionais, não moveu nada.
