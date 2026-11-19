"""Mapa de atividade da tela (onde os pixels mudam), base do zoom automático.

uso: python3 atividade.py  -> trab/atividade.json  [{"t": s, "caixa": [x0,y0,x1,y1] | null, "area": fração}]
Coordenadas no bruto 1920x1080, só dentro da região da tela (62..1652 x 74..968), sem a câmera.
"""
import json, os, subprocess
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
BRUTO = os.path.join(AQUI, 'trab', 'bruto.mp4')
X0, Y0, W, H = 62, 74, 1590, 894
ESC = 0.5
FPS = 5
w, h = int(W * ESC), int(H * ESC)

cmd = ['ffmpeg', '-v', 'error', '-i', BRUTO, '-vf', f'fps={FPS},crop={W}:{H}:{X0}:{Y0},scale={w}:{h},format=gray',
       '-f', 'rawvideo', '-pix_fmt', 'gray', '-']
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
ant = None
saida = []
i = 0
k = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
while True:
    b = p.stdout.read(w * h)
    if len(b) < w * h:
        break
    q = np.frombuffer(b, np.uint8).reshape(h, w)
    q = q.copy()
    # a câmera invade o canto inferior direito da região da tela
    q[int((777 - Y0) * ESC):, int((1612 - X0) * ESC):] = 0
    caixa, area, comps = None, 0.0, []
    if ant is not None:
        d = cv2.absdiff(q, ant)
        m = (d > 18).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
        m = cv2.dilate(m, k, iterations=2)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        boxes = [st[j] for j in range(1, n) if st[j][4] >= 40]
        comps = [[round(X0 + bx[0] / ESC), round(Y0 + bx[1] / ESC), round(X0 + (bx[0] + bx[2]) / ESC),
                  round(Y0 + (bx[1] + bx[3]) / ESC), int(bx[4] / ESC / ESC)] for bx in boxes]
        if boxes:
            xs0 = min(bx[0] for bx in boxes); ys0 = min(bx[1] for bx in boxes)
            xs1 = max(bx[0] + bx[2] for bx in boxes); ys1 = max(bx[1] + bx[3] for bx in boxes)
            caixa = [round(X0 + xs0 / ESC), round(Y0 + ys0 / ESC), round(X0 + xs1 / ESC), round(Y0 + ys1 / ESC)]
            area = float((m > 0).sum()) / (w * h)
    saida.append({'t': round(i / FPS, 2), 'caixa': caixa, 'area': round(area, 4), 'comps': comps if ant is not None else []})
    ant = q
    i += 1
p.wait()
json.dump(saida, open(os.path.join(AQUI, 'trab', 'atividade.json'), 'w'))
print('quadros', i)
