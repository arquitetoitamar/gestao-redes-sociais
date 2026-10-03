# Prompt para enviar na DM (quem comentar PROMPT)

## Mensagem da DM (copiar e colar)

Oi! Aqui está o prompt que eu falei no vídeo.

Troque só o que está entre [colchetes] pelos seus números e cole no seu agente de IA (ele precisa ter acesso ao Mercado Livre, Shopee e TikTok Shop para trazer dado real).

```
Você é meu agente de pesquisa de produtos. Faça uma varredura dos últimos 30 dias no Mercado Livre, Shopee e TikTok Shop.
Foco: [NICHO, ex.: moda].

REGRA: não temos produto de estimação. Vamos vender o que o mercado quer.

PREMISSA: meu custo de fabricação está definido entre R$ [CUSTO_MIN] e R$ [CUSTO_MAX] por peça.

FILTRO DE VENDAS
- Só produtos com no mínimo [MIN_VENDAS, ex.: 500] unidades vendidas nos últimos 30 dias.
- Sem teto: quanto mais vendeu, melhor.

ANÁLISE DE CADA PRODUTO
1. Volume vendido nos últimos 30 dias.
2. Preço praticado e faixa de preço dos principais concorrentes.
3. Quantos vendedores disputam esse mercado.
4. Se as vendas estão concentradas em poucos anúncios ou pulverizadas entre vários vendedores.

MARGEM
- Cruze com o meu custo de fabricação.
- Desconte comissão da plataforma, taxas, frete e imposto de [IMPOSTO, ex.: 4,5]%.
- Só passa quem ficar com margem de contribuição entre [MARGEM_MIN]% e [MARGEM_MAX]%.

ENTREGA
Faça a triagem e me entregue somente os 10 melhores produtos. Para cada um:
- Produto e plataforma onde encontrou
- Unidades vendidas nos últimos 30 dias
- Preço atual de venda
- Faixa de preço médio dos concorrentes
- Margem de contribuição projetada
- Quantidade de vendedores relevantes

EVIDÊNCIA (obrigatória)
- Link dos anúncios analisados.
- Imagem ou captura dos anúncios sempre que estiverem disponíveis.

FORMATO
Uma tabela comparativa, para eu entender rápido onde está a oportunidade.

REGRA DE OURO
Não invente dado. Se algo não puder ser confirmado, escreva "não confirmado". Tudo precisa ser baseado em dados reais e rastreável até a fonte.
```

Se quiser ver como fazer isso em 5 minutos com a nossa ferramenta, me responde aqui que eu te explico.

## Notas (não enviar)
- Base: o prompt ditado por @cristian.seller no reel de referência, reorganizado e com os números dele trocados por campos para preencher (custo de R$ 10–12, margem de 25–30% e imposto de 4,5% eram dele).
- Os 25–30% de margem não dizem se são sobre o preço de venda ou sobre o custo. Deixei "margem de contribuição". Quem quiser mais preciso pode acrescentar "sobre o preço de venda".
- Sem dado de Shopee/TikTok Shop o agente vai devolver "não confirmado" em muita coisa. O texto da DM já avisa.
