# gestao-redes-sociais

## Rotinas disponíveis (qualquer sessão)

- **"atualiza as notícias"** → skill `pauta-redes-sociais`, fase 1: roda `scripts/monitor_tiktok.py`, lista vídeos novos, commit+push do estado. Não posta nada.
- **"pauta do dia" / "posta a notícia"** → skill `pauta-redes-sociais`, fase 2: gera card + textos (Instagram, TikTok, grupo WhatsApp), **mostra para aprovação e só posta após "sim" explícito**.

## Regras do repo

- Estado e saídas ficam em `output/` e vão para o git (commit + push). Arquivos > 10 MB (vídeos/WAV) não sobem: o GitHub bloqueia > 100 MB.
- Em pautas, citar a fonte original da notícia, nunca a conta do TikTok monitorada.
- Skills ficam em `.agents/skills/` com symlink em `.claude/skills/`.
