#!/bin/bash
# Abertura de 10s feita SÓ com material do Itamar. Cortes no tempo da trilha
# (96 bpm -> 0.625 s por tempo). zoompan dá o movimento; drawtext não existe
# nesta máquina, então o título é PNG.
set -e
cd "$(dirname "$0")"
rm -rf ab && mkdir ab

# fonte  início  duração  direção-do-zoom
corte() { # $1 saída $2 arquivo $3 ss $4 t $5 in|out
  if [ "$5" = in ]; then
    Z="z='min(zoom+0.0012,1.18)'"
  else
    Z="z='if(lte(zoom,1.0),1.18,max(1.001,zoom-0.0012))'"
  fi
  ffmpeg -v error -ss "$3" -t "$4" -i "$2" \
    -vf "zoompan=$Z:d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,format=yuv420p" \
    -an -c:v h264_videotoolbox -b:v 12M "ab/$1.mp4" -y
}

corte 00 norm/01-3866.mp4 1.5  2.500 in    # rua do condomínio, abre devagar
corte 01 norm/01-3866.mp4 6.2  0.625 out   # a fachada
corte 02 norm/01-3866.mp4 11.3 0.625 in    # a Sofia na porta
corte 03 norm/02-3867.mp4 14.5 0.625 out   # o quintal
corte 04 norm/02-3867.mp4 46.0 0.625 in    # a piscina
corte 05 norm/03-3868.mp4 15.0  0.625 out   # ele e o Samuel
corte 06 norm/01-3866.mp4 59.0 0.625 in    # a bancada
corte 07 norm/04-4293.mp4 118  0.625 out   # ele andando no condomínio
corte 08 norm/02-3867.mp4 26.5 0.625 in    # as portas de vidro
corte 09 norm/01-3866.mp4 35.5 2.500 in    # interior, segura pro título

: > ab/lista.txt
for i in 00 01 02 03 04 05 06 07 08 09; do echo "file '$i.mp4'" >> ab/lista.txt; done
ffmpeg -v error -f concat -safe 0 -i ab/lista.txt -c copy ab/corte.mp4 -y

# título entra em 7.3s e segura até o fim
ffmpeg -v error -i ab/corte.mp4 -loop 1 -i titulo.png -i trilha.wav \
  -filter_complex "[1:v]format=rgba,fade=t=in:st=7.3:d=0.5:alpha=1[tt];[0:v][tt]overlay=0:0:shortest=1,fade=t=in:st=0:d=0.6[v]" \
  -map "[v]" -map 2:a -t 10 \
  -c:v h264_videotoolbox -b:v 12M -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart abertura.mp4 -y
ffprobe -v error -show_entries format=duration -of csv=p=0 abertura.mp4
echo ABERTURA-OK
