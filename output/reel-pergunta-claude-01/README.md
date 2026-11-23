# Reel "Pergunta pro Claude" #1 (23/11/2026)

Série baseada em `output/criativos-dores-mercado-livre/analise.md`. Roteiro 1: anúncio com visita e sem venda.
Status: RASCUNHO — aguardando aprovação do Itamar. Não publicar antes do "sim".

- Narração: `narracao.txt`, voz clonada HeyGen c463ef5b (TTS ~40 s, ~US$ 0,12).
- Animação: `motion.html` (cenas por tempo de palavra, `cronograma.py` → `trab/cronograma.json`), `motion.py todos 4` → `trab/mot/`.
- Áudio: `audio.py` (voz + sala + trilha sintetizada com ducking + efeitos da pasta media-use).
- Montagem: `ffmpeg -framerate 30 -i trab/mot/m_%05d.jpg -i trab/audio_final.wav ... videos/reel_pergunta_claude_01.mp4` (40,6 s, 1080x1920).
- Dados na tela são de exemplo (marcado "valores de exemplo"); nenhuma loja real.
- CTA: CONNECT (automação global do ManyChat).
