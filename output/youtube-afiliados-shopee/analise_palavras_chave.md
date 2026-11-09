# Palavras-chave: busca "shopee afiliados" no YouTube (09/11/2026)

Fonte: API do YouTube (search + tags dos 20 primeiros resultados, `concorrentes_shopee_afiliados.json`) e autocompletar do YouTube.

## Padrão dos primeiros colocados
- Título começa com a palavra exata em maiúsculas: "AFILIADO SHOPEE:" ou "(Afiliado Shopee)" (11 de 20).
- Termos que se repetem no título: "passo a passo" (14), "vender" / "como vender" (9), "guia completo" / "do zero" (7), "Shopee Vídeo" (5), "2026" (4).
- Promessa em maiúsculas: "VENDER MUITO", "Vender HOJE", "Primeira Venda", "O NOVO jeito", "Técnica Absurda".
- Tags: palavra principal + cauda longa. Mais usadas: afiliado shopee (12), afiliado shopee passo a passo (6), afiliado shopee vale a pena (5),
  como vender na shopee (5), afiliado shopee como divulgar, link de afiliado shopee, como ser afiliado shopee, renda extra,
  como ganhar dinheiro na shopee. Nicho IA: video com ia para shopee, google flow, fazer video com ia.
- Shorts dominam em views (600 mil a 1,3 milhão em 25–50 s); vídeos longos ficam entre 20 e 300 mil.
- Autocompletar: afiliado shopee com ia, como ser afiliado shopee 2026, link de afiliado shopee, shopee video afiliado com ia,
  ia para afiliados shopee, claude afiliado shopee.

## Aplicado
- Vídeo Mg7mIiimaOw: título "AFILIADO SHOPEE com IA: Passo a Passo para VENDER com o ChatGPT (Links, Vídeos e Achadinhos 2026)",
  20 tags (487 caracteres), descrição abrindo com a mesma frase, hashtags #afiliadoshopee #shopeeafiliados #shopeevideo (`atualiza_meta.py`).
- 3 Shorts cortados do vídeo (`shorts.py`), agendados às 18h com 48 h entre eles (`sobe_shorts.py`, `shorts_publicados.json`):
  10/11 maior comissão, 12/11 link em segundos, 14/11 vídeo feito pela IA. Todos com link para o vídeo completo.
