"""Rolagem vertical da janela do Claude, quadro a quadro, para arrastar as caixas de desfoque junto com o texto.

uso: python3 rolagem.py  -> trab/rolagem.json  {"<quadro>": [dy, x0, y0, x1, y1]}
dy = quanto o conteúdo desceu (px do bruto) do quadro anterior para este; caixa = janela escura daquele segundo.
"""
import json, os, subprocess
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
T = lambda *p: os.path.join(AQUI, 'trab', *p)
FPS = 30
jan = json.load(open(T('janela_escura.json')))          # [(segundo, caixa|None)]
por_seg = {t: b for t, b in jan if b}

# trechos com janela escura (com 1 s de folga)
segs = []
for t in sorted(por_seg):
    if segs and t - segs[-1][1] <= 2:
        segs[-1][1] = t
    else:
        segs.append([t, t])
segs = [(max(0, a - 1), b + 2) for a, b in segs if b - a >= 2]

saida = {}
for a, b in segs:
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', T('bruto.mp4'),
                          '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
    ant, f = None, round(a * FPS)
    while True:
        buf = p.stdout.read(1920 * 1080)
        if len(buf) < 1920 * 1080:
            break
        g = np.frombuffer(buf, np.uint8).reshape(1080, 1920)
        cx = por_seg.get(int(f / FPS)) or por_seg.get(int(f / FPS) - 1) or por_seg.get(int(f / FPS) + 1)
        if cx:
            x0, y0, x1, y1 = cx
            r = g[y0 + 60:y1 - 60, x0 + 40:x1 - 40]
            dy = 0.0
            if ant is not None and ant.shape == r.shape:
                # faixa do meio do quadro anterior procurada no atual: aguenta rolagem grande
                h = r.shape[0]
                melhor = (0, 0)
                for yc in (h // 2, h // 4, 3 * h // 4):
                    faixa = ant[max(0, yc - 50):yc + 50]
                    if faixa.std() < 8:                       # faixa vazia não serve de referência
                        continue
                    res = cv2.matchTemplate(r, faixa, cv2.TM_CCOEFF_NORMED)
                    _, mx, _, (_, yy) = cv2.minMaxLoc(res)
                    if mx > melhor[0]:
                        melhor = (mx, yy - max(0, yc - 50))
                if melhor[0] > 0.85:
                    dy = float(melhor[1])
            saida[str(f)] = [round(dy, 1), x0, y0, x1, y1]
            ant = r
        else:
            ant = None
        f += 1
    p.wait()
json.dump(saida, open(T('rolagem.json'), 'w'))
mov = sum(1 for v in saida.values() if abs(v[0]) >= 1)
print('quadros', len(saida), '| com rolagem', mov)
