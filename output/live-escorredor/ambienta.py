"""Gera as camadas de ambiente da live (rodar uma vez; monta.sh usa o resultado).
- trab/sfx-unidade.wav: tilintares de prato/talher sincronizados com trab/unidade.mp4 (39,9167 s)
- trab/ambiente-loop.wav: ruído de cozinha (ElevenLabs SFX) em loop sem emenda
Tempos dos toques medidos nos quadros dos clipes (mão encosta no escorredor)."""
import subprocess, os
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
SR = 48000
UNIDADE = 39.916667          # duração de trab/unidade.mp4
S = 'audio/sfx'

def run(*a): subprocess.run([FF, '-v', 'error', '-y', *a], check=True)

# 1) recorta cada tilintar (com 50 ms antes do ataque) e normaliza o pico em -20 dBFS (sox)
cortes = {'prato': ('prato.mp3', 0.66, 0.80), 'talher1': ('talher.mp3', 0.30, 0.45), 'talher2': ('talher.mp3', 2.00, 0.45)}
for nome, (arq, ini, dur) in cortes.items():
    run('-ss', str(ini), '-t', str(dur), '-i', f'{S}/{arq}', '-af',
        f'aresample={SR},aformat=channel_layouts=mono,afade=t=out:st={dur-0.12}:d=0.12',
        '-ar', str(SR), f'trab/hit-{nome}-bruto.wav')
    subprocess.run(['sox', f'trab/hit-{nome}-bruto.wav', f'trab/hit-{nome}.wav', 'gain', '-n', '-20'], check=True)
    os.remove(f'trab/hit-{nome}-bruto.wav')

# 2) toques ao longo da unidade: ida do prato, volta do prato (reverso), ida do talher, volta do talher
#    (tempo na unidade, som, ganho dB). Tirar o prato soa mais leve que encaixar.
eventos = [(1.76, 'prato', -6), (5.86, 'prato', 0), (14.06, 'prato', 0), (18.16, 'prato', -6),
           (22.08, 'talher1', -3), (24.68, 'talher2', 0), (25.98, 'talher1', -3), (28.18, 'talher2', 0),
           (31.58, 'talher2', 0), (33.78, 'talher1', -3), (35.08, 'talher2', 0), (37.68, 'talher1', -3)]
args, filt = [], []
for i, (t, som, g) in enumerate(eventos):
    args += ['-i', f'trab/hit-{som}.wav']
    ms = max(0, int((t - 0.05) * 1000))
    filt.append(f'[{i}:a]volume={g}dB,adelay={ms}[e{i}]')
n = len(eventos)
filt.append(f'anullsrc=r={SR}:cl=mono,atrim=0:{UNIDADE}[base]')
filt.append('[base]' + ''.join(f'[e{i}]' for i in range(n)) +
            f'amix=inputs={n+1}:normalize=0:duration=first,atrim=0:{UNIDADE},asetpts=N/SR/TB[out]')
run(*args, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ar', str(SR), 'trab/sfx-unidade.wav')

# 3) ambiente: emenda o fim no começo (crossfade de 2 s) e deixa em -40 LUFS
run('-i', f'{S}/ambiente.mp3', '-i', f'{S}/ambiente.mp3', '-filter_complex',
    f'[0:a]aresample={SR},atrim=0:20[a];[1:a]aresample={SR},atrim=20:22,asetpts=PTS-STARTPTS[b];'
    f'[b][a]acrossfade=d=2:c1=tri:c2=tri,aformat=channel_layouts=mono,loudnorm=I=-40:TP=-9[out]',
    '-map', '[out]', '-ar', str(SR), 'trab/ambiente-loop.wav')
for f in ['trab/sfx-unidade.wav', 'trab/ambiente-loop.wav']:
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                       capture_output=True, text=True).stdout.strip()
    print(f, d)
