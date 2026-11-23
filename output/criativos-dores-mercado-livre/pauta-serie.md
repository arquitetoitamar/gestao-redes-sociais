# Série "Pergunta pro Claude" — pauta completa (23/11/2026)

Formato aprovado pelo Itamar no nº 2 ("ficou show"): **um problema específico → orientação em 4 passos → "agora faz isso em N anúncios" → a pergunta pro Claude com o Marketplace Connect → resposta pronta → Comenta CONNECT.**
Cada episódio muda a cor de destaque (pedido do Itamar).
**Fundo SEMPRE branco** (Itamar, 23/11: "não use fundo escuro, fundo escuro fica com cara de IA"). A paleta de cada episódio define só a cor de destaque: use o 2º hex como `accent`, um tom mais claro como `accent2`, um mais escuro como `destaque` (palavra da legenda e tags) e um bem claro como `brilho` (o halo do fundo). Exemplos: ep 1 verde #059669/#34d399/#047857/#ecfdf5; ep 2 azul #2563eb/#60a5fa/#1d4ed8/#eff6ff.
 Valores na tela sempre "de exemplo". Texto nosso, sem copiar o perfil de referência.
Motor: `output/serie-pergunta-claude/motor/` (narração HeyGen voz c463ef5b ~US$ 0,12 por episódio). Sem saldo na HeyGen a tarefa para e avisa no WhatsApp.

| # | Status | Data |
|---|---|---|
| 1 Visita sem venda (refeito) | a gerar · JSON pronto (episodios/01) | 24/11 16h |
| 2 Reposição do Full | IG agendado 24/11 18h · Shorts publicado 23/11 (2eLnF7hcG_o) | 24/11 18h |
| 3 Fotos | a gerar | 24/11 20h |
| 5 Ficha técnica | a gerar | 25/11 16h |
| 11 Perguntas sem resposta | a gerar | 25/11 18h |
| 6 Catálogo perdido | a gerar | 25/11 20h |
| Chatiops + Claude (avulso, fora da série) | agendado IG + Shorts | 26/11 16h |
| 9 Resumo da manhã | a gerar | 26/11 18h |
| 7 Subir preço em degraus | a gerar | 26/11 20h |
| 8 Desconto com selo e piso de margem | a gerar | 28/11 16h |
| 10 Números do anúncio | a gerar | 28/11 18h |
| 13 Reclamação e reputação | a gerar | 28/11 20h |
| 12 Mesmo produto no ML e na Shopee | a gerar | 29/11 16h |
| 14 Qual logística usar | a gerar | 29/11 18h |
| 16 Quem vende o ano inteiro | a gerar | 29/11 20h |
| 17 Ads gastando sem vender | a gerar | 30/11 16h |
| 18 Estoque parado | a gerar | 30/11 18h |
| 19 Envio atrasado | a gerar | 30/11 20h |
| 20 Devolução que se repete | a gerar | 01/12 16h |
| 21 Abaixo do frete grátis | a gerar | 01/12 18h |
| 22 Mensagem pós-venda sem resposta | a gerar | 01/12 20h |
| 23 Campanha do ML que você perdeu | a gerar | 02/12 16h |
| 24 Quanto sobra de cada venda | a gerar | 02/12 18h |
| 25 Estoque demais no Full | a gerar | 02/12 20h |
| 26 Pedido sem nota fiscal | a gerar | 03/12 16h |
| 27 Anúncio fraco na Shopee | ⚠ confirmar diagnóstico de qualidade da Shopee no MC | 03/12 18h |
| 28 Título sem a palavra que o cliente busca | a gerar | 03/12 20h |
| 15 O que vender | ⚠ confirmar dados de concorrentes; sem OK, não sai | — |
| 4 Anúncio sem vídeo | ⚠ confirmar se gerar/subir clip com IA está liberado | — |

Pedido do Itamar (23/11): **3 episódios por dia, às 16h, 18h e 20h** ("Sim quero 3 postagem por dia"; escolheu "só MC, 3 episódios por dia"), gerados e postados sozinhos pela tarefa `serie-pergunta-claude-diaria` (10h gera os do dia, agenda Instagram + Shorts nos horários e manda prévia no WhatsApp). Horário ocupado por post avulso fica de fora (26/11 16h = Chatiops). Pula 27/11 (Dia D da Black Friday). Custo HeyGen ~US$ 0,36/dia. Motor: `output/serie-pergunta-claude/` (`motor/gera.py`, `motor/publica.py`, `episodios/NN-slug.json`).

## Uso como treinamento do Marketplace Connect (pedido do Itamar, 23/11)
Depois da série, os vídeos viram treinamento por tema: Estoque e Full (2), Anúncio (1, 3, 4, 5, 10), Preço e promoção (7, 8, 6), Atendimento e reputação (11, 13), Rotina (9), Multicanal (12).

## Monitoramento do perfil de referência
Tarefa diária `monitor-pronix-pauta` (09h30): confere Reels novos do @pronixnapratica (estado em `pronix-estado.json`), tira a dor de cada um e acrescenta um episódio novo nesta pauta, com texto nosso, paleta nova e a próxima data livre. Só leitura no Instagram; não gera vídeo nem posta.

## Episódios

### 1. Anúncio com visita e sem venda (refazer) — paleta esmeralda (#064e3b / #10b981 / destaque #fde68a)
- Gancho: "Seu anúncio tem visita e não vende? Não baixa o preço ainda."
- Passos: 1) pouca visita → o problema é título e capa; 2) passou de 50 visitas sem venda → o problema está dentro do anúncio; 3) pergunta que se repete vira resposta no próprio anúncio; 4) preço por último, e muda uma coisa por vez.
- Pergunta: "Quais anúncios tiveram mais de 50 visitas e nenhuma venda no último mês? O que falta em cada um?"
- Resposta: luminária sem vídeo · organizador com ficha vazia · suporte com a mesma pergunta 5×.

### 3. Fotos do anúncio — paleta violeta (#2e1065 / #8b5cf6 / #f0abfc)
- Gancho: "Seu anúncio tem 3 fotos? Você está perdendo venda no celular."
- Passos: 1) capa com fundo branco e sem texto; 2) da segunda foto em diante, benefício e medida; 3) produto em uso, na mão ou no ambiente; 4) responde a dúvida na foto, porque no celular ninguém desce até a descrição.
- Pergunta: "Quais dos meus 30 anúncios mais visitados têm menos de 6 fotos?"
- Resposta: lista com nº de fotos e visitas, os mais visitados no topo.

### 5. Ficha técnica incompleta — paleta petróleo e lima (#083344 / #22d3ee / #bef264)
- Gancho: "Campo vazio na ficha técnica tira seu anúncio do filtro da busca."
- Passos: 1) preenche todos os campos, até os opcionais; 2) no campo modelo, sinônimo que não coube no título; 3) não repete palavra do título; 4) código de barras também conta.
- Pergunta: "Quais anúncios têm campos da ficha técnica vazios? Me sugere o preenchimento."
- Resposta: anúncio · campos vazios (ex.: 7) · sugestão pronta para aprovar.

### 11. Perguntas sem resposta — paleta verde-limão sobre grafite (#1c1917 / #84cc16 / #fef08a)
- Gancho: "Pergunta respondida depois de 3 horas é venda pro concorrente."
- Passos: 1) responde em menos de 1 hora; 2) pergunta repetida vira informação no anúncio; 3) resposta curta, com o benefício; 4) à noite e no fim de semana também tem cliente.
- Pergunta: "Quais perguntas estão sem resposta e quais se repetem? Sugere a resposta de cada uma."
- Resposta: 4 sem resposta (há 2 h, 5 h…) · "voltagem" repetida 6× → sugestão de colocar no título/ficha. Responder só com OK.

### 6. Catálogo perdido — paleta vinho e rosa (#4c0519 / #f43f5e / #fecdd3)
- Gancho: "Seu anúncio caiu no catálogo e parou de vender?"
- Passos: 1) confere se você está ganhando a vitrine; 2) vê quanto falta pra ganhar e se ainda sobra margem; 3) não compensa? kit ou anúncio próprio; 4) catálogo que vende e é seu, fica.
- Pergunta: "Em quais catálogos eu estou perdendo e quanto falta pra ganhar, sem passar do meu piso?"
- Resposta: anúncio · preço pra ganhar · cabe no piso? (sim/não).

### 9. Resumo da manhã — paleta âmbar clara (fundo #fffbeb / texto #1c1917 / destaque #d97706)
- Gancho: "Todo dia de manhã eu faço uma pergunta pro Claude."
- Passos: 1) venda de ontem contra a média da semana; 2) vendeu menos → falta ajuste no anúncio; 3) vendeu mais → falta estoque; 4) na segunda, olha o fim de semana inteiro.
- Pergunta: "Como foi ontem contra a média de 7 dias? O que caiu, o que subiu e o que vai zerar de estoque?"
- Resposta: 3 blocos (caiu / subiu / vai zerar).

### 7. Subir preço sem perder posição — paleta preto e amarelo (#0a0a0a / #facc15 / #fafafa)
- Gancho: "Subiu 10% de uma vez e o anúncio sumiu?"
- Passos: 1) mexe na promoção, não no preço base; 2) sobe de 2 em 2%; 3) vendeu igual, sobe mais; caiu, volta; 4) deixa a próxima promoção pronta antes da atual acabar.
- Pergunta: "Nos anúncios com promoção que venderam igual na última semana, sugere a próxima 2% mais cara, sem passar do meu piso."
- Resposta: anúncio · promoção atual · próxima · aprovar.

### 8. Desconto com selo sem perder margem — paleta teal (#042f2e / #14b8a6 / #ccfbf1)
- Gancho: "Dá pra ganhar o selo de desconto sem tirar nada da margem."
- Passos: 1) preço cheio maior + desconto na central = mesmo preço final; 2) anota o piso de cada anúncio; 3) campanha pedindo desconto maior? confere o piso antes; 4) desconto de 50, 70% vicia o cliente.
- Pergunta: "Quais campanhas ativas me deixam abaixo do piso de margem?"
- Resposta: campanha · anúncio · preço final · abaixo do piso? 

### 10. Números do anúncio — paleta índigo (#1e1b4b / #818cf8 / #c7d2fe)
- Gancho: "Como saber se o seu anúncio está bom? Três números."
- Passos: 1) de impressão pra clique, pelo menos 1%; 2) abaixo disso, mexe na capa e no título; 3) de visita pra venda, de 2 a 3%; 4) abaixo disso, o problema está dentro do anúncio.
- Pergunta: "Compara meus anúncios com essas réguas. Onde cada um está travando?"
- Resposta: anúncio · clique % · conversão % · trava em (capa/título ou dentro do anúncio).

### 13. Reclamação e reputação — paleta vermelho escuro (#450a0a / #ef4444 / #fecaca)
- Gancho: "Uma reclamação sem resposta pode derrubar a sua cor de reputação."
- Passos: 1) responde em até 24 h; 2) oferece a solução antes da mediação; 3) olha o motivo que se repete; 4) corrige o anúncio que gera reclamação.
- Pergunta: "Quais reclamações abertas afetam minha reputação e qual o prazo de cada uma?"
- Resposta: reclamação · motivo · prazo · afeta reputação (sim/não).

### 12. Mesmo produto no Mercado Livre e na Shopee — paleta coral (#431407 / #fb923c / #ffedd5)
- Gancho: "Mesmo preço no Mercado Livre e na Shopee? Sua margem não é a mesma."
- Passos: 1) comissão muda de canal pra canal; 2) frete e subsídio também; 3) calcula o preço por canal pelo piso; 4) revisa quando o canal muda a taxa.
- Pergunta: "Compara a margem dos meus 10 produtos mais vendidos no Mercado Livre e na Shopee."
- Resposta: produto · margem ML · margem Shopee · ajuste sugerido.

### 4. Anúncio sem vídeo — paleta grafite e laranja (#18181b / #f97316 / #fed7aa) ⚠ confirmar produto
- Gancho: "Quantos dos seus anúncios que mais vendem não têm vídeo?"
- Passos: 1) um clip que tira dúvida; 2) um clip de uso, que traz gente de fora; 3) a palavra-chave falada no começo; 4) narração e legenda, não só música.
- Pergunta: "Lista os 20 anúncios mais visitados sem clip." (+ "gera um clip pro primeiro", só se a função estiver liberada no plano).

### 14. Qual logística usar — paleta azul-gelo (#0c4a6e / #38bdf8 / #e0f2fe)
- Gancho: "Correios, Agência, Flex ou Full? A escolha errada te tira da primeira página."
- Passos: 1) conta quantos anúncios da primeira página estão no Full; 2) produto de giro rápido vai pro Full; 3) Flex quando você entrega na sua cidade no mesmo dia; 4) Correios e Agência pra começar e testar.
- Pergunta: "Quais dos meus anúncios vendem mais de 2 por dia e ainda não estão no Full?"
- Resposta: anúncio · venda/dia · logística atual · sugestão.

### 15. O que vender — paleta mostarda (#422006 / #eab308 / #fef9c3) ⚠ confirmar dados de mercado
- Gancho: "Antes de comprar estoque, passa o produto por esse filtro."
- Passos: 1) busca com uma ou duas palavras; 2) vê quanto os 5 primeiros vendem por mês; 3) preço na média, nunca o mais barato; 4) acha o furo dos concorrentes (foto, vídeo, pergunta sem resposta).
- Pergunta: "Pra 'luminária de mesa', quanto vendem os 5 primeiros, qual o preço médio e o que falta nos anúncios deles?"
- Resposta: tabela de concorrentes + furo de cada um.

### 16. Quem vende o ano inteiro — paleta oliva (#1a2e05 / #65a30d / #ecfccb)
- Gancho: "Seu produto vende o ano todo ou só em dezembro?"
- Passos: 1) olha a venda mês a mês do último ano; 2) mês fraco não é anúncio ruim; 3) estoque acompanha a curva; 4) produto de ano inteiro é a base da loja.
- Pergunta: "Mostra a venda mês a mês dos meus 10 principais produtos e quais são sazonais."
- Resposta: produto · curva · "ano inteiro" ou "sazonal (pico em …)".

### 17. Ads gastando sem vender — paleta laranja (#ea580c)
- Gancho: "Seu Mercado Ads está gastando e não vende?"
- Passos: 1) olha o gasto por anúncio, não o total; 2) gastou sem vender em 14 dias, pausa; 3) põe a verba onde já vende; 4) revisa toda semana, não todo dia.
- Pergunta: "Quais anúncios no Ads gastaram mais de R$ 50 nos últimos 14 dias sem nenhuma venda?"
- Resposta: anúncio · gasto · vendas 0 · sugestão pausar.

### 18. Estoque parado — paleta ardósia (#475569)
- Gancho: "Tem produto parado há 2 meses prendendo o seu dinheiro?"
- Passos: 1) lista o que não vende há 60 dias; 2) vê se o problema é anúncio ou produto; 3) kit ou promoção pra girar; 4) não recompra o que encalhou.
- Pergunta: "Quais produtos com estoque não tiveram venda nos últimos 60 dias?"
- Resposta: produto · estoque · última venda · sugestão (kit/promoção).

### 19. Envio atrasado — paleta vermelho-tijolo (#b91c1c)
- Gancho: "Um envio atrasado já pesa na sua reputação."
- Passos: 1) confere todo dia o que vence hoje; 2) prioriza o que está mais perto do prazo; 3) etiqueta impressa cedo; 4) produto que sempre atrasa, revê o prazo do anúncio.
- Pergunta: "Quais pedidos precisam ser despachados hoje e quais já estão atrasados?"
- Resposta: pedido · produto · prazo · status (hoje/atrasado).

### 20. Devolução que se repete — paleta ameixa (#9333ea)
- Gancho: "Devolução com o mesmo motivo é o anúncio avisando que está errado."
- Passos: 1) agrupa as devoluções por motivo; 2) "não era o esperado" é foto ou descrição; 3) "defeito" é fornecedor; 4) corrige o anúncio antes de vender mais.
- Pergunta: "Quais produtos tiveram devolução nos últimos 30 dias e qual o motivo mais comum de cada um?"
- Resposta: produto · devoluções · motivo · o que corrigir.

### 21. Abaixo do frete grátis — paleta azul-petróleo (#0e7490)
- Gancho: "Seu produto custa R$ 75 e perde venda por causa do frete?"
- Passos: 1) lista o que está pouco abaixo do valor do frete grátis; 2) monta kit com 2 unidades; 3) ou um acessório junto; 4) compara a venda antes e depois.
- Pergunta: "Quais anúncios estão entre R$ 60 e R$ 78 e vendem pelo menos 1 por dia?"
- Resposta: anúncio · preço · venda/dia · sugestão de kit.

### 22. Mensagem pós-venda sem resposta — paleta verde-água (#0d9488)
- Gancho: "Cliente que comprou e não teve resposta vira reclamação."
- Passos: 1) responde mensagem de comprador no mesmo dia; 2) dúvida de entrega: manda o rastreio; 3) problema com o produto: oferece solução antes de virar reclamação; 4) mensagem repetida vira informação no anúncio.
- Pergunta: "Quais mensagens de compradores estão sem resposta e há quanto tempo?"
- Resposta: pedido · assunto · há quanto tempo · sugestão de resposta (envia só com OK).

### 23. Campanha do ML que você perdeu — paleta amarelo-ouro (#ca8a04)
- Gancho: "O Mercado Livre te convidou pra campanha e você nem viu?"
- Passos: 1) confere as campanhas abertas pra sua conta; 2) vê quais anúncios são candidatos; 3) entra só onde o preço final cabe no seu piso; 4) anota quando a campanha acaba.
- Pergunta: "Quais campanhas estão abertas pra minha conta e quais anúncios meus cabem sem passar do piso?"
- Resposta: campanha · anúncio · preço final · cabe no piso?

### 24. Quanto sobra de cada venda — paleta verde-musgo (#4d7c0f)
- Gancho: "Você sabe quanto sobra de cada venda depois da comissão e do frete?"
- Passos: 1) parte do preço de venda; 2) tira comissão e taxa fixa; 3) tira o frete que você paga; 4) tira o custo do produto e o imposto.
- Pergunta: "Calcula quanto sobra por venda nos meus 10 anúncios mais vendidos, com comissão, frete e custo."
- Resposta: anúncio · preço · sobra por venda · % (valores de exemplo).

### 25. Estoque demais no Full — paleta índigo-claro (#4f46e5)
- Gancho: "Estoque parado no Full também custa."
- Passos: 1) lista o que está há mais tempo no armazém; 2) compara com a venda por dia; 3) mais de 90 dias de estoque, para de mandar; 4) gira com promoção ou tira do Full.
- Pergunta: "Quais produtos no Full têm estoque pra mais de 90 dias de venda?"
- Resposta: produto · no Full · venda/dia · dias de estoque.

### 26. Pedido sem nota fiscal — paleta azul-royal (#1d4ed8)
- Gancho: "Pedido parado esperando nota fiscal atrasa o envio."
- Passos: 1) lista os pedidos pagos sem nota; 2) confere os dados fiscais do produto (NCM, origem); 3) emite em lote; 4) confere se a nota chegou no pedido.
- Pergunta: "Quais pedidos pagos ainda estão sem nota fiscal?"
- Resposta: pedido · produto · pago há · status da nota.

### 27. Anúncio fraco na Shopee — paleta coral-claro (#f97316) ⚠ confirmar
- Gancho: "A Shopee diz que seu anúncio é fraco e você nem sabe por quê."
- Passos: 1) confere a nota de qualidade de cada anúncio; 2) faltam fotos ou vídeo? completa; 3) descrição curta? completa; 4) atributos vazios? preenche.
- Pergunta: "Quais anúncios meus na Shopee têm diagnóstico de qualidade baixo e o que falta em cada um?"
- Resposta: anúncio · nota · o que falta.

### 28. Título sem a palavra que o cliente busca — paleta rosa-escuro (#be185d)
- Gancho: "Seu título tem a palavra que o cliente digita na busca?"
- Passos: 1) descobre como o cliente chama o produto; 2) a palavra principal vai no começo do título; 3) sem palavra repetida e sem marca dos outros; 4) muda um título por vez e acompanha as visitas.
- Pergunta: "Quais dos meus títulos não têm a palavra mais buscada da categoria?"
- Resposta: anúncio · título atual · palavra que falta · sugestão de título.
