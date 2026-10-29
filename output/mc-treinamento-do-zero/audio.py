#!/usr/bin/env python3
"""Áudio final: abertura (trilha) + voz acelerada (só ganho até -16 LUFS, sem EQ
nem redução de ruído) + efeitos curtos nos motions (whoosh, pop, ding, moeda)
+ trilha baixa na cartela final. Gera trab/audio_final.wav (48 kHz estéreo)."""
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


def loudnorm(caminho, alvo=-16):
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', caminho, '-af',
                        'loudnorm=I=%d:TP=-1.5:LRA=11:print_format=json' % alvo, '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    f = ('loudnorm=I=%d:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:'
         'offset=%s:linear=true' % (alvo, j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
    return ler(caminho, ('-af', f))


def whoosh(dur=0.55, sobe=True, ganho=0.15):
    n = int(dur * SR)
    x = np.random.default_rng(3).standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n)
    out = np.zeros(n, np.float32)
    for k in range(8):
        a, b = int(k * n / 8), int((k + 1) * n / 8)
        e = k if sobe else 7 - k
        fc = 300 * (12 ** (e / 7))
        sos = butter(2, [fc * 0.7, min(fc * 1.4, 20000)], 'bandpass', fs=SR, output='sos')
        out[a:b] = sosfilt(sos, x)[a:b]
    out *= np.sin(np.pi * t) ** 2
    out /= np.max(np.abs(out)) + 1e-9
    return out * ganho


def tom(freqs, dur, ganho, decai=18.0, harm=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    seg = n // len(freqs)
    for i, fq in enumerate(freqs):
        a = i * seg
        tt = t[:n - a]
        s = np.sin(2 * np.pi * fq * tt) + harm * np.sin(2 * np.pi * fq * 2 * tt)
        s *= np.exp(-tt * decai)
        out[a:] += s.astype(np.float32)
    ataque = np.minimum(1, t / 0.004)
    out *= ataque
    out /= np.max(np.abs(out)) + 1e-9
    return out * ganho


SONS = {
    'whoosh': whoosh(0.55, True, 0.15),
    'whoosh_baixo': whoosh(0.45, False, 0.08),
    'pop': tom([660, 990], 0.12, 0.07, decai=40),
    'ding': tom([1318], 0.35, 0.05, decai=12),
    'moeda': tom([988, 1319], 0.32, 0.10, decai=10, harm=0.4),
}


def main():
    tempos = json.load(open(os.path.join(T, 'tempos.json')))
    ab = loudnorm(os.path.join(V, 'abertura.mp4'))
    nab = int(round(tempos['abertura_s'] * FPS))
    L_ab = int(nab / FPS * SR)
    ab = np.pad(ab, ((0, max(0, L_ab - len(ab))), (0, 0)))[:L_ab]
    fala = loudnorm(os.path.join(T, 'fala.wav'))
    L = int(round(tempos['miolo_q'] / FPS * SR))
    fala = np.pad(fala, ((0, max(0, L - len(fala))), (0, 0)))[:L]
    for t, nome in json.load(open(os.path.join(T, 'sfx.json'))):
        s = SONS[nome]
        i = int(max(0, t) * SR)
        seg = fala[i:i + len(s)]
        seg += s[:len(seg), None]
    tr = ler(os.path.join(AQUI, 'abertura', 'trilha.wav'))
    fim_d = tempos['final_s']
    fim = tr[int(8.0 * SR):int(12.0 * SR)]
    fim = np.concatenate([fim] * int(np.ceil(fim_d * SR / len(fim))))[:int(fim_d * SR)] * 0.35
    rampa = np.linspace(0, 1, int(0.4 * SR))[:, None]
    fim[:len(rampa)] *= rampa
    fim[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))[:, None]
    y = np.clip(np.concatenate([ab, fala, fim]), -0.89, 0.89)
    wavfile.write(os.path.join(T, 'audio_final.wav'), SR, y.astype(np.float32))
    print('abertura %.2f s, miolo %.2f s, final %.1f s, total %.1f s' % (nab / FPS, L / SR, fim_d, len(y) / SR))


if __name__ == '__main__':
    main()
