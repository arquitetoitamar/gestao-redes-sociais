#!/bin/bash
# Baixa só o áudio dos vídeos curtos do canal e transcreve (whisper local).
cd "$(dirname "$0")/audio"
for id in fjrfmhMUD4M IiPvKDJ0gMo JE30Znavx_I e6YZbIU3oK8 So23jhRR900 LtifaBOjLRQ -sjtfEfCekY 5kOc1fDD0RM LlmvXuEu4F0; do
  [ -s "$id.wav" ] || { yt-dlp -q --no-warnings -f bestaudio -x --audio-format wav --postprocessor-args "ffmpeg:-ar 16000 -ac 1" -o "$id.%(ext)s" -- "https://www.youtube.com/watch?v=$id" || { echo "falhou $id"; continue; }; }
  [ -s "$id.json" ] || whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin -l pt -f "$id.wav" -oj -osrt -of "$id" -np >/dev/null 2>&1
  echo "$id $(ffprobe -v error -show_entries format=duration -of csv=p=0 $id.wav | cut -d. -f1)s $(grep -c -- '-->' $id.srt) falas"
done
echo FIM
