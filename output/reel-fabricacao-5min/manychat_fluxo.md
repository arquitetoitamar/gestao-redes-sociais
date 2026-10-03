# ManyChat: fluxo "Comenta PROMPT → prompt na DM"

Limite do Instagram: 1.000 caracteres por mensagem de DM. Todas as mensagens abaixo estão dentro do limite (o prompt foi dividido em 3 partes).

## Gatilho
Automação → Instagram → **Comentário em post ou Reel**. Escolha "qualquer publicação" (ou só os Reels com o CTA).
Palavras-chave (qualquer uma): `prompt`, `quero`, `eu quero`, `me manda`, `manda`

## Resposta pública automática (varie, para não parecer spam)
- Te mandei na DM! 📩
- Confere sua DM 😉
- Enviei! Dá uma olhada nas mensagens 📩

## Mensagens da DM (nesta ordem, com ~2 s entre elas)

### Mensagem 1 (abertura) (260 caracteres)
```
Oi! Aqui está o prompt que eu falei no vídeo. Vou mandar em 3 mensagens: copie as 3 juntas e cole no seu agente de IA (ele precisa ter acesso ao Mercado Livre, Shopee e TikTok Shop para trazer dado real). Troque o que está entre [colchetes] pelos seus números.
```

### Mensagem 2 (prompt, parte 1/3) (727 caracteres)
```
Você é meu agente de pesquisa de produtos. Faça uma varredura dos últimos 30 dias no Mercado Livre, Shopee e TikTok Shop. Foco: [NICHO, ex.: moda].

REGRA: não temos produto de estimação. Vamos vender o que o mercado quer.

PREMISSA: meu custo de fabricação está entre R$ [CUSTO_MIN] e R$ [CUSTO_MAX] por peça.

FILTRO DE VENDAS
- Só produtos com no mínimo [MIN_VENDAS, ex.: 500] unidades vendidas nos últimos 30 dias.
- Sem teto: quanto mais vendeu, melhor.

ANÁLISE DE CADA PRODUTO
1. Volume vendido nos últimos 30 dias.
2. Preço praticado e faixa de preço dos principais concorrentes.
3. Quantos vendedores disputam esse mercado.
4. Se as vendas estão concentradas em poucos anúncios ou pulverizadas entre vários vendedores.
```

### Mensagem 3 (prompt, parte 2/3) (513 caracteres)
```
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
```

### Mensagem 4 (prompt, parte 3/3) (364 caracteres)
```
EVIDÊNCIA (obrigatória)
- Link dos anúncios analisados.
- Imagem ou captura dos anúncios sempre que estiverem disponíveis.

FORMATO
Uma tabela comparativa, para eu entender rápido onde está a oportunidade.

REGRA DE OURO
Não invente dado. Se algo não puder ser confirmado, escreva "não confirmado". Tudo precisa ser baseado em dados reais e rastreável até a fonte.
```

### Mensagem 5 (CTA) (139 caracteres)
```
Quer ver como fazer esse tipo de pesquisa em 5 minutos com a nossa ferramenta? Saiba mais: https://l.tiops.com.br/ia-marketplace?o=manychat
```

## Dicas
- Marque quem recebeu com a tag `lead-prompt-fabricacao` para poder segmentar depois.
- Teste com a sua própria conta secundária antes de ligar.
- O ManyChat só consegue mandar a DM em até 7 dias depois do comentário.
- Para outros vídeos, troque o texto do prompt e a tag, e mantenha o mesmo gatilho.
