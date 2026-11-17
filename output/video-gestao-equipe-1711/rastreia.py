"""Caixas do Gmail por quadro: âncoras marcadas à mão + propagação por homografia (a tela é um plano).

uso: python3 rastreia.py <pasta_dos_quadros>   (a_NNNN.jpg desde 38 s, b_NNNN.jpg desde 72 s, 1080x1920)
Saída: caixas.json {"<quadro global a 30 fps>": [[x0, y0, x1, y1], ...]}
"""
import json, os, sys
import cv2
import numpy as np

PASTA = sys.argv[1]
FPS = 30
AQUI = os.path.dirname(os.path.abspath(__file__))

# (segundo, caixa da linha "lsantos.ads@gmail.com" em 1080x1920) — conferidas olhando o quadro
ANCORAS = [
    (42.4, (91, 1380, 443, 1493)), (43.5, (194, 1381, 486, 1468)), (44.5, (302, 1513, 583, 1589)),
    (45.5, (464, 1589, 778, 1686)), (46.5, (400, 1589, 713, 1707)), (47.5, (346, 1599, 670, 1707)),
    (48.5, (292, 1565, 605, 1684)), (49.5, (302, 1554, 594, 1640)), (50.5, (497, 1586, 799, 1684)),
    (51.5, (443, 1608, 745, 1705)),
    (77.6, (53, 1142, 283, 1212)),
    (84.5, (0, 1221, 140, 1254)), (85.4, (0, 1220, 185, 1265)),
]
# até onde cada trecho vai (o Gmail entra/sai de quadro): [início, fim] em segundos
TRECHOS = [(41.8, 52.4), (76.9, 78.4), (83.8, 85.75)]
PAD_X, PAD_Y = 30, 22


def arquivo(n):
    t = n / FPS
    if t < 72:
        return os.path.join(PASTA, 'a_%04d.jpg' % (n - 38 * FPS))
    return os.path.join(PASTA, 'b_%04d.jpg' % (n - 72 * FPS))


orb = cv2.ORB_create(2500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
cache = {}


def feats(n):
    if n not in cache:
        g = cv2.imread(arquivo(n), cv2.IMREAD_GRAYSCALE)
        g = cv2.resize(g, (540, 960))
        cache[n] = orb.detectAndCompute(g, None)
    return cache[n]


def homog(n0, n1):
    """Homografia que leva pontos do quadro n0 ao n1 (coordenadas 1080x1920)."""
    k0, d0 = feats(n0)
    k1, d1 = feats(n1)
    if d0 is None or d1 is None:
        return None
    m = bf.match(d0, d1)
    if len(m) < 20:
        return None
    p0 = np.float32([k0[x.queryIdx].pt for x in m]) * 2
    p1 = np.float32([k1[x.trainIdx].pt for x in m]) * 2
    H, ok = cv2.findHomography(p0, p1, cv2.RANSAC, 6.0)
    if H is None or ok.sum() < 25:
        return None
    return H


def leva(caixa, H):
    x0, y0, x1, y1 = caixa
    pts = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]).reshape(-1, 1, 2)
    q = cv2.perspectiveTransform(pts, H).reshape(-1, 2)
    return (float(q[:, 0].min()), float(q[:, 1].min()), float(q[:, 0].max()), float(q[:, 1].max()))


caixas = {}
for ini, fim in TRECHOS:
    a, b = round(ini * FPS), round(fim * FPS)
    ancs = [(round(t * FPS), c) for t, c in ANCORAS if ini <= t <= fim]
    for i, (na, ca) in enumerate(ancs):
        ate_frente = ancs[i + 1][0] if i + 1 < len(ancs) else b
        ate_tras = ancs[i - 1][0] if i else a
        caixas.setdefault(na, []).append(ca)
        for passo, limite in ((1, ate_frente), (-1, ate_tras)):
            c, n = ca, na
            while n != limite:
                H = homog(n, n + passo)
                if H is None:          # perdeu o rastro: segura a última caixa
                    pass
                else:
                    c = leva(c, H)
                n += passo
                caixas.setdefault(n, []).append(c)

saida = {}
for n, cs in sorted(caixas.items()):
    saida[str(n)] = [[max(0, int(c[0] - PAD_X)), max(0, int(c[1] - PAD_Y)), min(1080, int(c[2] + PAD_X)),
                      min(1920, int(c[3] + PAD_Y))] for c in cs]
json.dump(saida, open(os.path.join(AQUI, 'caixas.json'), 'w'))
print('quadros com máscara:', len(saida), 'de', sum(round(f * FPS) - round(i * FPS) + 1 for i, f in TRECHOS))
