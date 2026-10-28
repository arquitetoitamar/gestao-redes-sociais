# LinkedIn: Imersão IA para Marketplaces (24/10/2026)

Publicado em 28/10/2026, 01h: https://www.linkedin.com/feed/update/urn:li:activity:7521061130383859712/

- Texto em `texto.md`. Não cita que o Itamar é fundador (pedido dele); "tive a oportunidade de falar" no lugar de "fui convidado", porque a Imersão é da Tiops.
- 6 fotos da pasta do videomaker (Drive "IA para Marketplaces/Fotos", 125 fotos), reduzidas para 2048 px: 9763 (sala cheia, capa), 9697, 9677, 9690, 9695, 9775.
- Publicado pelo Chrome. O LinkedIn só cria o `input[type=file]` no clique de "Mídia"; para não abrir o seletor nativo, o `HTMLInputElement.prototype.click` foi interceptado antes do clique e as fotos subiram direto no input. Colar texto: `ClipboardEvent('paste')` com `text/html` em `<p>`, intercalando `<p><br></p>`, senão as linhas em branco somem.
