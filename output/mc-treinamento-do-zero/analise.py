#!/usr/bin/env python3
"""Mapa de atividade da gravação de tela, para o zoom seguir a ação.

Lê o bruto a 10 fps em 480x270 (cinza), ignora o balão da câmera e mede,
entre quadros vizinhos, quanto da tela mudou e onde (caixa e centro).
Gera trab/atividade.json: [[t, fração, cx, cy, x0, y0, x1, y1], ...] em
coordenadas do vídeo cheio (1920x1080).
"""
import json, os, subprocess, sys
import numpy as np, cv2

AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, 'trab')
SRC = os.path.join(AQUI, 'videos', 'bruto.mp4')
W, H = 1920, 1080
w, h = 480, 270
K = W / w


SCREEN = (63, 75, 1648, 966)     # tela gravada dentro do quadro do Vids
CAM = (1612, 772, 1876, 1036)      # balão da câmera


def main(cam=CAM):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-vf', 'fps=10,scale=%d:%d' % (w, h),
                          '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
    mask = np.zeros((h, w), np.uint8)
    sx0, sy0, sx1, sy1 = [int(v / K) for v in SCREEN]
    mask[sy0 + 1:sy1 - 1, sx0 + 1:sx1 - 1] = 1
    if cam:
        x0, y0, x1, y1 = [int(v / K) for v in cam]
        mask[max(0, y0 - 3):y1 + 3, max(0, x0 - 3):x1 + 3] = 0
    ant, out, n = None, [], 0
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h:
            break
        g = np.frombuffer(b, np.uint8).reshape(h, w)
        if ant is not None:
            d = (cv2.absdiff(g, ant) > 18).astype(np.uint8) & mask
            d = cv2.morphologyEx(d, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
            fr = float(d.mean())
            if fr > 0:
                ys, xs = np.nonzero(d)
                out.append([round(n / 10, 2), round(fr, 5), round(float(xs.mean()) * K), round(float(ys.mean()) * K),
                            int(xs.min() * K), int(ys.min() * K), int((xs.max() + 1) * K), int((ys.max() + 1) * K)])
            else:
                out.append([round(n / 10, 2), 0.0, 0, 0, 0, 0, 0, 0])
        ant = g
        n += 1
    json.dump(out, open(os.path.join(T, 'atividade.json'), 'w'))
    print('amostras', len(out), 'duração %.1f s' % (n / 10))


if __name__ == '__main__':
    main()
