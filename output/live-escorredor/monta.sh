#!/bin/bash
# Monta o vídeo de 8 min para a live: loop ida-e-volta dos clipes + fala (2 roteiros).
# Entrada: audio/parte1.mp3 e audio/parte2.mp3 (ElevenLabs, voz Jenifer pt-BR).
# Saída: final/escorredor-live-8min.mp4 (1080x1920, 24 fps).
set -euo pipefail
cd "$(dirname "$0")"
FF=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg   # tem drawtext
ALVO=${ALVO:-480}                              # duração final em segundos

# 1) fala: parte 1 + 1,5 s de respiro + parte 2
$FF -v error -y -i audio/parte1.mp3 -i audio/parte2.mp3 -filter_complex \
  "[0:a]aresample=48000,aformat=channel_layouts=mono[a];[1:a]aresample=48000,aformat=channel_layouts=mono[b];
   anullsrc=r=48000:cl=mono,atrim=0:1.5[s];[a][s][b]concat=n=3:v=0:a=1[f]" -map "[f]" trab/fala-bruta.wav
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 trab/fala-bruta.wav)
# 2) ajusta a velocidade para fechar em ALVO segundos (só se ficar entre 0.9x e 1.25x)
F=$(python3 -c "d=$D;a=$ALVO;f=d/a;print(f'{f:.4f}' if 0.9<=f<=1.25 else '1.0')")
echo "fala: ${D}s -> atempo ${F}"
$FF -v error -y -i trab/fala-bruta.wav -af "atempo=${F},loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 trab/fala.wav
T=$(ffprobe -v error -show_entries format=duration -of csv=p=0 trab/fala.wav)

# 3) vídeo: unidade de loop repetida até cobrir a fala + selo discreto de IA
$FF -v error -y -stream_loop -1 -i trab/unidade.mp4 -i trab/fala.wav -t "$T" \
  -vf "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Conteúdo gerado com IA':fontsize=30:fontcolor=white@0.75:box=1:boxcolor=black@0.35:boxborderw=10:x=36:y=60" \
  -map 0:v -map 1:a -c:v libx264 -preset medium -crf 20 -r 24 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -movflags +faststart final/escorredor-live-8min.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 final/escorredor-live-8min.mp4
