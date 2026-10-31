# Posts agendados do Instagram sem depender do Mac

A API do Instagram não agenda. Aqui o agendamento roda na AWS (conta 615026068056, us-east-1):
EventBridge Scheduler (`ig-<id>`, uma vez, fuso America/Sao_Paulo, se apaga depois) → Lambda
`tiops-ig-agendado` → Graph API do @tiopstecnologia.

- Token: Secrets Manager `tiops/instagram/tiopstecnologia` (copiado de `~/.hermes/credentials/instagram_config.json` por `agenda.py infra`, nunca impresso).
- Mídia: `s3://tiops-public-assets-1785392019/temp/agendados/` (prefixo público); apagada depois de publicar.
- Resultado: `s3://tiops-public-assets-1785392019/agendados-estado/<id>.json` (`publicado` com link, ou `erro`).
- Sem repetição: retentativa 0 no Scheduler e na Lambda, e a marca de estado impede rodar duas vezes.

```bash
python3 agenda.py agenda <id> reel|imagem <arquivo> <legenda.md> "AAAA-MM-DD HH:MM" [capa_ms]
python3 agenda.py lista
python3 agenda.py cancela <id>
```
