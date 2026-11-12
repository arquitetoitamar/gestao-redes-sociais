# Reels e Shorts: vídeos explicativos do Gemini Notebook (12/11/2026)

Origem: dois vídeos verticais 720x1280 gerados no Gemini Notebook, em `~/Downloads`:
`Como_IAs_Publicam_Anúncios_em_Marketplaces.mp4` (70 s) e `Como_a_IA_Gerencia_Lojas_Sozinha.mp4` (71 s).
Pedido: "crie dois reels e shorts, melhore estes vídeos, remova a máscara do Gemini".

## Saída (`final/`)
| Peça | Reel | Short | Duração |
|---|---|---|---|
| A IA publica seu anúncio por você | `publica-anuncio-reel.mp4` | `publica-anuncio-short.mp4` | 70,4 s |
| Pause no ML e na Shopee com uma frase | `pausa-ml-shopee-reel.mp4` | `pausa-ml-shopee-short.mp4` | 71,1 s |

Reel e Short só mudam no cartão final. Os MP4 do vídeo B têm 15 MB e não vão para o git (limite de 10 MB).

## O que `monta.py` faz
- **Marca "Gemini Notebook"** (canto inferior direito, x 530-695 / y 1239-1253 no quadro original):
  - vídeo A (fundo liso): `delogo`;
  - vídeo B, parte do papel pontilhado: copia o mesmo pedaço de papel 187 px à esquerda (4 colunas de pontos), com borda suavizada;
  - vídeo B, parte do caderno (antes de 13,2 s): `delogo`.
- **Fim morto cortado**: os dois terminavam com ~3 s de "carregando" e tela preta depois da narração.
- **Legenda do Gemini fora do rodapé**: nas cenas em que ela ficava em y ~1700 de 1920 (embaixo do nome e da legenda do Instagram e do título do Shorts), a imagem sobe 140 px no quadro original:
  - vídeo A, a partir de 30,4 s: o fundo escuro é completado esticando a última linha;
  - vídeo B, a partir de 13,2 s: completado com faixas do mesmo papel, na mesma fase dos pontos.
  - As duas trocas de cena são cortes secos, então a subida não aparece.
- **Gancho escrito** nos primeiros 4 s:
  - A: "A IA PUBLICA SEU / ANÚNCIO POR VOCÊ";
  - B: "PAUSE NO ML / E NA SHOPEE / COM UMA FRASE".
- **Cartão final de 3 s**: Marketplace Connect, liga ChatGPT, Claude e Gemini às lojas.
  - Reel: "Comente CONNECT", que dispara a automação já ativa no ManyChat.
  - Short: "Link na descrição" e marketplaces.tiops.com.br.
- **Imagem e áudio**: 1080x1920 a 30 fps; volume em -14 LUFS. A narração é TTS do Gemini, não a voz do Itamar, então a regra de não mexer no áudio não se aplica.

## Transcrição
Feita pelo AWS Transcribe (o modelo do whisper-cpp tinha sumido do cache): `transcricao-*.srt`.

## Conferência
- Folha de contato a cada 5 s, cantos da marca em 6 tempos e os quadros da troca de cena.
- Volume: -14,1 e -13,9 LUFS, pico -1,2 dBFS.
- Resta: no vídeo B, a legenda "Imagine pedir no" aparece 2 quadros (66 ms) na posição antiga antes da troca de cena. Imperceptível.

Textos para publicar em `legendas.md`.
