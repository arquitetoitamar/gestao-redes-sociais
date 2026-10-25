# Off-topic: "Comprei uma casa nova" — 25/10/2026

**Publicado não listado:** https://www.youtube.com/watch?v=KdC30SOwoB4 (`KdC30SOwoB4`)

Vlog pessoal montado com quatro gravações do Itamar, na ordem em que ele mandou,
mais uma abertura de 10 s feita só com quadros dessas mesmas gravações.

## O corte

| Trecho | Fonte | Entra em | Dura |
|---|---|---|---|
| Abertura | montagem dos 4 clipes + `trilha.wav` | 0:00 | 0:10 |
| Casa por dentro | `IMG_3866.MOV` | 0:10 | 1:09 |
| Quintal e piscina | `IMG_3867.MOV` | 1:19 | 1:11 |
| Samuel, Sofia e a mudança | `IMG_3868.MOV` | 2:30 | 0:48 |
| Volta a pé pelo condomínio | `IMG_4293.MOV` | 3:18 | 7:56 |

Final: 11:14 · 1920x1080 · 30 fps · −15,0 LUFS.

**Os quatro clipes são paisagem.** O `ffprobe` mostra 2160x3840 em dois deles,
mas eles trazem `rotation=90`, então decodificam em 3840x2160. O tratamento de
retrato em `normaliza.sh` (fundo borrado) acabou sendo inócuo — o vídeo cobre o
quadro inteiro. Fica registrado para ninguém reescrever aquilo achando que está
quebrado.

## A abertura

Dez segundos, cortes no tempo da trilha (96 bpm, 0,625 s por tempo), `zoompan`
dando movimento em cada plano, título em PNG entrando aos 7,3 s.

O Itamar pediu Higgsfield e eu gerei lá uma casa 3D — **ele recusou, com razão:
não era a casa dele**. Ficou o aprendizado: em vídeo pessoal, imagem gerada que
finge ser o assunto real não serve. A abertura passou a sair do próprio material.
(Custou 10 créditos de Higgsfield, descartados.)

## A trilha

`trilha.py` sintetiza a faixa do zero em numpy — Am–F–C–G, 96 bpm, pad de serras
destoadas, baixo, arpejo, bumbo/caixa/chimbal e uma subida de ruído no último
compasso. Nenhuma amostra de terceiro, então não há titular de direito autoral.

Foi por necessidade: o Higgsfield no plano Starter não expõe modelo de música
(`sonilo_music` é restrito ao pipeline de jogos) e não há biblioteca local.

## Transcrição

Gemini está com crédito esgotado (402) e o `whisper` do brew quebra no
`llvmlite`. A saída foi `brew install whisper-cpp` + `ggml-large-v3-turbo`:

```bash
whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo.bin -l pt -f wav/4293.wav -osrt -of tr-4293
```

Os quatro `.srt` estão aqui. Foram eles que deram os capítulos e a descrição.

## O que ficou pendente de decisão do Itamar

1. **O número `168` da fachada aparece legível de 0:10 a 0:25**, e no clipe longo
   ele fala "São José dos Campos". Junto com as ruas do condomínio, vira endereço
   achável. Não mascarei: a câmera se mexe no trecho, então a tarja varreria o
   quadro e estragaria a entrada que ele faz questão de mostrar. E é número de
   casa, não credencial — diferente dos tokens tapados nas aulas.
2. **Samuel e Sofia aparecem e são citados pelo nome.**

Por isso subiu **não listado**. Ele confere e troca para público.

## Duas armadilhas no upload

**Tags.** O YouTube envolve em aspas toda tag que tem espaço, e esses dois
caracteres contam no limite de 500. Contar `len(tag) + 1` dá um número menor e o
upload volta `400 invalidTags`. `textos.py` checa do jeito certo:

```python
_custo = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1
assert _custo <= 500
```

**PUT único de 863 MB morre em broken pipe.** `sobe.py` manda em blocos de 8 MB
(múltiplo de 256 KB, exigência do protocolo) e pergunta ao servidor onde parou
com `Content-Range: bytes */total` — ele responde 308 com o `Range` recebido.
Uma queda custa um bloco. A sessão fica em `.sessao-upload.json` para retomar.

## Refazer

```bash
./normaliza.sh      # os 4 originais -> norm/*.mp4 1080p
./abertura.sh       # abertura.mp4 (precisa de trilha.wav e titulo.png)
./junta.sh          # final.mp4
python3 sobe.py unlisted
```

`titulo.py` e `trilha.py` geram `titulo.png` e `trilha.wav`. O ffmpeg desta
máquina **não tem drawtext nem libass** — todo texto é PNG composto com `overlay`.
