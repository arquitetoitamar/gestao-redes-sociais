# Instagram @tiopstecnologia: o que dá alcance

Coleta de 27/10/2026, com `python3 coleta.py`. Gera `posts.json` (154 posts com métricas) e `conta.json` (a conta nos últimos 30 dias). A conta tem 812 seguidores.

## Números

| Formato | Posts | Alcance mediano |
|---|---|---|
| Reels | 86 | 124 |
| Carrossel | 16 | 45 |
| Imagem estática | 52 | 30 |

- **Um post fez a conta.** O Reel da extensão do Chrome (14/08, https://www.instagram.com/reel/DcBhQ_sOg0E/) teve 25.710 de alcance, 758 compartilhamentos, 693 salvamentos e 16,6 s de tempo médio assistido. O segundo melhor post teve 1.606.
- **O segundo nível é notícia de tecnologia de fora**: robôs humanoides (1.606) e caminhão autônomo NAVIO (1.512).
- **O resto dos Reels fica entre 100 e 200.**
- **Compartilhar e salvar é o que separa.** Reels com 0 compartilhamentos+salvamentos têm alcance mediano de 90. Com 10 ou mais, a mediana é 1.606.
- **Horário (Reels desde junho, em BRT)**: 16h–19h tem mediana de 148; 20h–23h, 131; 12h–15h, 92; 08h–11h, 58, o pior horário.
- **Dia da semana**: sábado (181), domingo (158) e segunda (220, com só 4 posts) vão melhor que terça (79).
- **"Comenta X" na legenda não muda o alcance**: mediana de 129 com o pedido e 127 sem.
- **Tempo assistido abaixo de 6 s derruba o alcance** (mediana de 100). De 6 s para cima fica entre 130 e 140.

## Conta, últimos 30 dias

- **Alcance de 29.165, sendo 24.830 de anúncio (85%).** Pelo orgânico: Reels 3.340, stories 923, posts 192, carrossel 129.
- **+126 seguidores e −14 que deixaram de seguir.** Os picos de anúncio (6.263 de alcance em 11/10, 3.063 em 25/10) trouxeram 4 seguidores cada. Anúncio dá alcance e quase não dá seguidor.
- **Público**: 35–44 anos é a maior faixa (265), seguida de 25–34 (217). São 71% homens. A cidade de São Paulo tem 140 seguidores.

## O que fazer

1. **Ferramenta útil e grátis é o formato que viraliza.** O viral funcionou porque o gancho falava de algo do próprio seller ("seu anúncio tem nota, você só nunca viu"), listava o que a ferramenta mostra e tirava o risco ("grátis, código aberto, só lê, não mexe em nada"). Repetir isso com outras ferramentas, checklists ou prompts que dê para salvar.
2. **Só Reels.** Imagem estática alcança um quarto do que um Reel alcança.
3. **Postar entre 16h e 20h, de preferência no fim de semana.** Evitar a manhã: o Reel "substituir", da Imersão, saiu às 09:35 de 27/10 e tinha 22 de alcance cinco horas depois.
4. **Notícia de tecnologia de fora** (robôs, autônomos) vale como topo de funil, amarrando no fim com a operação do seller.
5. **Os primeiros segundos precisam segurar.** Abaixo de 6 s de tempo médio, o alcance cai.

Cuidado ao ler: o alcance por post vem da API como ela devolve. A conta tem anúncio rodando, e não deu para confirmar quais posts foram impulsionados porque o token não tem `ads_read`.
