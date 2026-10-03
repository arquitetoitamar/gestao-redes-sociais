# gestao-redes-sociais

## Rotinas disponíveis (qualquer sessão)

- **"atualiza as notícias"** → skill `pauta-redes-sociais`, fase 1: roda `scripts/monitor_tiktok.py`, lista vídeos novos, commit+push do estado. Não posta nada.
- **"pauta do dia" / "posta a notícia"** → skill `pauta-redes-sociais`, fase 2: gera card + textos (Instagram, TikTok, grupo WhatsApp), **mostra para aprovação e só posta após "sim" explícito**.

## Regras do repo

- Estado e saídas ficam em `output/` e vão para o git (commit + push). Arquivos > 10 MB (vídeos/WAV) não sobem: o GitHub bloqueia > 100 MB.
- Em pautas, citar a fonte original da notícia, nunca a conta do TikTok monitorada.
- Skills ficam em `.agents/skills/` com symlink em `.claude/skills/`.

## Dependências fora do repo (conferir em máquina/Claude novo)

- `yt-dlp` (monitor TikTok): `brew install yt-dlp`
- Playwright + Chromium (card de imagem): `pip install playwright && playwright install chromium`
- Conector **Chatiops (MCP)** conectado na conta Claude, para `send_group_message` / `list_groups`.
- `.env` local (não versionado); modelo em `.env.example`. A API REST do Chatiops precisa de `CHATIOPS_TOKEN` (só se for enviar imagem ao grupo).
- Memórias do Claude não viajam com o repo; as regras essenciais estão na skill `pauta-redes-sociais`.
