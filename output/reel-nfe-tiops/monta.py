"""Junta narração (cada fala no seu instante), trilha e quadros em reel_nfe_tiops.mp4.
uso: python3 monta.py   (depois de timeline.py, render.py frames e music.py)"""
import json, subprocess
import numpy as np
from scipy.io import wavfile

SR = 48000
TL = json.load(open('build/timeline.json'))
N = int((TL['total'] + 0.3) * SR)
narr = np.zeros(N)
for s in TL['scenes']:
    if s['kind'] != 'scene':
        continue
    sr, x = wavfile.read(f"audio/{s['narr']}.wav")
    assert sr == SR
    x = x.astype(float) / 32768
    i = int(s['nstart'] * SR)
    narr[i:i + len(x)] += x[:N - i]
wavfile.write('audio/narracao_full.wav', SR, (np.clip(narr, -1, 1) * 32767).astype(np.int16))

def ff(*a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)

# cada faixa normalizada numa passada separada (loudnorm encadeado truncou áudio antes)
ff('-i', 'audio/narracao_full.wav', '-af', 'loudnorm=I=-16:TP=-2:LRA=9', '-ar', '48000', '-ac', '2', 'audio/narr_norm.wav')
ff('-i', 'audio/musica.wav', '-af', 'loudnorm=I=-31:TP=-6:LRA=7', '-ar', '48000', 'audio/mus_norm.wav')
# trilha abaixa sob a voz e fecha no volume cheio no fim
ff('-i', 'audio/mus_norm.wav', '-i', 'audio/narr_norm.wav', '-filter_complex',
   '[0][1]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=350[m];[m][1]amix=inputs=2:normalize=0:duration=longest[a]',
   '-map', '[a]', 'audio/mix_pre.wav')
ff('-i', 'audio/mix_pre.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89:level=disabled', '-ar', '48000', 'audio/mix_final.wav')
ff('-framerate', str(TL['fps']), '-i', 'frames/f%05d.jpg', '-i', 'audio/mix_final.wav',
   '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
   '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'reel_nfe_tiops.mp4')
print('ok')
