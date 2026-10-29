# Treinamento do Marketplace Connect do zero (YouTube, 29/10/2026)

Gravação de tela no Google Vids ("Trilha gamificada", `Meu Drive/Exportações do Vids/`) mostrando o
Treino MAC: conector de treinamento gamificado do Marketplace Connect rodando no ChatGPT.
Publicado público no canal Itamar Rocha: https://youtu.be/q9O1-xQ4Qm0 (ver `publicado.json`).
O Itamar pediu para não esconder nada da tela.

## Pipeline (rodar nesta ordem)
1. whisper-cli (`-ml 1 -oj`) em `trab/audio16.wav` → `trab/palavras.json`.
2. `cortes.py`: corta pausas, 1,2x (atempo) e os trechos de `TIRA` (tropeço em 222–237 s, gravação travada no fim) → `trab/segmentos.json`, `trab/fala.wav`.
3. `analise.py` (opcional): mapa de onde a tela muda, ajuda a posicionar os zooms.
4. `roteiro.py`: capítulos, zooms, etiquetas, passos, painéis, cartões de tela cheia (tempos no bruto).
5. `abertura/abertura.py render ../videos/abertura.mp4` (mesma abertura do GestorPro, cartela com "TREINAMENTO DO ZERO / MARKETPLACE CONNECT").
6. `render.py sfx` e `render.py` (miolo em 6 processos + cartela final); `render.py quadros t1,t2` para conferir.
7. `audio.py` (voz só com ganho até -16 LUFS + whoosh/pop/moeda nos motions) e `render.py junta` → `videos/final.mp4`.
8. `publica.py texto|sobe`.

Capa: `thumb.jpg`, Higgsfield GPT Image 2.5 com foto real + capa aprovada + tela do jogo como referência.
Vídeos, WAVs e quadros de trabalho foram apagados depois de publicar (o bruto continua no Drive).
