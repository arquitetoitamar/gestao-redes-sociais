---
name: pauta-redes-sociais
description: Atualiza as notícias locais monitoradas do TikTok (ex. @danielmaehara) e, quando o usuário pedir, transforma uma notícia em pauta própria — card de imagem (feed 4:5 e story 9:16), texto para Instagram e TikTok e mensagem para o grupo de WhatsApp "#21 Consultoria IA marketplaces Claude ChatGPT" via Chatiops — SEMPRE mostrando tudo para aprovação antes de postar. Use em "atualiza as notícias", "pauta do dia", "pega o mais recente", "posta a notícia no grupo", "monitor TikTok → redes".
---

# Pauta para redes sociais

Duas fases, disparadas pelo usuário. Funciona em qualquer sessão deste repo.

## Fase 1: atualizar notícias locais (gatilho: "atualiza as notícias", "atualizar monitor")

1. `python3 scripts/monitor_tiktok.py` (estado e digest em `output/monitor-tiktok/<conta>/`; adicionar contas em `CONTAS` no script).
2. Ler o digest e **listar ao usuário só os vídeos novos** (data, título/1ª frase da legenda, views). Posts em modo foto sem legenda: sinalizar como "sem texto".
3. Commit e push só de `output/monitor-tiktok/` (arquivos < 10 MB; MP4 grande fica local). Ver memória "estado no repo".
4. **Não gerar card nem postar nada nesta fase.** Perguntar qual notícia virar pauta.

## Fase 2: montar pauta (gatilho: "pauta do dia", "posta a notícia", ou o usuário escolhe uma da lista)

Cadência: uma notícia por dia, disparada pelo usuário. Se já existe `output/pauta-<hoje>-*`, avisar antes de gerar outra.

1. **Reescrever com palavras próprias**: manter fatos (números, nomes, valores), mudar estrutura, ângulo para sellers de marketplace/e-commerce.
   **Não citar a conta do TikTok.** Citar a **fonte original da notícia** (empresa/veículo; confirmar com WebSearch se preciso).
   Se não der para identificar com segurança, omitir o campo `fonte`.
2. Criar `output/pauta-<AAAA-MM-DD>-<slug>/pauta.json` (`tag`, `titulo`, `destaque`, `destaque_legenda`, `bullets` máx. 3, `fonte`) e gerar o card:
   `python3 .agents/skills/pauta-redes-sociais/scripts/gerar_card.py <pasta>/pauta.json <pasta>/`
   Saída: `post_4x5.jpg` (1080x1350) e `story_9x16.jpg` (1080x1920). Ler a imagem e conferir.
3. Escrever na mesma pasta:
   - `instagram.md`: legenda completa, bullets com →, pergunta final, fonte, 8-12 hashtags (@tiopstecnologia).
   - `tiktok.md`: legenda curta (~150 caracteres + hashtags) e roteiro de voz de 30 s.
   - `whatsapp_grupo.txt`: formato WhatsApp (`*negrito*`), sem hashtags.
4. **PORTÃO DE APROVAÇÃO (obrigatório).** Mostrar ao usuário, no chat: o card (abrir a imagem com Read/painel), a legenda do Instagram,
   a do TikTok e a mensagem do grupo. Perguntar o que aprova. **Parar e esperar um "sim" explícito.**
   Edição pedida → ajustar e mostrar de novo. Aprovação não vale para a pauta seguinte.
5. **Só depois do "sim", postar o que foi aprovado** (cada destino é decisão separada: grupo, Instagram, TikTok):
   - Grupo WhatsApp: `send_group_message` (MCP Chatiops; ferramenta diferida, carregar via ToolSearch
     `select:mcp__412ee624-9ab4-429a-b67e-24e89d8badd8__send_group_message,mcp__412ee624-9ab4-429a-b67e-24e89d8badd8__list_groups`).
     Grupo **#21 Consultoria IA marketplaces Claude ChatGPT**, JID `120363407151462316@g.us` (139 membros). Confirmar o JID com `list_groups`;
     há grupos de nomes parecidos. O MCP envia só texto; a imagem não vai ao grupo (API REST é por número e exige `CHATIOPS_TOKEN`).
     Avisar o usuário e deixar o card na pasta para ele anexar.
   - Instagram/TikTok: skills `instagram-graph-publisher` e `tiktok-content-publisher`, só se o usuário aprovou esse destino.
6. Commit e push de `output/pauta-*` (< 10 MB).

## Regras

- Nunca postar sem aprovação explícita na fase 2. Enviar ao grupo atinge 139 pessoas.
- Não publicar faturamento, margem, custo de IA ou dado de cliente (checagem de 5 perguntas das regras de publicação).
- CTA de produto: "Saiba mais", nunca "teste grátis".
- Só imagem e texto; não alterar áudio/vídeo do usuário.
