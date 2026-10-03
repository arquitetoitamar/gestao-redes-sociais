---
name: pauta-redes-sociais
description: Pega o vídeo mais recente de uma conta monitorada do TikTok (ex. @danielmaehara), transforma em pauta própria, gera card de imagem (feed 4:5 e story 9:16), formata texto para Instagram e TikTok e posta no grupo de WhatsApp "#21 Consultoria IA marketplaces Claude ChatGPT" via Chatiops. Use quando pedirem "pega o mais recente", "pauta do dia", "posta a notícia no grupo", "monitor TikTok → redes".
---

# Pauta para redes sociais

Fluxo completo, do monitor TikTok ao grupo de WhatsApp.

## Passos

1. **Atualizar o monitor** (grava estado em `output/monitor-tiktok/<conta>/`):
   `python3 scripts/monitor_tiktok.py`
   Pegar o vídeo mais recente **com legenda** em `output/monitor-tiktok/<conta>/digest.md`
   (posts em modo foto sem legenda não servem como pauta; avisar o usuário e usar o anterior).
2. **Reescrever com palavras próprias**: nunca copiar a legenda. Manter fatos (números, nomes, valores),
   mudar estrutura e adicionar ângulo para sellers de marketplace/e-commerce. Sempre creditar a fonte (`Fonte: @conta`).
3. **Montar `output/pauta-<AAAA-MM-DD>-<slug>/pauta.json`** com `tag`, `titulo`, `destaque`,
   `destaque_legenda`, `bullets` (máx. 3), `fonte`. Gerar o card:
   `python3 .agents/skills/pauta-redes-sociais/scripts/gerar_card.py <pasta>/pauta.json <pasta>/`
   Saída: `post_4x5.jpg` (1080x1350) e `story_9x16.jpg` (1080x1920). **Ler a imagem** e conferir antes de seguir.
4. **Formatar o texto por rede** na mesma pasta:
   - `instagram.md`: legenda completa, bullets com →, pergunta final, fonte, 8-12 hashtags. Conta @tiopstecnologia.
   - `tiktok.md`: legenda curta (~150 caracteres + hashtags) e roteiro de voz de 30 s (gancho, fato, conexão, pergunta).
   - `whatsapp_grupo.txt`: formato WhatsApp (`*negrito*`, emojis moderados), sem hashtags.
5. **Postar no grupo** com `send_group_message` (MCP Chatiops, ferramenta diferida: carregar via ToolSearch
   `select:mcp__412ee624-9ab4-429a-b67e-24e89d8badd8__send_group_message,...__list_groups`).
   - Grupo: **#21 Consultoria IA marketplaces Claude ChatGPT**, JID `120363407151462316@g.us` (139 membros).
     Confirmar o JID com `list_groups` antes; existem vários grupos de nomes parecidos.
   - O MCP envia **só texto**. A API REST do Chatiops (`/api/messages/send`) é por número e exige `CHATIOPS_TOKEN`,
     então a imagem não vai ao grupo por aqui: avisar o usuário e deixar o card na pasta para ele anexar.
6. **Registrar e publicar o trabalho**: commit e push da pasta `output/pauta-*` (só arquivos < 10 MB). Ver
   regra em memória "estado no repo".

## Regras

- Enviar ao grupo é ação pública para 139 pessoas: só enviar quando o usuário pediu explicitamente nesta sessão.
- Não publicar faturamento, margem, custo de IA ou dado de cliente. Fazer a checagem de 5 perguntas das regras de publicação.
- CTA de produto: "Saiba mais", nunca "teste grátis".
- Áudio/vídeo do usuário: não alterar. Esta skill usa só imagem e texto.
- Postagem em Instagram/TikTok é à parte (skills `instagram-graph-publisher` e `tiktok-content-publisher`).
