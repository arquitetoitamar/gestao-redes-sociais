#!/bin/bash
# Junta abertura + os 4 clipes. Todos já estão em 1920x1080 30fps h264/aac,
# então concat sem recodificar — não perde geração nenhuma.
set -e
cd "$(dirname "$0")"
: > lista-final.txt
for p in abertura.mp4 norm/01-3866.mp4 norm/02-3867.mp4 norm/03-3868.mp4 norm/04-4293.mp4; do
  echo "file '$p'" >> lista-final.txt
done
ffmpeg -v error -f concat -safe 0 -i lista-final.txt -c copy -movflags +faststart final.mp4 -y
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_type,codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 final.mp4
