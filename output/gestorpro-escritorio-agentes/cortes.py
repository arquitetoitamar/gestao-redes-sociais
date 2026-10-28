#!/usr/bin/env python3
"""Roteiro de cortes da gravação do GestorPro.

- Fala fica inteira e o vídeo todo vai 1,2x (atempo, sem mudar o tom).
- Pausas entre falas encurtam: até 1,2 s viram 0,28 s; maiores viram
  timelapse (1/5 da duração, entre 0,4 e 0,9 s). O áudio da pausa é o próprio
  ambiente da gravação, só mais curto.
- Saem a frase com o nome da compradora ("...no caso, a Cláudia") e o nome
  "Fernando" lido da mensagem.

Gera trab/segmentos.json ([c0, c1, s0, s1] no tempo compacto/bruto) e
trab/fala.wav (48 kHz, já acelerado). FAT é o fator final.
"""
import json, os, subprocess
import numpy as np
from scipy.io import wavfile

AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, 'trab')
FAT = 1.2
SR = 48000


def tokens():
    d = json.load(open(os.path.join(T, 'palavras.json')))
    ws = []
    for s in d['transcription']:
        t = s['text'].strip()
        if t:
            ws.append([s['offsets']['from'] / 1000, s['offsets']['to'] / 1000, t])
    return ws


def remover(ws):
    """Tira trechos com nome de comprador (do fim do token anterior ao início do seguinte)."""
    tira = []
    for i, (a, b, t) in enumerate(ws):
        if t.startswith('Cláudia'):
            j = i
            while not ws[j][2].startswith('Para'):
                j -= 1
            tira.append((ws[j - 1][1] + 0.05, ws[i + 1][0] - 0.02))
        if t.startswith('Fernando'):
            tira.append((ws[i - 1][1] + 0.03, ws[i + 1][0] - 0.02))
    return tira


def main():
    ws = tokens()
    tira = remover(ws)
    print('removidos:', [(round(a, 2), round(b, 2)) for a, b in tira])
    ws = [w for w in ws if not any(a <= (w[0] + w[1]) / 2 <= b for a, b in tira)]
    # blocos de fala: tokens com pausa <= 0,35 s ficam juntos
    blocos = []
    for a, b, _ in ws:
        if blocos and a - blocos[-1][1] <= 0.35 and not any(blocos[-1][1] <= x <= a for x, _ in tira):
            blocos[-1][1] = b
        else:
            blocos.append([a, b])
    # folga: whisper costuma marcar o fim um pouco cedo
    for i, bl in enumerate(blocos):
        ini = max(0.0, bl[0] - 0.06)
        fim = bl[1] + 0.12
        if i + 1 < len(blocos):
            fim = min(fim, blocos[i + 1][0] - 0.06)
        if i > 0:
            ini = max(ini, blocos[i - 1][1])
        bl[0], bl[1] = ini, fim

    sr, x = wavfile.read(os.path.join(T, 'audio48.wav'))
    x = x.astype(np.float32)
    seg, partes, c = [], [], 0.0
    xf = int(0.012 * SR)
    rampa = np.linspace(0, 1, xf, dtype=np.float32)

    def peca(s0, dur_src, dur_c):
        i0 = int(s0 * SR)
        p = x[i0:i0 + int(dur_c * SR)].copy()
        if len(p) > 2 * xf:
            p[:xf] *= rampa
            p[-xf:] *= rampa[::-1]
        return p

    for i, (a, b) in enumerate(blocos):
        if i > 0:
            g = a - blocos[i - 1][1]
            if g > 0.02:
                gc = 0.28 if g < 1.2 else min(0.9, max(0.4, g / 5))
                gc = min(gc, g)
                seg.append([c, c + gc, blocos[i - 1][1], a])
                partes.append(peca(blocos[i - 1][1], g, gc))
                c += gc
        seg.append([c, c + (b - a), a, b])
        partes.append(peca(a, b - a, b - a))
        c += b - a
    y = np.concatenate(partes)
    wavfile.write(os.path.join(T, 'fala_compacta.wav'), SR, y.astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(T, 'fala_compacta.wav'),
                    '-af', 'atempo=%.3f' % FAT, '-ar', str(SR), os.path.join(T, 'fala.wav')], check=True)
    json.dump({'fat': FAT, 'seg': seg, 'tira': tira}, open(os.path.join(T, 'segmentos.json'), 'w'))
    print('blocos %d, compacto %.1f s, final %.1f s' % (len(blocos), c, c / FAT))


if __name__ == '__main__':
    main()
