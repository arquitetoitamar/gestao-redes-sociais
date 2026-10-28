# Escritório de Agentes no Mercado Livre (YouTube, 28/10/2026)

Gravação de tela do GestorPro feita no Google Vids ("Demonstraçao Gestorpro", exportada em
`Meu Drive/Exportações do Vids/`), editada e publicada como vídeo público no canal Itamar Rocha.

## Pipeline (rodar nesta ordem)
1. `cortes.py`: corta pausas, acelera a fala 1,2x (atempo) e tira os nomes de compradores lidos em voz alta → `trab/segmentos.json`, `trab/fala.wav`.
2. `vocab.py` + `ocr.py`: OCR (tesseract, eng) a cada 6 quadros → `trab/ocr/*.json` com as palavras lidas.
3. `audio.py`: abertura + voz (-16 LUFS, só ganho e limitador) + whoosh + trilha na cartela final → `trab/audio_final.wav`.
4. `render.py`: monta abertura + miolo + cartela → `videos/final.mp4`. Use `render.py teste <ini> <fim>` ou `render.py quadros t1,t2` para conferir.
5. `auditoria.py`: OCR no vídeo final procurando texto legível que não seja rótulo do app.
6. `publica.py texto|sobe`: título, descrição com capítulos, tags, idioma, local e thumb.

## Privacidade (por que o desfoque é "à prova de falha")
A janela do navegador inteira fica desfocada por padrão. Só voltam nítidos:
- linhas que o OCR leu e em que TODAS as palavras estão no vocabulário de rótulos do app
  (`vocab.py`: strings do front do gestor-pro, sem comentários, com nomes de pessoa/loja/produto bloqueados), sem dígitos;
- e só se o quadro não mudou desde a leitura do OCR (rolagem volta a desfocar);
- a ilustração do escritório (achada por template) e o balão da câmera.
O que o OCR não ler continua desfocado. A gravação original tinha nome completo, endereço, CEP e
valores de compra de compradores, faturamento e margem da loja e o ID do comprador na URL.

## Peças
- `abertura/`: abertura nova (cenas da Imersão + insights + trilha eletrônica feita em Python).
- `broll.py` → `videos/broll/`: 8 animações (robô, recomendação, WhatsApp, contestação, banda de margem, promoção, cérebro, dia inteiro).
- `videos/lat/`: 7 s de 5 verticais da Imersão para o painel lateral.
- `thumb.jpg` (Higgsfield, gpt_image_2_5 com foto real de referência), `thumb-alt-1.jpg`, `prompt_thumb.md`.

Vídeos e WAVs ficam fora do git (`.gitignore`).
