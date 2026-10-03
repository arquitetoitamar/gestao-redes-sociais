#!/bin/bash
cd "$(dirname "$0")"
for c in c1 c2 c3 c4; do
  start=$(date +%s)
  npx remotion still src/index.ts Corte out/${c}_cover.png --props=props/${c}.json --frame=62 > /dev/null 2>&1
  npx remotion render src/index.ts Corte out/${c}.mp4 --props=props/${c}.json --codec=h264 --crf=18 --pixel-format=yuv420p > out/${c}_render.log 2>&1
  echo "$c done in $(( $(date +%s) - start ))s exit=$?" >> out/render_status.txt
done
echo ALL_DONE >> out/render_status.txt
