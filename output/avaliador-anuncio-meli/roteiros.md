# Avaliador de anúncio do Mercado Livre — roteiros e estrutura (rascunho)

Origem: briefing do DEV (card 143). Página: marketplaces.tiops.com.br/avaliar-anuncio-meli-com-ia (ainda não publicada).
Status: **nada publicado, nada com número real ainda.** Notas só saem da ferramenta depois que a página estiver no ar.

## Regras que valem para todos os criativos

- Link sempre por `l.tiops.com.br/<slug>?o=<origem>`. Criar o slug só quando a página estiver no ar. Origens sugeridas:
  `ig-reels-notadodia`, `ig-reels-caro`, `ig-reels-duelo`, `ig-car-criterio-<n>`, `yt-shorts-<tema>`.
- A nota **não é IA**: são critérios objetivos, os mesmos da extensão do Chrome. Nunca escrever "a IA analisou seu anúncio". O slug "com-ia" é decisão de marketing, o texto do criativo não afirma isso.
- Números de produto só de `meli-oauth-buddy/docs/sistema.json`. Nunca "260 actions" (são 1.000+ ferramentas) nem "R$ 49,90" (é R$ 99,90 no Starter PRO).
- CTA padrão: "Saiba mais" / "Cole o link do seu anúncio". Nunca "teste grátis".
- Os 8 critérios (nome exato): descrição, imagens, SEO, especificações, benefícios, estrutura, itens inclusos, confiança.
- Diferencial: outros avaliadores mostram 4 barras (reputação, título, preço, imagem); a nossa tem 8 e ordena os pontos fracos do que mais atrapalha ao que menos atrapalha. Não citar o concorrente pelo nome no criativo.

## Formato 1 — "Nota do dia" (Reels/Shorts ~20 s; produção zero)

Gancho (0–2 s, legenda grande na capa): **"MAIS VENDIDO DE [CATEGORIA]: NOTA [XX]"**
1. Tela: link colado no avaliador, anúncio aparece no celular com a identidade do ML.
2. Nota surge + 8 barras enchendo. Voz: "O mais vendido de [categoria] tira [XX]. Olha onde ele perde ponto."
3. Zoom no pior critério + a ordem dos pontos fracos.
4. Fecho: "Cole o link do seu anúncio e veja a sua nota. Link na bio."
Frequência: 1 por dia útil vira série. Categoria escolhida por engajamento anterior.

## Formato 2 — Anúncio caro com nota baixa (Reels ~25 s)

Gancho provisório: **"R$ 7.714 E A NOTA É [XX]"** (o "pior ponto" só sai da nota real; o anúncio tem 12 imagens, então imagem pode nem ser o gargalo).
Exemplo indicado pelo Itamar: PC gamer RTX 5060 / Ryzen 7 5700x.
⚠️ **Anúncio de terceiro (PC gamer), decisão relatada pelo DEV como do Itamar; confirmar com ele direto antes de publicar.** Regras de segurança que aplico de qualquer forma: não citar a loja nem o nome do vendedor, não linkar o anúncio, não mostrar o nome da loja na tela. A crítica é ao padrão, não à loja. Anúncio próprio da Tiops: DEV diz que o Itamar proibiu; usar só se ele liberar.
Dados lidos pelo DEV (não usar sem a nota real): R$ 7.714 (de R$ 18.199,56, 57% OFF), 12 imagens, descrição longa com blocos de "====" e CTA que manda o comprador sair do anúncio.
**Nota do anúncio: ainda não existe.** Não inventar número. O DEV manda o anúncio lido e a nota quando a página subir; conferir na extensão antes.

## Formato 3 — Duelo (Reels ~30 s)

Gancho: **"SEU ANÚNCIO x O LÍDER DA CATEGORIA"**
Lado a lado, 8 barras, quem ganha em cada critério, e o critério em que o líder perde.
Mesmo cuidado do formato 2 para o anúncio de terceiro (sem loja, sem vendedor, sem link). O "seu" anúncio de demonstração depende da decisão do Itamar (anúncio próprio está vetado por ele, segundo o DEV).

## Formato 4 — Série "o que os 8 critérios pegam que os 4 não pegam" (carrossel, 8 posts)

Um critério por post, 6–8 slides cada, padrão dos carrosséis A/B/C (1080x1350, paleta creme/tinta/amarelo).
Ordem sugerida (mais visual → mais técnico): 1 imagens · 2 descrição · 3 especificações · 4 benefícios · 5 itens inclusos · 6 estrutura · 7 SEO · 8 confiança.
Slide 1: pergunta ("Seu anúncio diz o que vem na caixa?"). Meio: exemplo bom x ruim. Último: "Veja sua nota nos 8 critérios. Link na bio."

## Referência do concorrente (enviada pelo Itamar em 2026-09-20)

Landing e criativo do Reels do concorrente, lidos dos prints:
- Landing: 4 barras (reputação, título, preço, imagem principal), nota única de exemplo "62/100", campo para colar o link, botão "Receber meu diagnóstico". Selo "análise gratuita".
- Criativo de anúncio no Instagram: celular com a página do anúncio e 3 medidores (imagem principal, clips, título), headline dirigida ao vendedor, botão "Descubra com um diagnóstico gratuito", botão "Saiba mais".
- Incoerência deles: a landing mede reputação/título/preço/imagem, o criativo mede imagem/clips/título. Não citar o nome deles nem atacar; só mostrar a nossa completude.
- Nossa vantagem, a mostrar de forma visual: 8 critérios em vez de 3–4, pontos fracos ordenados, sem login. "Mesma nota da extensão" só depois de conferir.
- Rascunho de layout: `rascunho-criativo-8-criterios.png` (1080x1350, dados de teste do anúncio da Tiops informados pelo DEV, marca "RASCUNHO"; textos como "Muito a melhorar" são provisórios e devem seguir o texto real da página).

## Estrutura de produção (reaproveita o que já existe)

- Composição Remotion "Corte" (capa com legenda grande, logos, motions, CTA "SAIBA MAIS") serve de base; trocar o clipe de origem por gravação de tela da página.
- Precisa do DEV: prints/gravação da página no ar, com o anúncio dentro do celular. Aguardar.
- Prova pública: gravar uma vez o mesmo anúncio na extensão e na página batendo a nota. **Só afirmar "é a mesma nota" depois de conferir eu mesmo** (hoje é só palavra do briefing).

## Pendências

- [ ] Página no ar (card 143) + prints do DEV
- [ ] Itamar decide formatos 2 e 3 (anúncio de terceiro)
- [ ] Conferir extensão x página com o mesmo anúncio
- [ ] Criar links curtos com `?o=` por criativo
- [ ] Card no Board de Tarefas (produto redes sociais) — criar quando o Itamar confirmar prioridade
