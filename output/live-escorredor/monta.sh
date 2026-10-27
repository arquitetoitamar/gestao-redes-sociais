#!/bin/bash
# Monta o vídeo de 8 min para a live: loop ida-e-volta dos clipes + fala (2 roteiros).
# Entrada: audio/bloco1..4.wav (ElevenLabs, voz Jessica, eleven_v3 pt), intercalando os 2 roteiros.
# Saída: final/escorredor-live-8min.mp4 (1080x1920, 24 fps).
set -euo pipefail
cd "$(dirname "$0")"
FF=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg   # tem drawtext
ALVO=${ALVO:-480}                              # duração final em segundos

# 1) fala: blocos de ~2 min intercalados (roteiro 1, 2, 1, 2), com 1,2 s de respiro entre eles
#    audio/bloco1..4.wav saem de parte1/parte2 cortados numa pausa entre parágrafos
BLOCOS=(audio/bloco1.wav audio/bloco2.wav audio/bloco3.wav audio/bloco4.wav)
ENTRADAS=(); FILTRO=""; N=0
for b in "${BLOCOS[@]}"; do
  ENTRADAS+=(-i "$b")
  FILTRO+="[$N:a]aresample=48000,aformat=channel_layouts=mono[a$N];"
  N=$((N+1))
done
CADEIA=""
for ((i=0;i<N;i++)); do
  CADEIA+="[a$i]"
  if (( i < N-1 )); then FILTRO+="anullsrc=r=48000:cl=mono,atrim=0:1.2[s$i];"; CADEIA+="[s$i]"; fi
done
FILTRO+="${CADEIA}concat=n=$((2*N-1)):v=0:a=1[f]"
$FF -v error -y "${ENTRADAS[@]}" -filter_complex "$FILTRO" -map "[f]" trab/fala-bruta.wav
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 trab/fala-bruta.wav)
# 2) ajusta a velocidade para fechar em ALVO segundos (só se ficar entre 0.9x e 1.25x)
F=$(python3 -c "d=$D;a=$ALVO;f=d/a;print(f'{f:.4f}' if 0.9<=f<=1.25 else '1.0')")
echo "fala: ${D}s -> atempo ${F}"
$FF -v error -y -i trab/fala-bruta.wav -af "atempo=${F},loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 trab/fala.wav
T=$(ffprobe -v error -show_entries format=duration -of csv=p=0 trab/fala.wav)

# 2b) voz "na cozinha": tira o grave de estúdio, sala pequena (eco curto) como celular perto da boca
sox trab/fala.wav trab/fala-sala.wav highpass 100 lowpass 11000 reverb 25 60 30 0 8 -8

# 3) vídeo: unidade de loop repetida até cobrir a fala + selo discreto de IA
#    áudio: voz na sala + ambiente de cozinha (-40 LUFS) + tilintares sincronizados com o loop
#    (trab/sfx-unidade.wav tem o mesmo tamanho de trab/unidade.mp4; gerar com: python3 ambienta.py)
$FF -v error -y -stream_loop -1 -i trab/unidade.mp4 -i trab/fala-sala.wav \
  -stream_loop -1 -i trab/ambiente-loop.wav -stream_loop -1 -i trab/sfx-unidade.wav -t "$T" \
  -filter_complex "[0:v]drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Conteúdo gerado com IA':fontsize=30:fontcolor=white@0.75:box=1:boxcolor=black@0.35:boxborderw=10:x=36:y=60[v];
    [1:a]aformat=channel_layouts=mono[voz];[2:a]aformat=channel_layouts=mono[amb];[3:a]aformat=channel_layouts=mono,volume=6dB[sfx];
    [voz][amb][sfx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.84:level=disabled[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -r 24 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -ar 48000 -movflags +faststart final/escorredor-live-8min.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 final/escorredor-live-8min.mp4
