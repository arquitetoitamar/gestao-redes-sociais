# Live TikTok Shop: escorredor 12 pratos inox (vídeo em loop de 8 min)

O produto é o "Escorredor 12 Pratos Em Aço Inox Com Porta Talheres Inox Com Bandeja Coletora Água Preto", vendido pela Lojas Souza (produto 1736878695314719849). Ele é de outro seller, então a API não abre o anúncio. Os dados vieram dos prints, que estão em `ref/`.

A técnica de referência é o vídeo do Pedro Veiga ("Live Shop com IA"); a transcrição está em `ref/transcricao.txt`.

## O que a técnica ensina e o que foi usado

1. Fazer uma foto realista em primeira pessoa do produto, com a mão tocando nele, em 9:16 e sem texto. Saiu em `trab/quadro-inicial.png`, feita com GPT Image 2.5 no Higgsfield a partir das fotos do anúncio.
2. Animar a foto em clipes de 10 s com o Grok, o modelo que o vídeo recomenda. São dois clipes partindo do mesmo quadro: `clipe-prato` (tira o prato e devolve) e `clipe-talher` (tira garfo e colher do porta-talheres e devolve).
3. Montar o loop de ida e volta: o clipe roda para frente e depois ao contrário, nos dois clipes. O resultado é `trab/unidade.mp4`, com 39,9 s, e ele se repete até cobrir a fala. Como os dois clipes começam no mesmo quadro, a emenda não aparece.
4. Fala longa sem repetir: 2 roteiros de ~3.800 caracteres cada, que dão ~8 min, com começos diferentes e perguntas que a própria apresentadora responde. Estão em `roteiros/`.
5. Voz pt-BR do ElevenLabs: Jenifer (`GOkMqfyKMLVUcYfO2WbB`), sotaque do interior de São Paulo, modelo eleven_v3.

## O que ficou de fora da técnica

- **Não clonei a voz de criador do TikTok.** Clonar a voz de alguém sem autorização é problema. Usei uma voz de biblioteca.
- **Os roteiros não inventam nada.** Não dizem preço (mandam conferir no carrinho), não falam em "oferta relâmpago" ou "últimas unidades" e não respondem comentário falso. Tudo vem do anúncio: inox, 12 pratos, porta-talheres, bandeja, encaixe sem solda e mais de 5 mil vendidos.
- **O vídeo tem um selo discreto "Conteúdo gerado com IA".** O TikTok exige rótulo em conteúdo realista gerado por IA. Para tirar, edite o `drawtext` no `monta.sh`.
- **Risco do TikTok:** a regra de LIVE proíbe transmitir conteúdo pré-gravado em loop como se fosse ao vivo. Rodar isso na live arrisca restrição da conta de afiliado. O mesmo vídeo serve sem esse risco como post, anúncio ou vídeo do produto na vitrine.

## Montagem

```bash
# com audio/parte1.mp3 e audio/parte2.mp3 no lugar
./monta.sh            # gera final/escorredor-live-8min.mp4 com 8:00 cravados
```

`monta.sh` junta as duas falas com 1,5 s de respiro e ajusta a velocidade para fechar em 8:00. A variável `ALVO` muda a duração, mas o ajuste só vale entre 0,9x e 1,25x. Em seguida o script repete o loop, normaliza o áudio em -16 LUFS e aplica o selo. Precisa do ffmpeg-full por causa do drawtext.

## Custos (27/10/2026)

- Higgsfield: quadro inicial por 2,75 créditos e 2 clipes Grok de 10 s em 720p por 90. O saldo ficou em ~94,5.
- ElevenLabs: as falas foram geradas no fluxo `QBxXq7wbCfrnYDxFoMN5` (~7,4 mil créditos), mas o conector não deixa baixar. A chave do `.env` não tem as permissões `text_to_speech` e `speech_history_read`.
