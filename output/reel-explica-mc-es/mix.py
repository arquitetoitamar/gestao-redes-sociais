"""Mixa narração (nos instantes da timeline) + trilha com abaixamento sob a voz.
uso: python3 mix.py <variante> <saida.wav>   (usa build/timeline.json e audio/musica.wav atuais)"""
import json, subprocess, sys
V, OUT = sys.argv[1], sys.argv[2]
TL = json.load(open('build/timeline.json'))
cenas = [s for s in TL['scenes'] if s['kind'] == 'scene']
args, filt = ['ffmpeg', '-v', 'error', '-y'], []
for i, s in enumerate(cenas):
    args += ['-i', f"audio_{V}/{s['narr']}.wav"]
    ms = int(round(s['nstart'] * 1000))
    filt.append(f"[{i}:a]adelay={ms}|{ms},apad[a{i}]")
args += ['-i', 'audio/musica.wav']
m = len(cenas)
filt.append(''.join(f'[a{i}]' for i in range(m)) + f"amix=inputs={m}:normalize=0:duration=longest,atrim=0:{TL['total'] + 0.3},"
            "aformat=channel_layouts=stereo,asplit=2[voz][sc]")
filt.append(f"[{m}:a]volume=0.32[mus]")
filt.append("[mus][sc]sidechaincompress=threshold=0.02:ratio=5:attack=15:release=350[musd]")
filt.append(f"[voz][musd]amix=inputs=2:normalize=0:duration=first,atrim=0:{TL['total'] + 0.3},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000")
args += ['-filter_complex', ';'.join(filt), '-ac', '2', OUT]
subprocess.run(args, check=True)
print('mix ok', OUT)
