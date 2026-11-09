# Vídeo YouTube: Afiliado Shopee no ChatGPT (09/11/2026)

Publicado: https://youtu.be/Mg7mIiimaOw (público, 09/11 às ~16h10).
Original: `~/Downloads/afiliados.mp4` (15min16s, gravação de tela). Editado: `~/Downloads/afiliados - editado.mp4` (14min21s). Vídeos não vão para o git (> 10 MB).

## Edição
- `edita.py`: acelera 4x as 18 esperas em silêncio (> 3 s) com selo "⏩ 4x"; áudio original intacto nas falas.
  Desfoca o que não pode ir a público: lista de lojas no painel do Marketplace Connect (0:42–0:57),
  lista escurecida atrás das janelas (0:57–1:35, janela "Conectar Shopee Afiliados" nítida), lista de integrações
  (1:35–1:42) e a lateral de projetos/conversas do ChatGPT sempre que ela aparece (detecção por luminância).
- `monta.py` + `motions.html`: abertura animada, nome, barra de passo (Passo 1 a 6, bônus e extras), cartões de prompt,
  cartão do endereço do conector, lembretes "link na descrição", tela final de 8 s; gera `capitulos.txt`.
- `sobe_youtube.py`: título, descrição com capítulos e links, 19 tags (palavras do autocompletar do YouTube), categoria Educação,
  pt-BR, mídia sintética declarada (os vídeos de produto mostrados são de IA), capa `capa_b.jpg`.

## Links
- Marketplace Connect: https://l.tiops.com.br/shopee-afiliados?o=youtube (campanha shopee-afiliados-nov26 → marketplaces.tiops.com.br)
- Conector: https://mcp.tiops.com.br/mcp/afiliados

## Capa
Higgsfield (gpt_image_2_6, 2k, alta), referência: capa aprovada "ChatGPT publica no Mercado Livre". `capa_b.jpg` publicada, `capa_a.jpg` alternativa.

## Pendências
- Tela final e cards do YouTube: a API não permite; colocar no Studio (inscrever-se + vídeo do Marketplace Connect).
- Comentário fixado com os links: o token não tem o escopo force-ssl; fixar à mão no Studio.
