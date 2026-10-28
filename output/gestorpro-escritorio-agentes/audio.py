#!/usr/bin/env python3
"""Áudio final: abertura (trilha) + voz acelerada (só ganho até -16 LUFS e
limitador, sem EQ nem redução de ruído) + whoosh na entrada dos painéis +
trilha baixa na cartela final. Gera trab/audio_final.wav (48 kHz estéreo)."""
import json, os, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, 'trab')
V = os.path.join(AQUI, 'videos')
SR = 48000
FPS = 30


def ler(caminho, extra=()):
    tmp = os.path.join(T, '_tmp.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', caminho, *extra, '-ar', str(SR), '-ac', '2',
                    '-c:a', 'pcm_f32le', tmp], check=True)
    sr, x = wavfile.read(tmp)
    os.remove(tmp)
    return x.astype(np.float32)


def loudnorm(caminho):
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', caminho, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    f = ('loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:'
         'offset=%s:linear=true' % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
    return ler(caminho, ('-af', f))


def whoosh(dur=0.55):
    n = int(dur * SR)
    rng = np.random.default_rng(3)
    x = rng.standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n)
    out = np.zeros(n, np.float32)
    for k in range(8):                      # varredura de passa-banda subindo
        a, b = int(k * n / 8), int((k + 1) * n / 8)
        fc = 300 * (12 ** (k / 7))
        sos = butter(2, [fc * 0.7, min(fc * 1.4, 20000)], 'bandpass', fs=SR, output='sos')
        out[a:b] = sosfilt(sos, x)[a:b]
    env = np.sin(np.pi * t) ** 2
    out = out * env
    out /= np.max(np.abs(out)) + 1e-9
    return np.stack([out, out], 1) * 0.16


def main():
    import render
    ab = loudnorm(os.path.join(V, 'abertura.mp4'))
    nab = int(round(len(ab) / SR * FPS))
    ab = np.pad(ab, ((0, max(0, int(nab / FPS * SR) - len(ab))), (0, 0)))[:int(nab / FPS * SR)]
    fala = loudnorm(os.path.join(T, 'fala.wav'))
    n_mio = int(render.DUR * FPS)
    L = int(n_mio / FPS * SR)
    fala = np.pad(fala, ((0, max(0, L - len(fala))), (0, 0)))[:L]
    w = whoosh()
    cam = render.Camadas()
    momentos = [b[0] for b in cam.broll] + [l[0] for l in cam.lat] + [l[0] + render.LAT_DUR - 0.45 for l in cam.lat]
    for t in momentos:
        i = int(max(0, t - 0.25) * SR)
        seg = fala[i:i + len(w)]
        seg += w[:len(seg)]
    tr = ler(os.path.join(AQUI, 'abertura', 'trilha.wav'))
    fim = tr[int(8.0 * SR):int(12.0 * SR)]
    reps = int(np.ceil(render.FINAL_DUR * SR / len(fim)))
    fim = np.concatenate([fim] * reps)[:int(render.FINAL_DUR * SR)] * 0.35
    rampa = np.linspace(0, 1, int(0.4 * SR))[:, None]
    fim[:len(rampa)] *= rampa
    fim[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))[:, None]
    y = np.concatenate([ab, fala, fim])
    y = np.clip(y, -0.89, 0.89)
    wavfile.write(os.path.join(T, 'audio_final.wav'), SR, y.astype(np.float32))
    print('abertura %.2f s, miolo %.2f s, final %.1f s, total %.1f s' % (nab / FPS, n_mio / FPS, render.FINAL_DUR, len(y) / SR))


if __name__ == '__main__':
    main()
