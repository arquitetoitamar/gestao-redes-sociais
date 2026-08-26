# Skill `youtube-api` — relatórios e publicação pela API

Skill usada para autenticar e operar a **YouTube Data API v3** e a **YouTube
Analytics API** a partir de ambiente cloud/headless, onde o fluxo OAuth
`run_local_server` não funciona.

**Atualizada em 18/ago/2026.**

## O que ela faz

- Publicar/subir vídeo ou Short no YouTube
- Trocar código OAuth do Google por token
- Definir capa (thumbnail) de um vídeo
- Puxar views, likes e inscritos via API
- Gerar capas verticais com texto grande a partir de um frame do vídeo

## Scripts

| Script | O que faz |
|---|---|
| `scripts/snapshot_views.py` | Congela `views` + `engagedViews` por vídeo (JSON + CSV). É o que mantém a série histórica na régua antiga. |
| `scripts/stats.py` | Canal/vídeo com as duas réguas lado a lado. |
| `scripts/analytics.py` | Relatório com views e intencionais, ⚠ nos vídeos que inflam mais de 2x, e aviso quando o período consultado atravessa 24/ago/2026. |

## Credenciais

- Token OAuth: `~/.hermes/credentials/youtube_token.pickle`
- Client secret: `~/client_secret.json`
- Scopes: `youtube.upload`, `youtube.readonly`, `yt-analytics.readonly`
- Projeto Google Cloud: `gen-lang-client-0236201276`

Reautorizado em 18/ago/2026 com `yt-analytics.readonly` ativo — é o escopo que
libera `engagedViews`.

## Por que `engagedViews` importa

Ver `docs/youtube/mudanca-metricas-views-youtube-2026.md`. Resumo: desde
24/ago/2026 o YouTube conta view no play, sem tempo mínimo. Qualquer comparação
com número anterior a essa data tem que usar `engagedViews`, senão o crescimento
é fantasma.

## Snapshots gerados

- `snapshot_youtube_2026-08-18.json` / `.csv` — 116 vídeos, linha de corte
  pré-cutover (1.490 inscritos, 134.345 views, 53.979 engagedViews).
