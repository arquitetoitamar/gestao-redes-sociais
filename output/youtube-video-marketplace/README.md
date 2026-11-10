# Vídeo YouTube: vídeo de produto com IA para marketplace (10/11/2026)

Original: `~/Downloads/como gerar video par ao Marketplace .mp4` (22min35s, gravação de tela). Editado: `~/Downloads/video de produto com IA - editado.mp4`.
Vídeos não vão para o git (> 10 MB). Publicado: https://youtu.be/rirx1DWcSuk (público, 10/11/2026 ~18h50).

## Edição (`edita.py`, depois `monta.py`)
- Pedido: "acelere o vídeo pra ficar mais rápido". Fala em 1,2x (atempo, sem outro tratamento de áudio); esperas em silêncio em 4x
  com selo "⏩ 4x"; silêncios com o vídeo gerado tocando ficam em 1x (detectados por movimento na tela). 22min35s → 16min32s + 8 s de tela final.
- Cortado 20:12–21:17 do original: tentativa de adicionar um segundo conector (`/mcp/utils`) no Gemini que não completou e mostrava o e-mail.
- Desfoque: lista de conversas, projetos e conta na lateral do ChatGPT e do Gemini (pela URL na barra, OCR em `trab/url.json`)
  e a URL do bucket S3 no começo (0:32–0:52).
- Motions (`motions.html`): abertura de 6 s, nome, barra de capítulo na margem de cima, cartões dos prompts, cartão "o que a IA precisa",
  cartão do conector `mcp.tiops.com.br/mcp`, lembretes "link na descrição", tela final de 8 s.
- Legenda queimada na faixa cinza de baixo: whisper.cpp + correções de nomes (ChatGPT, Gemini, Higgsfield, UGC, /storyboard).
  A API não sobe legenda (o token não tem o escopo force-ssl).
- Capítulos em `capitulos.txt`, sem capítulo na tela final (capítulo com menos de 10 s esconde todos).

## Links
- Marketplace Connect: https://l.tiops.com.br/video-produto?o=youtube (campanha video-produto-nov26 → marketplaces.tiops.com.br/comece)
- Conector: https://mcp.tiops.com.br/mcp · Google Flow: https://flow.google.com

## Capa
Higgsfield `gpt_image_2_6` com a capa do vídeo de afiliados como referência (rosto e estilo). `capa_a.jpg` publicada, `capa_b.jpg` alternativa.

## Pendências
- Tela final e cards do YouTube: a API não permite; colocar no Studio.
- Comentário fixado com os links: fixar à mão no Studio.
