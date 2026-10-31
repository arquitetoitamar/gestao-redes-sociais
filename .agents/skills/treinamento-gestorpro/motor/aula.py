#!/usr/bin/env python3
"""Motor das aulas do treinamento GestorPro (skill treinamento-gestorpro).

Abertura simples + seções narradas pelo avatar do Itamar (HeyGen) + cartela final.
A tela é a página capturada em retina (capturas/pagina.png, rolagem costurada) dentro da
moldura 16:9; a câmera rola e dá zoom conforme o roteiro.py da aula, com luz (resto
escurecido), cartões explicativos, cursor e o avatar num círculo.

  python3 aula.py <pasta-da-aula> tempos              duração de cada seção
  python3 aula.py <pasta-da-aula> quadros t1,t2,...   JPGs de conferência em trab/
  python3 aula.py <pasta-da-aula> teste <ini> <fim>   trecho -> videos/teste.mp4
  python3 aula.py <pasta-da-aula>                     vídeo inteiro -> videos/final.mp4
  python3 aula.py <pasta-da-aula> junta               só refaz áudio + junção das partes
"""
import json, math, os, re, subprocess, sys, unicodedata
from multiprocessing import Pool
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from motion import (W, H, YEL, INK, NAVY, GREEN, RED, WHITE, GREY, clamp01, ease, ease_io, ease_back,
                    sprite_texto, cola, cola_escala, caixa, sobre, icone)
MOTOR = os.path.dirname(os.path.abspath(__file__))
AQUI = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
sys.path.insert(0, AQUI)
import roteiro as R

SECS = sorted(R.SECOES)
C = os.path.join(AQUI, 'capturas')
T = os.path.join(AQUI, 'trab')
V = os.path.join(AQUI, 'videos')
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
FPS = 30
VW, VH = 1470, 827                 # tela 16:9 em pontos
MX, MY = 236, 52                   # canto da área principal
MH = VH - MY                       # altura visível da área principal (775)
ABERTURA, GAP, FINAL = 4.2, 0.6, 5.0
ORANGE = (40, 120, 235)


# ---------------------------------------------------------------- tempo da fala
def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', s)


def falas():
    out = {}
    for s in SECS:
        d = json.load(open(os.path.join(T, 'pal-%d.json' % s)))
        txt, tempos = '', []
        for w in d['transcription']:
            pedaco = norm(w['text'])
            if not pedaco.strip():
                pedaco = ' '
            for ch in pedaco:
                if ch == ' ' and txt.endswith(' '):
                    continue
                txt += ch
                tempos.append(w['offsets']['from'] / 1000)
        out[s] = (txt, tempos)
    return out


def acha(fl, s, frase):
    txt, tempos = fl[s]
    alvo = norm(frase).strip()
    i = txt.find(alvo)
    if i < 0:
        raise SystemExit('não achei "%s" na seção %d: ...%s' % (frase, s, txt[:300]))
    return tempos[i]


def duracao(arq):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', arq],
                                capture_output=True, text=True).stdout)


DUR = {s: duracao(os.path.join(V, 'av-%d.mp4' % s)) for s in SECS}
INI = {}
_t = ABERTURA
for s in SECS:
    INI[s] = _t
    _t += DUR[s] + GAP
FIM_AULA = _t
TOTAL = FIM_AULA + FINAL
N = int(round(TOTAL * FPS))


# ---------------------------------------------------------------- linha do tempo
def linha():
    fl = falas()
    ev = []
    for s, lista in R.SECOES.items():
        for gat, tipo, dados in lista:
            t = INI[s] + (gat if isinstance(gat, (int, float)) else acha(fl, s, gat))
            ev.append((t, s, tipo, dados))
    ev.sort(key=lambda e: e[0])
    return ev


def ret_tela(dados, S):
    """retângulo em pontos na tela 16:9 (para 'pag', usa a rolagem S)"""
    if 'pag' in dados:
        x, y, w, h = dados['pag']
        return (x + MX, y - S + MY, w, h)
    return dados['tela']


def s_alvo(r):
    x, y, w, h = r
    return float(min(max(y + h / 2 - MH / 2, 0), PAGE_H - MH))


class Plano:
    def __init__(self):
        self.ev = linha()
        n = N
        S = np.zeros(n); z = np.ones(n); cx = np.full(n, VW / 2); cy = np.full(n, VH / 2)
        estado = [None] * n
        cur = {'S': 0.0, 'z': 1.0, 'cx': VW / 2, 'cy': VH / 2}
        self.luzes, self.cartoes, self.cliques, self.estados = [], [], [], []
        cur_estado, t_estado = None, 0.0
        luz_atual, cart_atual = None, None
        marcas = []
        for t, s, tipo, d in self.ev:
            marcas.append((t, tipo, d))
        # câmera e rolagem
        i_ev = 0
        for f in range(n):
            t = f / FPS
            while i_ev < len(self.ev) and self.ev[i_ev][0] <= t:
                _, sec, tipo, d = self.ev[i_ev]
                if tipo == 'geral':
                    cur.update(S=float(d['S']) if 'S' in d else cur['S'], z=1.0, cx=VW / 2, cy=VH / 2)
                elif tipo == 'foco':
                    if 'pag' in d:
                        cur['S'] = s_alvo(d['pag'])
                    rx, ry, rw, rh = ret_tela(d, cur['S'])
                    zz = d.get('z') or min(0.82 * VW / rw, 0.72 * VH / rh)
                    zz = min(1.9, max(1.0, zz))
                    cur.update(z=zz, cx=rx + rw / 2, cy=ry + rh / 2)
                elif tipo == 'estado':
                    cur_estado = d['nome']
                i_ev += 1
            S[f], z[f], cx[f], cy[f] = cur['S'], cur['z'], cur['cx'], cur['cy']
            estado[f] = cur_estado
        sg = 0.38 * FPS
        self.S = gaussian_filter1d(S, sg * 1.15, mode='nearest')
        self.z = gaussian_filter1d(z, sg, mode='nearest')
        hw, hh = VW / (2 * z), VH / (2 * z)
        cx, cy = np.clip(cx, hw, VW - hw), np.clip(cy, hh, VH - hh)
        self.cx = gaussian_filter1d(cx, sg, mode='nearest')
        self.cy = gaussian_filter1d(cy, sg, mode='nearest')
        hw, hh = VW / (2 * self.z), VH / (2 * self.z)
        self.cx, self.cy = np.clip(self.cx, hw, VW - hw), np.clip(self.cy, hh, VH - hh)
        # estados como intervalos (para o cross-fade)
        self.est_alpha = {}
        for nome in R.ESTADOS:
            a = np.array([1.0 if e == nome else 0.0 for e in estado])
            self.est_alpha[nome] = gaussian_filter1d(a, 0.12 * FPS, mode='nearest')
        # luzes, cartões e cliques como intervalos
        fim_sec = {s: INI[s] + DUR[s] + GAP * 0.6 for s in SECS}
        abertos = {'luz': None, 'cartao': None}
        for t, sec, tipo, d in self.ev:
            if tipo in ('luz', 'apaga'):
                if abertos['luz']:
                    abertos['luz'][1] = t
                    abertos['luz'] = None
                if tipo == 'luz':
                    item = [t, fim_sec[sec] + 30, d]
                    self.luzes.append(item)
                    abertos['luz'] = item
            if tipo in ('cartao', 'grande', 'fecha'):
                if abertos['cartao']:
                    abertos['cartao'][1] = t
                    abertos['cartao'] = None
                if tipo != 'fecha':
                    item = [t, fim_sec[sec] + 30, d, tipo]
                    self.cartoes.append(item)
                    abertos['cartao'] = item
            if tipo == 'clique':
                self.cliques.append((t, d))
        for lst in (self.luzes, self.cartoes):
            for item in lst:
                item[1] = min(item[1], FIM_AULA - 0.2)
        self.capitulo = [(INI[s], s) for s in SECS]


FOLGA = 330                  # folga no fim da página para centralizar as últimas linhas
from PIL import Image as _Img
PAGE_H = _Img.open(os.path.join(C, 'pagina.png')).size[1] // 2 + FOLGA


# ---------------------------------------------------------------- imagens da tela
def pad16x9(im, topo_cortado=0):
    """captura de tela inteira (2940 x h) -> 2940 x 1654, estendendo o miolo"""
    h = im.shape[0]
    alvo = VH * 2
    if topo_cortado:
        im = np.vstack([np.repeat(im[:1], topo_cortado, axis=0), im])
        h = im.shape[0]
    if h >= alvo:
        return im[:alvo]
    rod = 70
    out = np.empty((alvo, im.shape[1], 3), np.uint8)
    out[:h - rod] = im[:h - rod]
    out[h - rod:alvo - rod] = im[h - rod - 40]
    out[alvo - rod:] = im[h - rod:]
    return out


class Tela:
    def __init__(self):
        self.mold = cv2.imread(os.path.join(C, 'moldura16x9.png'))
        pag = cv2.imread(os.path.join(C, 'pagina.png'))
        folga = np.empty((FOLGA * 2, pag.shape[1], 3), np.uint8)
        folga[:] = pag[-6]
        self.pag = np.vstack([pag, folga])
        self.alt, self.estados = {}, {}
        for nome, e in R.ESTADOS.items():
            im = cv2.imread(os.path.join(C, e['arquivo']))
            if e['tipo'] == 'pagina':             # mesma página, outro estado (aba, filtro) na rolagem e['scroll']
                p2 = self.pag.copy()
                miolo = im[MY * 2 - e.get('corte', 0):, MX * 2:]
                y0 = e['scroll'] * 2
                p2[y0:y0 + miolo.shape[0]] = miolo[:p2.shape[0] - y0]
                self.alt[nome] = p2
            else:                                  # tela inteira (outra página, modal)
                self.estados[nome] = pad16x9(im)
        self.base = self.mold.copy()

    def quadro(self, S, alphas):
        y = int(round(S * 2))
        hmain = VH * 2 - MY * 2
        f = self.base
        f[MY * 2:, MX * 2:] = self.pag[y:y + hmain]
        for nome, p2 in self.alt.items():
            a = alphas[nome]
            if a > 0.01:
                f[MY * 2:, MX * 2:] = cv2.addWeighted(f[MY * 2:, MX * 2:], 1 - a, p2[y:y + hmain], a, 0)
        for nome, im in self.estados.items():
            a = alphas[nome]
            if a > 0.01:
                f = cv2.addWeighted(f, 1 - a, im, a, 0) if a < 0.99 else im.copy()
        return f


# ---------------------------------------------------------------- fundo, moldura e câmera
def fundo():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    top, bot = np.array([46, 22, 10], np.float32), np.array([70, 36, 16], np.float32)
    k = (yy / H)[:, :, None]
    base = top * (1 - k) + bot * k
    g = np.exp(-((xx - 1500) ** 2 + (yy - 200) ** 2) / (2 * 520 ** 2))[:, :, None]
    base = base * (1 - 0.18 * g) + np.array((255, 170, 60), np.float32) * 0.18 * g
    img = base.astype(np.uint8)
    for x in range(0, W, 40):
        for y in range(0, H, 40):
            cv2.circle(img, (x, y), 1, (92, 64, 44), -1, cv2.LINE_AA)
    return img


def camera(tela_img, z, cx, cy, bg):
    """tela 2940x1654 -> quadro 1920x1080 com moldura arredondada quando não está em tela cheia.
    Devolve o quadro e a função que leva pontos da tela para pixels do quadro."""
    f = ease_io((z - 1.0) / 0.22)
    ow = 1700 + 220 * f
    oh = ow * VH / VW
    ox, oy = (W - ow) / 2, (H - oh) / 2 + 6 * (1 - f)
    cw, ch = VW / z, VH / z
    s = ow / cw                                        # pixels de saída por ponto
    src = tela_img
    k = 2.0                                            # pixels da captura por ponto
    if s / k < 0.78:                                   # reduz antes (texto sem serrilhado)
        src = cv2.resize(tela_img, (VW, VH), interpolation=cv2.INTER_AREA)
        k = 1.0
    sp = s / k
    x0, y0 = cx - cw / 2, cy - ch / 2
    M = np.float32([[sp, 0, ox - x0 * k * sp], [0, sp, oy - y0 * k * sp]])
    warp = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR if sp < 1.3 else cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)
    if f >= 0.995:
        out = warp
    else:
        out = bg.copy()
        X0, Y0, X1, Y1 = int(round(ox)), int(round(oy)), int(round(ox + ow)), int(round(oy + oh))
        sh = np.zeros((H // 8, W // 8), np.float32)
        cv2.rectangle(sh, (X0 // 8, Y0 // 8 + 2), (X1 // 8, Y1 // 8 + 3), 1.0, -1)
        sh = cv2.resize(cv2.GaussianBlur(sh, (0, 0), 3), (W, H))[:, :, None]
        out = (out * (1 - 0.55 * sh * (1 - f))).astype(np.uint8)
        r = int(22 * (1 - f)) + 1
        m = np.zeros((H, W), np.uint8)
        cv2.rectangle(m, (X0 + r, Y0), (X1 - r, Y1), 255, -1)
        cv2.rectangle(m, (X0, Y0 + r), (X1, Y1 - r), 255, -1)
        for px, py in ((X0 + r, Y0 + r), (X1 - r, Y0 + r), (X0 + r, Y1 - r), (X1 - r, Y1 - r)):
            cv2.circle(m, (px, py), r, 255, -1, cv2.LINE_AA)
        a = (m.astype(np.float32) / 255)[:, :, None]
        ys, xs = max(0, Y0 - 2), max(0, X0 - 2)
        ye, xe = min(H, Y1 + 2), min(W, X1 + 2)
        reg = a[ys:ye, xs:xe]
        out[ys:ye, xs:xe] = (out[ys:ye, xs:xe] * (1 - reg) + warp[ys:ye, xs:xe] * reg).astype(np.uint8)

    def mapa(px, py):
        return ox + (px - x0) * s, oy + (py - y0) * s
    return out, mapa, s


# ---------------------------------------------------------------- camadas
def arredondado(img, x0, y0, x1, y1, r, cor, esp):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    r = int(max(1, min(r, (x1 - x0) / 2, (y1 - y0) / 2)))
    cv2.line(img, (x0 + r, y0), (x1 - r, y0), cor, esp, cv2.LINE_AA)
    cv2.line(img, (x0 + r, y1), (x1 - r, y1), cor, esp, cv2.LINE_AA)
    cv2.line(img, (x0, y0 + r), (x0, y1 - r), cor, esp, cv2.LINE_AA)
    cv2.line(img, (x1, y0 + r), (x1, y1 - r), cor, esp, cv2.LINE_AA)
    for (cx, cy), a0 in (((x0 + r, y0 + r), 180), ((x1 - r, y0 + r), 270), ((x1 - r, y1 - r), 0), ((x0 + r, y1 - r), 90)):
        cv2.ellipse(img, (cx, cy), (r, r), 0, a0, a0 + 90, cor, esp, cv2.LINE_AA)


class Camadas:
    def __init__(self, plano):
        self.p = plano
        self.cache = {}
        self.cursor = self.faz_cursor()

    def spr(self, chave, fn):
        if chave not in self.cache:
            self.cache[chave] = fn()
        return self.cache[chave]

    def faz_cursor(self):
        S = 4
        im = np.zeros((44 * S, 32 * S, 4), np.uint8)
        pts = np.array([[2, 2], [2, 34], [10, 26], [16, 40], [21, 38], [15, 24], [26, 24]], np.int32) * S
        cv2.fillPoly(im, [pts], (255, 255, 255, 255), cv2.LINE_AA)
        cv2.polylines(im, [pts], True, (20, 20, 20, 255), 2 * S, cv2.LINE_AA)
        return cv2.resize(im, (32, 44), interpolation=cv2.INTER_AREA)

    def luz(self, f, t, mapa, S):
        for t0, t1, d in self.p.luzes:
            if t0 - 0.05 <= t < t1 + 0.35:
                a = ease((t - t0) / 0.35) * (1 - ease((t - t1) / 0.35))
                if a <= 0.01:
                    continue
                rx, ry, rw, rh = ret_tela(d, S)
                pad = 6
                X0, Y0 = mapa(rx - pad, ry - pad)
                X1, Y1 = mapa(rx + rw + pad, ry + rh + pad)
                X0, Y0, X1, Y1 = max(-5, X0), max(-5, Y0), min(W + 5, X1), min(H + 5, Y1)
                if X1 - X0 < 4 or Y1 - Y0 < 4:
                    continue
                esc = (f.astype(np.float32) * (1 - 0.58 * a)).astype(np.uint8)
                m = np.zeros((H, W), np.uint8)
                r = 14
                xi0, yi0, xi1, yi1 = int(X0), int(Y0), int(X1), int(Y1)
                cv2.rectangle(m, (xi0 + r, yi0), (xi1 - r, yi1), 255, -1)
                cv2.rectangle(m, (xi0, yi0 + r), (xi1, yi1 - r), 255, -1)
                for px, py in ((xi0 + r, yi0 + r), (xi1 - r, yi0 + r), (xi0 + r, yi1 - r), (xi1 - r, yi1 - r)):
                    cv2.circle(m, (px, py), r, 255, -1, cv2.LINE_AA)
                mm = (m.astype(np.float32) / 255)[:, :, None]
                f[:] = (esc * (1 - mm) + f * mm).astype(np.uint8)
                ov = f.copy()
                arredondado(ov, X0, Y0, X1, Y1, r, YEL, 5)
                f[:] = cv2.addWeighted(f, 1 - a, ov, a, 0)
                if d.get('rot'):
                    sp = self.spr(('rot', d['rot']), lambda: sprite_texto(d['rot'], 30, INK, fundo=YEL + (255,), pad=(16, 8), raio=10))
                    lx = min(max(X0, 30), W - sp.shape[1] - 30)
                    ly = Y0 - sp.shape[0] - 12
                    if ly < 20:
                        ly = Y1 + 12
                    if ly + sp.shape[0] > H - 20:
                        ly = max(20, Y0 + 12)
                    cola(f, sp, lx, ly - (1 - ease((t - t0) / 0.3)) * 12, a)

    def cartao(self, f, t):
        for t0, t1, d, tipo in self.p.cartoes:
            if not (t0 - 0.05 <= t < t1 + 0.4):
                continue
            k = t - t0
            a = ease(k / 0.35) * (1 - ease((t - t1) / 0.35))
            if a <= 0.01:
                continue
            if tipo == 'cartao':
                spr = self.spr(('c', d['chap'], d['tit']), lambda: self.faz_cartao(d))
                x = 46 - (1 - ease(k / 0.4)) * 90
                cola(f, spr, x, H - 60 - spr.shape[0], a)
            else:
                spr = self.spr(('g', d['chap'], d['tit']), lambda: self.faz_grande(d))
                f[:] = (f.astype(np.float32) * (1 - 0.55 * a)).astype(np.uint8)
                cola_escala(f, spr, W / 2, H / 2 - 20, 0.9 + 0.1 * ease_back(k / 0.45), a)

    def faz_cartao(self, d):
        chap = sprite_texto(d['chap'], 24, INK, fundo=YEL + (255,), pad=(14, 6), raio=8)
        tit = sprite_texto(d['tit'], 42, WHITE, pad=(0, 0), larg_max=760)
        txt = sprite_texto(d.get('txt', ''), 28, (225, 218, 210), pad=(0, 0), peso=500, larg_max=760) if d.get('txt') else None
        w = max(tit.shape[1], txt.shape[1] if txt is not None else 0) + 80
        h = 40 + tit.shape[0] + (14 + txt.shape[0] if txt is not None else 0) + 34
        box = caixa(w, h, (40, 20, 9), 22, 240, borda=(90, 64, 40), larg_borda=2)
        cv2.rectangle(box, (0, 22), (7, h - 22), YEL + (255,), -1)
        sobre(box, tit, 40, 36)
        if txt is not None:
            sobre(box, txt, 40, 36 + tit.shape[0] + 14)
        out = np.zeros((h + chap.shape[0] - 14, max(w, chap.shape[1] + 40), 4), np.uint8)
        sobre(out, box, 0, chap.shape[0] - 14)
        sobre(out, chap, 34, 0)
        return out

    def faz_grande(self, d):
        cor = {'red': (90, 90, 235), 'yel': YEL, 'green': (120, 205, 60)}[d.get('cor', 'yel')]
        chap = sprite_texto(d['chap'], 34, INK, fundo=cor + (255,), pad=(20, 9), raio=12)
        tit = sprite_texto(d['tit'], 78, WHITE, pad=(0, 0), larg_max=1240, alinha='centro', entre=1.12)
        txt = sprite_texto(d['txt'], 38, (225, 218, 210), pad=(0, 0), peso=600, larg_max=1240, alinha='centro') if d.get('txt') else None
        w = max(tit.shape[1], txt.shape[1] if txt is not None else 0, chap.shape[1]) + 140
        h = 70 + chap.shape[0] + 30 + tit.shape[0] + (24 + txt.shape[0] if txt is not None else 0) + 70
        box = caixa(w, h, (44, 21, 10), 34, 245, borda=(96, 70, 46), larg_borda=2)
        cv2.rectangle(box, (40, 0), (w - 40, 6), cor + (255,), -1)
        y = 70
        sobre(box, chap, (w - chap.shape[1]) // 2, y)
        y += chap.shape[0] + 30
        sobre(box, tit, (w - tit.shape[1]) // 2, y)
        if txt is not None:
            sobre(box, txt, (w - txt.shape[1]) // 2, y + tit.shape[0] + 24)
        return box

    def clique(self, f, t, mapa, S):
        for t0, d in self.p.cliques:
            k = t - (t0 - 0.9)
            if not (0 <= k < 2.2):
                continue
            rx, ry, rw, rh = ret_tela(d, S)
            tx, ty = mapa(rx + rw / 2, ry + rh / 2)
            sx, sy = tx + 260, ty + 200
            e = ease_io(k / 0.85)
            x, y = sx + (tx - sx) * e, sy + (ty - sy) * e
            a = clamp01(k / 0.2) * (1 - clamp01((k - 1.7) / 0.5))
            kc = k - 0.9
            if 0 <= kc < 0.6:
                ov = f.copy()
                cv2.circle(ov, (int(tx), int(ty)), int(10 + 70 * ease(kc / 0.6)), YEL, 4, cv2.LINE_AA)
                f[:] = cv2.addWeighted(f, 1 - (1 - kc / 0.6) * a, ov, (1 - kc / 0.6) * a, 0)
            pres = 0.88 if 0.85 <= k < 1.05 else 1.0
            cola_escala(f, self.cursor, x + 14, y + 20, pres, a)

    def chip(self, f, t):
        for t0, s in self.p.capitulo:
            k = t - t0
            if 0 <= k < 4.0:
                a = ease(k / 0.35) * (1 - ease((k - 3.5) / 0.5))
                sp = self.spr(('cap', s), lambda: self.faz_chip(s))
                cola(f, sp, 46 - (1 - ease(k / 0.4)) * 50, 36, a)

    def faz_chip(self, s):
        num = sprite_texto('%02d' % s, 28, INK, fundo=YEL + (255,), pad=(12, 6), raio=8)
        tit = sprite_texto(R.CAPITULOS[s].upper(), 28, WHITE, fundo=(40, 20, 9, 235), pad=(14, 6), raio=8)
        out = np.zeros((max(num.shape[0], tit.shape[0]), num.shape[1] + 8 + tit.shape[1], 4), np.uint8)
        sobre(out, num, 0, 0)
        sobre(out, tit, num.shape[1] + 8, 0)
        return out


# ---------------------------------------------------------------- avatar
class Avatar:
    D = 290

    def __init__(self):
        self.sec, self.p, self.idx, self.q = None, None, -1, None
        D = self.D
        m = np.zeros((D * 4, D * 4), np.uint8)
        cv2.circle(m, (D * 2, D * 2), D * 2 - 2, 255, -1, cv2.LINE_AA)
        self.mask = cv2.resize(m, (D, D), interpolation=cv2.INTER_AREA).astype(np.float32)[:, :, None] / 255

    def quadro(self, sec, k):
        alvo = int(k * FPS)
        if self.sec != sec or alvo < self.idx:
            if self.p:
                self.p.kill()
            ss = max(0.0, alvo / FPS)
            self.p = subprocess.Popen([FF, '-v', 'error', '-ss', '%.3f' % ss, '-i', os.path.join(V, 'av-%d.mp4' % sec),
                                       '-vf', 'fps=30,crop=430:430:425:95,scale=%d:%d' % (self.D, self.D),
                                       '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self.sec, self.idx = sec, alvo - 1
        n = self.D * self.D * 3
        while self.idx < alvo:
            b = self.p.stdout.read(n)
            if len(b) == n:
                self.q = np.frombuffer(b, np.uint8).reshape(self.D, self.D, 3)
            self.idx += 1
        return self.q

    def cola(self, f, t):
        sec = None
        for s in SECS:
            if INI[s] - GAP <= t < INI[s] + DUR[s] + (GAP if s < SECS[-1] else FINAL):
                sec = s
        if sec is None:
            return
        k = min(max(t - INI[sec], 0.0), DUR[sec] - 0.05)
        q = self.quadro(sec, k)
        if q is None:
            return
        a = ease((t - INI[1] + 0.4) / 0.5) * (1 - ease((t - FIM_AULA - 0.2) / 0.5))
        D = self.D
        x, y = W - 40 - D, H - 40 - D
        reg = f[y:y + D, x:x + D].astype(np.float32)
        m = self.mask * a
        f[y:y + D, x:x + D] = (reg * (1 - m) + q.astype(np.float32) * m).astype(np.uint8)
        ov = f.copy()
        cv2.circle(ov, (x + D // 2, y + D // 2), D // 2 + 3, YEL, 6, cv2.LINE_AA)
        f[:] = cv2.addWeighted(f, 1 - a, ov, a, 0)


# ---------------------------------------------------------------- abertura e final
class Cartelas:
    def __init__(self, bg):
        self.bg = bg
        A = R.AULA
        self.a = {'chap': sprite_texto('TREINAMENTO GESTORPRO', 30, INK, fundo=YEL + (255,), pad=(20, 9), raio=12),
                  'tit': sprite_texto(A['titulo'], 92, WHITE, pad=(0, 0), larg_max=1600, alinha='centro'),
                  'sub': sprite_texto(A['subtitulo'], 36, (225, 218, 210), pad=(0, 0), peso=500, larg_max=1500, alinha='centro'),
                  'cam': sprite_texto(A['caminho'], 30, (255, 210, 150), pad=(0, 0), peso=600)}
        self.f = {'chap': sprite_texto('TREINAMENTO GESTORPRO', 30, INK, fundo=YEL + (255,), pad=(20, 9), raio=12),
                  'tit': sprite_texto(A['fecho'], 64, WHITE, pad=(0, 0), larg_max=1600, alinha='centro'),
                  'sub': sprite_texto(A.get('chamada', 'Veja as outras aulas da playlist de treinamento'), 36,
                                      (225, 218, 210), pad=(0, 0), peso=500)}

    def abertura(self, t):
        f = self.bg.copy()
        A = self.a
        cola_escala(f, A['chap'], W / 2, 360 - (1 - ease(t / 0.5)) * 30, 1.0, ease(t / 0.4))
        k = t - 0.3
        cola_escala(f, A['tit'], W / 2, 480, 0.94 + 0.06 * ease(k / 0.6), ease(k / 0.5))
        k = t - 0.8
        cola_escala(f, A['sub'], W / 2, 590 + (1 - ease(k / 0.5)) * 20, 1.0, ease(k / 0.5))
        k = t - 1.2
        larg = int(520 * ease_io(k / 0.8))
        if larg > 2:
            cv2.line(f, (W // 2 - larg // 2, 660), (W // 2 + larg // 2, 660), YEL, 3, cv2.LINE_AA)
        cola_escala(f, A['cam'], W / 2, 710, 1.0, ease((t - 1.6) / 0.5))
        sai = clamp01((t - (ABERTURA - 0.45)) / 0.45)
        if sai > 0:
            f = (f.astype(np.float32) * (1 - sai) + np.full_like(f, 255) * 0.0 * sai).astype(np.uint8)
        return f

    def final(self, t):
        f = self.bg.copy()
        A = self.f
        cola_escala(f, A['chap'], W / 2, 400, 1.0, ease(t / 0.4))
        cola_escala(f, A['tit'], W / 2, 510, 0.95 + 0.05 * ease((t - 0.3) / 0.5), ease((t - 0.3) / 0.5))
        cola_escala(f, A['sub'], W / 2, 610, 1.0, ease((t - 0.8) / 0.5))
        fim = clamp01((t - (FINAL - 0.8)) / 0.8)
        if fim > 0:
            f = (f.astype(np.float32) * (1 - fim)).astype(np.uint8)
        return f


# ---------------------------------------------------------------- quadro
class Motor:
    def __init__(self):
        self.p = Plano()
        self.tela = Tela()
        self.bg = fundo()
        self.cam = Camadas(self.p)
        self.av = Avatar()
        self.cart = Cartelas(self.bg)

    def quadro(self, n):
        t = n / FPS
        if t < ABERTURA:
            f = self.cart.abertura(t)
            if t > ABERTURA - 0.45:                      # entra a tela por baixo
                g = self.tela_quadro(n)
                a = ease((t - (ABERTURA - 0.45)) / 0.45)
                f = cv2.addWeighted(f, 1 - a, g, a, 0)
            return f
        if t >= FIM_AULA:
            f = self.cart.final(t - FIM_AULA)
            if t < FIM_AULA + 0.4:
                g = self.tela_quadro(min(n, N - 1))
                a = ease((t - FIM_AULA) / 0.4)
                f = cv2.addWeighted(g, 1 - a, f, a, 0)
            return f
        return self.tela_quadro(n)

    def tela_quadro(self, n):
        p = self.p
        n = min(n, N - 1)
        t = n / FPS
        S = float(p.S[n])
        img = self.tela.quadro(S, {k: v[n] for k, v in p.est_alpha.items()})
        f, mapa, s = camera(img, float(p.z[n]), float(p.cx[n]), float(p.cy[n]), self.bg)
        self.cam.luz(f, t, mapa, S)
        self.cam.clique(f, t, mapa, S)
        self.cam.cartao(f, t)
        self.cam.chip(f, t)
        self.av.cola(f, t)
        return f


def encoder(caminho, crf=19):
    return subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H),
                             '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
                             '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', '-movflags', '+faststart', caminho],
                            stdin=subprocess.PIPE)


def parte(args):
    n0, n1, caminho = args
    m = Motor()
    enc = encoder(caminho)
    for n in range(n0, n1):
        enc.stdin.write(np.ascontiguousarray(m.quadro(n)).tobytes())
    enc.stdin.close(); enc.wait()
    return caminho


def audio():
    """voz das seções (só ganho até -16 LUFS) nos tempos certos + trilha curta na abertura e no final"""
    from scipy.io import wavfile
    SR = 48000
    voz = os.path.join(T, 'voz.wav')
    lista = os.path.join(T, 'voz.txt')
    partes = []
    for s in SECS:
        a = os.path.join(T, 'v-%d.wav' % s)
        subprocess.run([FF, '-v', 'error', '-y', '-i', os.path.join(V, 'av-%d.mp4' % s), '-vn', '-ac', '1', '-ar', str(SR),
                        '-c:a', 'pcm_s16le', a], check=True)
        partes.append(a)
    total = np.zeros(int(TOTAL * SR) + SR, np.float32)
    for s, a in zip(SECS, partes):
        sr, x = wavfile.read(a)
        x = x.astype(np.float32) / 32768
        i = int(INI[s] * SR)
        total[i:i + len(x)] += x
        os.remove(a)
    wavfile.write(voz, SR, (np.clip(total, -1, 1) * 32767).astype(np.int16))
    del total
    m = subprocess.run([FF, '-hide_banner', '-i', voz, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    filtro = ('loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:'
              'offset=%s:linear=true' % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
    vn = os.path.join(T, 'voz-norm.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-i', voz, '-af', filtro, '-ar', str(SR), '-ac', '1', vn], check=True)
    sr, y = wavfile.read(vn)
    y = y.astype(np.float32) / 32768
    os.remove(voz); os.remove(vn)
    tr_arq = os.path.join(MOTOR, 'trilha.wav')
    if os.path.exists(tr_arq):
        sr2, tr = wavfile.read(tr_arq)
        tr = tr.astype(np.float32)
        tr /= max(1.0, np.abs(tr).max())
        if tr.ndim == 2:
            tr = tr.mean(axis=1)
        if sr2 != SR:
            idx = (np.arange(int(len(tr) * SR / sr2)) * sr2 / SR).astype(int)
            tr = tr[idx]
        ab = tr[int(8.0 * SR):int((8.0 + ABERTURA + 1.0) * SR)] * 0.22
        ab[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))
        ab[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
        y[:len(ab)] += ab[:len(y)]
        fi = tr[int(8.0 * SR):int((8.0 + FINAL) * SR)] * 0.22
        fi[:int(0.4 * SR)] *= np.linspace(0, 1, int(0.4 * SR))
        fi[-int(2.0 * SR):] *= np.linspace(1, 0, int(2.0 * SR))
        i = int(FIM_AULA * SR)
        y[i:i + len(fi)] += fi[:len(y) - i]
    y = y[:int(TOTAL * SR)]
    tmp = os.path.join(T, 'audio_final.wav')
    wavfile.write(tmp, SR, (np.clip(y, -0.95, 0.95) * 32767).astype(np.int16))
    del y
    out = os.path.join(T, 'audio_final.m4a')
    subprocess.run([FF, '-v', 'error', '-y', '-i', tmp, '-ac', '2', '-c:a', 'aac', '-b:a', '192k', out], check=True)
    os.remove(tmp)
    return out


NP = 3                             # processos em paralelo (mais que isso enche a swap deste Mac)


def main():
    modo = sys.argv[2] if len(sys.argv) > 2 else 'tudo'
    if modo == 'quadros':
        m = Motor()
        for t in [float(x) for x in sys.argv[3].split(',')]:
            cv2.imwrite(os.path.join(T, 'q-%06.2f.jpg' % t), m.quadro(int(t * FPS)), [cv2.IMWRITE_JPEG_QUALITY, 88])
        return
    if modo == 'teste':
        a, b = float(sys.argv[3]), float(sys.argv[4])
        print(parte((int(a * FPS), int(b * FPS), os.path.join(V, 'teste.mp4'))))
        return
    if modo == 'tempos':
        print('total %.1f s' % TOTAL, {s: (round(INI[s], 1), round(DUR[s], 1)) for s in INI})
        return
    lim = np.linspace(0, N, NP + 1).astype(int)
    partes = [(lim[i], lim[i + 1], os.path.join(V, 'parte-%02d.mp4' % i)) for i in range(NP)]
    with Pool(NP) as pool:
        for c in pool.imap_unordered(parte, partes):
            print('ok', c, flush=True)
    a = audio()
    lista = os.path.join(T, 'partes.txt')
    with open(lista, 'w') as f:
        for _, _, c in partes:
            f.write("file '%s'\n" % c)
    subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista, '-i', a, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'copy', '-shortest', '-movflags', '+faststart',
                    os.path.join(V, 'final.mp4')], check=True)
    for _, _, c in partes:
        os.remove(c)
    print(os.path.join(V, 'final.mp4'), TOTAL)


if __name__ == '__main__':
    main()
