#!/bin/bash
# Tudo vira 1920x1080 30fps h264 + aac 48k estéreo, pra concat sem recodificar depois.
set -e
cd "$(dirname "$0")"
mkdir -p norm

larg() { # paisagem: encaixa com barras
  ffmpeg -v error -stats -i "$2" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p" \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
    -c:v h264_videotoolbox -b:v 10M -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -movflags +faststart "norm/$1.mp4" -y
}

retr() { # retrato: fundo borrado + vídeo centralizado
  ffmpeg -v error -stats -i "$2" \
    -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=28:3,eq=brightness=-0.14:saturation=0.7[bg];[0:v]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,fps=30,format=yuv420p[v]" \
    -map "[v]" -map 0:a \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
    -c:v h264_videotoolbox -b:v 10M -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -movflags +faststart "norm/$1.mp4" -y
}

larg 01-3866 "/Users/itamar/Downloads/IMG_3866.MOV"
larg 02-3867 "/Users/itamar/Downloads/Fotos do iCloud de Itamar Silva rocha dos santos/IMG_3867.MOV"
retr 03-3868 "/Users/itamar/Downloads/Fotos do iCloud de Itamar Silva rocha dos santos 2/IMG_3868.MOV"
retr 04-4293 "/Users/itamar/Downloads/IMG_4293.MOV"
echo NORMALIZADO
