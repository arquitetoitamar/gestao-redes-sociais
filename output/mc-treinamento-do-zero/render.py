#!/usr/bin/env python3
"""Montagem do vídeo "Treinamento do Marketplace Connect do zero".

Abertura (videos/abertura.mp4) + miolo + cartela final. No miolo, a tela
gravada sai do quadro do Vids e entra numa moldura sobre fundo da marca, com
zoom e pan que seguem o que está sendo feito (roteiro.ZOOMS). Por cima vêm os
motions do roteiro: etiquetas, passos, painel lateral, cartões de tela cheia,
medalha, XP e o balão da câmera redondo.

  python3 render.py quadros t1,t2,...   PNGs de conferência (tempo final do miolo)
  python3 render.py teste <ini> <fim>   só um trecho do miolo -> videos/teste.mp4
  python3 render.py sfx                 momentos dos efeitos sonoros -> trab/sfx.json
  python3 render.py                     vídeo inteiro -> videos/final.mp4
"""
import bisect, json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter1d
import roteiro as R

AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, 'trab')
V = os.path.join(AQUI, 'videos')
SRC = os.path.join(V, 'bruto.mp4')
W, H, FPS = 1920, 1080, 30
FONTE = '/Users/itamar/git/gestao-redes-sociais/output/reel-explica-marketplace-connect/assets/Inter.ttf'
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'

# cores BGR
YEL = (0, 196, 245)
INK = (12, 11, 11)
NAVY = (48, 22, 10)
CARD = (58, 30, 15)
CYAN = (255, 200, 60)
GREEN = (110, 200, 50)
RED = (70, 70, 230)
WHITE = (255, 255, 255)
GREY = (190, 182, 176)

SX0, SY0, SX1, SY1 = R.SCREEN
SW, SH = SX1 - SX0, SY1 - SY0

SEG = json.load(open(os.path.join(T, 'segmentos.json')))
FAT = SEG['fat']
SEGS = SEG['seg']
C0S = [s[0] for s in SEGS]
DUR = SEGS[-1][1] / FAT
N = int(DUR * FPS)
FINAL_DUR = 8.0
PASSO_P = 80


# ---------------------------------------------------------------- tempo
def fonte_t(t):
    """tempo final do miolo -> tempo no bruto"""
    c = t * FAT
    i = max(0, bisect.bisect_right(C0S, c) - 1)
    c0, c1, s0, s1 = SEGS[i]
    if c1 <= c0:
        return s0
    return s0 + min(1.0, max(0.0, (c - c0) / (c1 - c0))) * (s1 - s0)


def final_t(s):
    """tempo no bruto -> tempo final do miolo"""
    for c0, c1, s0, s1 in SEGS:
        if s0 <= s <= s1:
            return (c0 + (s - s0) / max(1e-6, s1 - s0) * (c1 - c0)) / FAT
        if s < s0:
            return c0 / FAT
    return DUR


def clamp01(x):
    return min(1.0, max(0.0, x))


def ease(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_back(x, s=1.9):
    x = clamp01(x)
    x -= 1
    return 1 + x * x * ((s + 1) * x + s)


def janela(k, d, a=0.35, b=0.3):
    """alfa de entrada/saída de um elemento que dura d"""
    return ease(k / a) * (1 - ease((k - (d - b)) / b))


# ---------------------------------------------------------------- texto e sprites
_fontes = {}


def fonte(px, peso=900):
    k = (px, peso)
    if k not in _fontes:
        f = ImageFont.truetype(FONTE, px)
        f.set_variation_by_axes([32 if px >= 40 else 18, peso])
        _fontes[k] = f
    return _fontes[k]


def rgb(c):
    return (c[2], c[1], c[0])


def quebra(txt, f, larg):
    linhas, cur = [], ''
    for p in txt.split():
        tst = (cur + ' ' + p).strip()
        if f.getlength(tst) > larg and cur:
            linhas.append(cur)
            cur = p
        else:
            cur = tst
    linhas.append(cur)
    return linhas


def sprite_texto(txt, px, cor=WHITE, fundo=None, pad=(18, 10), raio=10, larg_max=None, peso=900,
                 contorno=0, cor_contorno=INK, entre=1.22, alinha='esq'):
    """BGRA com o texto (cores em BGR)."""
    f = fonte(px, peso)
    linhas = quebra(txt, f, larg_max) if larg_max else [txt]
    lw = int(max(f.getlength(l) for l in linhas)) + 2 * contorno
    lh = int(px * entre)
    w, h = lw + 2 * pad[0], lh * len(linhas) + 2 * pad[1] + int(px * 0.1)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if fundo:
        d.rounded_rectangle([0, 0, w - 1, h - 1], raio, fill=rgb(fundo[:3]) + (fundo[3] if len(fundo) > 3 else 255,))
    for k, l in enumerate(linhas):
        x = pad[0] + contorno
        if alinha == 'centro':
            x = (w - f.getlength(l)) / 2
        d.text((x, pad[1] + k * lh), l, font=f, fill=rgb(cor),
               stroke_width=contorno, stroke_fill=rgb(cor_contorno))
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)


def cola(dst, spr, x, y, alpha=1.0):
    if alpha <= 0.003:
        return
    h, w = spr.shape[:2]
    x, y = int(round(x)), int(round(y))
    Hd, Wd = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(Wd, x + w), min(Hd, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (s[:, :, 3:4].astype(np.float32) / 255.0) * alpha
    roi = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (roi * (1 - a) + s[:, :, :3].astype(np.float32) * a).astype(np.uint8)


def cola_escala(dst, spr, cx, cy, esc, alpha=1.0, escy=None):
    """cola centralizado em (cx, cy) com escala"""
    escy = esc if escy is None else escy
    if esc <= 0.02 or escy <= 0.02:
        return
    h, w = spr.shape[:2]
    nw, nh = max(1, int(w * esc)), max(1, int(h * escy))
    s = spr if (nw == w and nh == h) else cv2.resize(spr, (nw, nh), interpolation=cv2.INTER_AREA if esc < 1 else cv2.INTER_LINEAR)
    cola(dst, s, cx - nw / 2, cy - nh / 2, alpha)


def junta_h(*sprs, gap=0, alinha='centro'):
    h = max(s.shape[0] for s in sprs)
    w = sum(s.shape[1] for s in sprs) + gap * (len(sprs) - 1)
    out = np.zeros((h, w, 4), np.uint8)
    x = 0
    for s in sprs:
        y = (h - s.shape[0]) // 2 if alinha == 'centro' else 0
        sub = out[y:y + s.shape[0], x:x + s.shape[1]]
        a = s[:, :, 3:4].astype(np.float32) / 255
        sub[:, :, :3] = (sub[:, :, :3] * (1 - a) + s[:, :, :3] * a).astype(np.uint8)
        sub[:, :, 3] = np.maximum(sub[:, :, 3], s[:, :, 3])
        x += s.shape[1] + gap
    return out


def caixa(w, h, cor, raio, alpha=255, borda=None, larg_borda=3):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], raio, fill=rgb(cor) + (alpha,),
                        outline=(rgb(borda) + (255,)) if borda else None, width=larg_borda if borda else 0)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)


def sobre(base, spr, x, y):
    """alpha-composite de spr sobre o sprite base (BGRA), in place"""
    h, w = spr.shape[:2]
    sub = base[y:y + h, x:x + w]
    a = spr[:, :, 3:4].astype(np.float32) / 255
    sub[:, :, :3] = (sub[:, :, :3] * (1 - a) + spr[:, :, :3] * a).astype(np.uint8)
    sub[:, :, 3] = np.maximum(sub[:, :, 3], spr[:, :, 3])
    return base


# ---------------------------------------------------------------- ícones (desenhados em 4x e reduzidos)
def icone(nome, tam=56, cor=INK, fundo=YEL):
    S = tam * 4
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if fundo:
        d.ellipse([0, 0, S - 1, S - 1], fill=rgb(fundo) + (255,))
    c = rgb(cor) + (255,)
    m = S / 2
    lw = int(S * 0.075)
    if nome == 'check':
        d.line([(S * .28, S * .52), (S * .44, S * .67), (S * .73, S * .35)], fill=c, width=int(S * .1), joint='curve')
    elif nome == 'estrela':
        pts = []
        for i in range(10):
            r = S * (.30 if i % 2 == 0 else .13)
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((m + r * math.cos(a), m + 0.02 * S + r * math.sin(a)))
        d.polygon(pts, fill=c)
    elif nome == 'cadeado':
        d.rounded_rectangle([S * .3, S * .46, S * .7, S * .74], int(S * .05), fill=c)
        d.arc([S * .36, S * .26, S * .64, S * .58], 180, 360, fill=c, width=lw)
        d.line([(S * .36, S * .42), (S * .36, S * .47)], fill=c, width=lw)
        d.line([(S * .64, S * .42), (S * .64, S * .47)], fill=c, width=lw)
    elif nome == 'raio':
        d.polygon([(S * .55, S * .18), (S * .3, S * .55), (S * .48, S * .55), (S * .42, S * .82),
                   (S * .7, S * .43), (S * .52, S * .43)], fill=c)
    elif nome == 'trofeu':
        d.rounded_rectangle([S * .32, S * .24, S * .68, S * .52], int(S * .12), fill=c)
        d.arc([S * .2, S * .27, S * .4, S * .47], 90, 270, fill=c, width=lw)
        d.arc([S * .6, S * .27, S * .8, S * .47], 270, 90, fill=c, width=lw)
        d.rectangle([S * .46, S * .5, S * .54, S * .64], fill=c)
        d.rounded_rectangle([S * .34, S * .64, S * .66, S * .74], int(S * .03), fill=c)
    elif nome == 'celular':
        d.rounded_rectangle([S * .34, S * .2, S * .66, S * .8], int(S * .06), outline=c, width=lw)
        d.line([(S * .45, S * .72), (S * .55, S * .72)], fill=c, width=lw)
    elif nome == 'presente':
        d.rectangle([S * .26, S * .44, S * .74, S * .76], fill=c)
        d.rectangle([S * .22, S * .34, S * .78, S * .44], fill=c)
        d.rectangle([S * .47, S * .34, S * .53, S * .76], fill=rgb(fundo) + (255,) if fundo else (0, 0, 0, 0))
        d.ellipse([S * .32, S * .2, S * .5, S * .36], outline=c, width=lw)
        d.ellipse([S * .5, S * .2, S * .68, S * .36], outline=c, width=lw)
    elif nome == 'moeda':
        d.ellipse([S * .24, S * .24, S * .76, S * .76], outline=c, width=lw)
        f = fonte(int(S * .34))
        d.text((m, m + S * .01), '$', font=f, fill=c, anchor='mm')
    elif nome == 'link':
        d.rounded_rectangle([S * .18, S * .38, S * .56, S * .62], int(S * .1), outline=c, width=lw)
        d.rounded_rectangle([S * .44, S * .38, S * .82, S * .62], int(S * .1), outline=c, width=lw)
    elif nome == 'controle':
        d.rounded_rectangle([S * .18, S * .34, S * .82, S * .68], int(S * .16), fill=c)
        bg = rgb(fundo) + (255,) if fundo else (0, 0, 0, 0)
        d.rectangle([S * .29, S * .48, S * .41, S * .53], fill=bg)
        d.rectangle([S * .325, S * .445, S * .375, S * .565], fill=bg)
        d.ellipse([S * .6, S * .42, S * .66, S * .48], fill=bg)
        d.ellipse([S * .66, S * .5, S * .72, S * .56], fill=bg)
    elif nome == 'x':
        d.line([(S * .3, S * .3), (S * .7, S * .7)], fill=c, width=int(S * .1))
        d.line([(S * .7, S * .3), (S * .3, S * .7)], fill=c, width=int(S * .1))
    im = im.resize((tam, tam), Image.LANCZOS)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)


def medalha(tam, cor_a, cor_b):
    """medalha redonda com estrela e fita (RGB de cor_a/cor_b em BGR)"""
    S = tam * 4
    im = Image.new('RGBA', (S, int(S * 1.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(S * .3, 0), (S * .48, 0), (S * .58, S * .4), (S * .4, S * .4)], fill=(40, 90, 210, 255))
    d.polygon([(S * .52, 0), (S * .7, 0), (S * .6, S * .4), (S * .42, S * .4)], fill=(230, 60, 70, 255))
    y0 = S * .25
    for i in range(40):
        k = i / 39
        c = tuple(int(cor_a[2 - j] * (1 - k) + cor_b[2 - j] * k) for j in range(3))
        r = S * .5 - i * S * .0055
        d.ellipse([S * .5 - r, y0 + S * .5 - r, S * .5 + r, y0 + S * .5 + r], fill=c + (255,))
    pts = []
    for i in range(10):
        r = S * (.24 if i % 2 == 0 else .1)
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((S * .5 + r * math.cos(a), y0 + S * .52 + r * math.sin(a)))
    d.polygon(pts, fill=(255, 255, 255, 235))
    im = im.resize((tam, int(tam * 1.25)), Image.LANCZOS)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)


def etiqueta(chapeu, texto, ic=None, px=44, cor_chapeu=YEL):
    """chapéu amarelo + caixa escura com ícone e texto"""
    corpo = sprite_texto(texto, px, WHITE, pad=(0, 0))
    icn = icone(ic, 64) if ic else None
    ph, pv = 30, 20
    w = corpo.shape[1] + 2 * ph + (icn.shape[1] + 20 if icn is not None else 0)
    h = max(corpo.shape[0], 64) + 2 * pv
    box = caixa(w, h, (40, 20, 9), 22, 242, borda=(80, 56, 36), larg_borda=2)
    x = ph
    if icn is not None:
        sobre(box, icn, x, (h - 64) // 2)
        x += 84
    sobre(box, corpo, x, (h - corpo.shape[0]) // 2 + 2)
    chap = sprite_texto(chapeu, 24, INK, fundo=cor_chapeu + (255,), pad=(14, 6), raio=8)
    out = np.zeros((h + chap.shape[0] - 12, max(w, chap.shape[1] + 24), 4), np.uint8)
    sobre(out, box, 0, chap.shape[0] - 12)
    sobre(out, chap, 24, 0)
    return out


# ---------------------------------------------------------------- leitura de vídeo
class Leitor:
    def __init__(self, caminho, w=W, h=H, ss=0.0):
        self.w, self.h = w, h
        cmd = [FF, '-v', 'error', '-ss', '%.3f' % ss, '-i', caminho, '-vf', 'scale=%d:%d,fps=30' % (w, h),
               '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.ultimo = np.zeros((h, w, 3), np.uint8)

    def proximo(self):
        b = self.p.stdout.read(self.w * self.h * 3)
        if len(b) == self.w * self.h * 3:
            self.ultimo = np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3).copy()
        return self.ultimo

    def fecha(self):
        self.p.kill()


class Bruto:
    def __init__(self, ini=0):
        self.idx = ini - 1
        self.l = Leitor(SRC, ss=ini / 30)
        self.q = None

    def quadro(self, alvo):
        while self.idx < alvo:
            self.q = self.l.proximo()
            self.idx += 1
        return self.q


# ---------------------------------------------------------------- câmera
def plano():
    z = np.ones(N)
    cx = np.full(N, SW / 2)
    cy = np.full(N, SH / 2)
    for a, b, x, y, zz in R.ZOOMS:
        n0, n1 = int(final_t(a) * FPS), int(final_t(b) * FPS)
        z[n0:n1] = zz
        cx[n0:n1] = x - SX0
        cy[n0:n1] = y - SY0
    hw, hh = SW / (2 * z), SH / (2 * z)
    cx, cy = np.clip(cx, hw, SW - hw), np.clip(cy, hh, SH - hh)
    sg = 0.30 * FPS
    z = gaussian_filter1d(z, sg, mode='nearest')
    cx = gaussian_filter1d(cx, sg * 1.1, mode='nearest')
    cy = gaussian_filter1d(cy, sg * 1.1, mode='nearest')
    hw, hh = SW / (2 * z), SH / (2 * z)
    cx, cy = np.clip(cx, hw, SW - hw), np.clip(cy, hh, SH - hh)
    p = np.zeros(N)
    for a, b, *_ in R.PAINEIS:
        p[int(final_t(a) * FPS):int(final_t(b) * FPS)] = 1
    p = gaussian_filter1d(p, 0.2 * FPS, mode='nearest')
    return z, cx, cy, p


def fundo_marca():
    """fundo azul-marinho com grade de pontos e brilhos suaves (um pouco maior, para deslizar)"""
    w, h = W + 80, H + 80
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.zeros((h, w, 3), np.float32)
    top, bot = np.array([40, 18, 8], np.float32), np.array([66, 34, 16], np.float32)
    k = (yy / h)[:, :, None]
    base[:] = top * (1 - k) + bot * k
    for (gx, gy, r, cor, a) in ((260, 160, 700, YEL, 0.10), (1760, 980, 800, CYAN, 0.10)):
        g = np.exp(-((xx - gx) ** 2 + (yy - gy) ** 2) / (2 * r * r / 4))[:, :, None]
        base = base * (1 - a * g) + np.array(cor, np.float32) * a * g
    img = base.astype(np.uint8)
    for x in range(0, w, 48):
        for y in range(0, h, 48):
            cv2.circle(img, (x, y), 1, (95, 70, 50), -1, cv2.LINE_AA)
    return img


class Palco:
    def __init__(self):
        self.z, self.cx, self.cy, self.p = plano()
        self.bg = fundo_marca()
        self.sombras = {}
        D = 236
        self.D = D
        m = np.zeros((D * 4, D * 4), np.uint8)
        cv2.circle(m, (D * 2, D * 2), D * 2 - 2, 255, -1, cv2.LINE_AA)
        self.mask_cam = cv2.resize(m, (D, D), interpolation=cv2.INTER_AREA).astype(np.float32)[:, :, None] / 255
        an = Image.new('RGBA', (D * 4 + 40, D * 4 + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(an)
        c = D * 2 + 20
        d.ellipse([c - D * 2 - 14, c - D * 2 - 14, c + D * 2 + 14, c + D * 2 + 14], outline=rgb(YEL) + (255,), width=22)
        an = an.resize((D + 10, D + 10), Image.LANCZOS)
        self.anel = cv2.cvtColor(np.array(an), cv2.COLOR_RGBA2BGRA)

    def vista(self, n):
        z, p = self.z[n], self.p[n]
        f = ease_io((z - 1.0) / 0.35)
        vw = 1700 + 220 * f
        vw = vw * (1 - p) + 1290 * p
        vh = vw * SH / SW
        vcx = 960 * (1 - p) + (36 + 645) * p
        vcy = (532 + 8 * f) * (1 - p) + 470 * p
        raio = 24 * (1 - f) * (1 - p) + 18 * p
        return z, self.cx[n], self.cy[n], vw, vh, vcx, vcy, raio, f * (1 - p)

    def sombra(self, x0, y0, x1, y1, r):
        k = (x0 // 6, y0 // 6, x1 // 6, y1 // 6)
        if k not in self.sombras:
            if len(self.sombras) > 10:
                self.sombras.pop(next(iter(self.sombras)))
            s = np.zeros((H // 8, W // 8), np.float32)
            cv2.rectangle(s, (x0 // 8, y0 // 8 + 2), (x1 // 8, y1 // 8 + 3), 1.0, -1)
            s = cv2.GaussianBlur(s, (0, 0), 3.0)
            s = cv2.resize(s, (W, H), interpolation=cv2.INTER_LINEAR)[:, :, None]
            bg = self.bg[40:40 + H, 40:40 + W].astype(np.float32)
            self.sombras[k] = (bg * (1 - 0.6 * s)).astype(np.uint8)
        return self.sombras[k].copy()

    def compoe(self, n, q):
        q = q.copy()
        q[766:SY1, 1606:SX1] = q[766:SY1, 1605:1606]          # tira a beirada do balão da câmera
        z, cx, cy, vw, vh, vcx, vcy, raio, full = self.vista(n)
        cw, ch = SW / z, SH / z
        s = vw / cw
        vx0, vy0 = vcx - vw / 2, vcy - vh / 2
        M = np.float32([[s, 0, vx0 - (SX0 + cx - cw / 2) * s], [0, s, vy0 - (SY0 + cy - ch / 2) * s]])
        warp = cv2.warpAffine(q, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        x0, y0 = int(round(vx0)), int(round(vy0))
        x1, y1 = int(round(vx0 + vw)), int(round(vy0 + vh))
        if x0 <= 0 and y0 <= 0 and x1 >= W and y1 >= H:
            out = warp
        else:
            out = self.sombra(x0, y0, x1, y1, raio)
            xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            fundo = out[ya:yb, xa:xb].copy()
            out[ya:yb, xa:xb] = warp[ya:yb, xa:xb]
            r = int(raio)
            if r > 1:
                m = np.zeros((r * 4, r * 4), np.uint8)
                cv2.circle(m, (r * 4, r * 4), r * 4, 255, -1, cv2.LINE_AA)
                m = cv2.resize(m, (r, r), interpolation=cv2.INTER_AREA).astype(np.float32)[:, :, None] / 255
                hh, ww = yb - ya, xb - xa
                for flip_y in (False, True):
                    for flip_x in (False, True):
                        mm = m[::-1 if flip_y else 1, ::-1 if flip_x else 1]
                        cy0 = hh - r if flip_y else 0
                        cx0 = ww - r if flip_x else 0
                        if cy0 < 0 or cx0 < 0:
                            continue
                        reg = out[ya + cy0:ya + cy0 + r, xa + cx0:xa + cx0 + r].astype(np.float32)
                        fb = fundo[cy0:cy0 + r, cx0:cx0 + r].astype(np.float32)
                        out[ya + cy0:ya + cy0 + r, xa + cx0:xa + cx0 + r] = (reg * mm + fb * (1 - mm)).astype(np.uint8)
            if full < 0.98:
                cv2.rectangle(out, (xa, ya), (xb - 1, yb - 1), (90, 66, 44), 1, cv2.LINE_AA) if r <= 1 else None
        return out, q

    def camera(self, out, q, alpha=1.0):
        a, b, c, d = R.CAM_IN
        cam = cv2.resize(q[b:d, a:c], (self.D, self.D), interpolation=cv2.INTER_AREA)
        x, y = W - 34 - self.D, H - 34 - self.D
        reg = out[y:y + self.D, x:x + self.D].astype(np.float32)
        m = self.mask_cam * alpha
        out[y:y + self.D, x:x + self.D] = (reg * (1 - m) + cam.astype(np.float32) * m).astype(np.uint8)
        cola(out, self.anel, x - 5, y - 5, alpha)


# ---------------------------------------------------------------- camadas (motions)
class Camadas:
    def __init__(self):
        ft = final_t
        self.cap = [(ft(s), t) for s, t in R.CAPITULOS]
        self.cap_spr = {}
        self.tags = [(ft(a), ft(b), etiqueta(ch, tx, ic)) for a, b, ch, tx, ic in R.TAGS]
        self.passos = [(ft(a), ft(b), etiqueta(ch, tx, None, px=38)) for a, b, ch, tx in R.PASSOS]
        a, b, ch, tx = R.PROMPT
        self.prompt = (ft(a), ft(b), sprite_texto(ch, 24, INK, fundo=YEL + (255,), pad=(14, 6), raio=8),
                       sprite_texto(tx, 50, WHITE, pad=(0, 0), peso=700))
        self.inter = [(ft(a), ft(b), tipo) for a, b, tipo in R.INTERLUDIOS]
        self.inter_spr = {}
        self.paineis = []
        for a, b, tit, itens in R.PAINEIS:
            its = []
            for t, it, det in itens:
                its.append((ft(t), sprite_texto(it, 30, WHITE, pad=(0, 0)), sprite_texto(it, 30, YEL, pad=(0, 0)),
                            sprite_texto(det, 22, GREY, pad=(0, 0), peso=500, larg_max=380)))
            base, y0 = self.painel_base(tit)
            self.paineis.append((ft(a), ft(b), (base, y0), its))
        m0, m1, m2 = R.MEDALHA
        self.medalha = (ft(m0), ft(m1), ft(m2),
                        medalha(150, (60, 120, 205), (30, 70, 140)), medalha(150, (225, 225, 230), (150, 150, 160)),
                        etiqueta('MEDALHA DE BRONZE', 'Nível 1 concluído', None, px=44, cor_chapeu=(80, 140, 215)),
                        etiqueta('MEDALHA DE PRATA', 'Nos níveis 2 e 3', None, px=44, cor_chapeu=(210, 210, 215)))
        x0, x1, txt = R.XP
        self.xp = (ft(x0), ft(x1), sprite_texto(txt, 120, YEL, pad=(10, 10), contorno=8, cor_contorno=INK),
                   icone('moeda', 54, INK, YEL))
        self.cortes = [ft(b) for a, b in [(222.45, 236.95), (536.6, 562.35)]]

    # --- base do painel lateral
    def painel_base(self, titulo):
        w, h = 520, 720
        base = caixa(w, h, (44, 22, 10), 26, 246, borda=(90, 64, 40), larg_borda=2)
        cv2.rectangle(base, (26, 0), (w - 26, 5), YEL + (255,), -1)
        chap = sprite_texto('TREINO MAC', 22, INK, fundo=YEL + (255,), pad=(12, 5), raio=7)
        sobre(base, chap, 32, 34)
        tit = sprite_texto(titulo, 38, WHITE, pad=(0, 0), larg_max=456, entre=1.08)
        sobre(base, tit, 32, 84)
        return base, 84 + tit.shape[0] + 30

    def eventos_sfx(self):
        ev = []
        for a, b, _ in self.inter:
            ev += [(a - 0.15, 'whoosh'), (b - 0.3, 'whoosh_baixo')]
        for a, b, _, its in self.paineis:
            ev += [(a - 0.1, 'whoosh'), (b - 0.35, 'whoosh_baixo')]
            ev += [(t, 'ding') for t, *_ in its]
        for a, b, _ in self.tags:
            ev.append((a, 'pop'))
        for a, b, _ in self.passos:
            ev.append((a, 'pop'))
        ev.append((self.prompt[0], 'pop'))
        ev += [(self.xp[0], 'moeda'), (self.medalha[0] + 0.25, 'moeda'), (self.medalha[1] + 0.25, 'moeda')]
        ev += [(c - 0.2, 'whoosh_baixo') for c in self.cortes]
        return sorted(ev)

    def ativo_inter(self, t):
        for a, b, tipo in self.inter:
            if a <= t < b:
                return a, b, tipo
        return None

    # --- desenho
    def capitulo(self, f, t):
        for i, (t0, titulo) in enumerate(self.cap):
            if t0 <= t < t0 + 4.2 and t > 0.3:
                k = t - t0
                a = ease(k / 0.35) * (1 - ease((k - 3.7) / 0.5))
                if i not in self.cap_spr:
                    num = sprite_texto('%02d' % (i + 1), 30, INK, fundo=YEL + (255,), pad=(12, 6), raio=8)
                    tit = sprite_texto(titulo.upper(), 30, WHITE, fundo=(40, 20, 9, 235), pad=(14, 6), raio=8)
                    self.cap_spr[i] = (num, tit)
                num, tit = self.cap_spr[i]
                dx = (1 - ease(k / 0.4)) * -60
                cola(f, num, 46 + dx, H - 34 - num.shape[0], a)
                cola(f, tit, 46 + num.shape[1] + 8 + dx, H - 34 - tit.shape[0], a)

    def etiquetas(self, f, t, painel):
        for a, b, spr in self.tags:
            if a <= t < b:
                k, d = t - a, b - a
                al = janela(k, d)
                esc = 0.7 + 0.3 * ease_back(k / 0.4)
                cx = 960 if painel < 0.5 else 680
                cy = 36 + spr.shape[0] / 2 - (ease((k - (d - 0.3)) / 0.3)) * 20
                cola_escala(f, spr, cx, cy, esc, al)

    def passos_rodape(self, f, t):
        for a, b, spr in self.passos:
            if a <= t < b:
                k, d = t - a, b - a
                al = janela(k, d, 0.3, 0.25)
                x = 46 - (1 - ease(k / 0.4)) * 80
                cola(f, spr, x, H - 120 - spr.shape[0], al)

    def prompt_card(self, f, t):
        a, b, chap, txt = self.prompt
        if not (a <= t < b):
            return
        k, d = t - a, b - a
        al = janela(k, d)
        n = int(clamp01((k - 0.35) / 1.4) * txt.shape[1])
        w = txt.shape[1] + 80
        hh = txt.shape[0] + 56
        box = caixa(w, hh, (30, 16, 8), 20, 245, borda=YEL, larg_borda=3)
        if n > 0:
            sobre(box, txt[:, :n], 40, 28)
        if (k * 2) % 1 < 0.6:
            cv2.rectangle(box, (40 + n + 4, 26), (40 + n + 8, 26 + txt.shape[0]), YEL + (255,), -1)
        x = 960 - w / 2
        y = 70 + (1 - ease(k / 0.35)) * -30
        cola(f, box, x, y, al)
        cola(f, chap, x + 30, y - chap.shape[0] + 10, al)

    def xp_pop(self, f, t):
        a, b, spr, moeda = self.xp
        if not (a <= t < b):
            return
        k, d = t - a, b - a
        al = janela(k, d, 0.2, 0.5)
        esc = 0.5 + 0.5 * ease_back(k / 0.45, 2.6)
        cy = 520 - ease(k / d) * 90
        cola_escala(f, spr, 1180, cy, esc, al)
        rng = np.random.default_rng(7)
        for i in range(10):
            ang = rng.uniform(0, 2 * math.pi)
            vel = rng.uniform(180, 380)
            kk = clamp01(k / 1.6)
            x = 1180 + math.cos(ang) * vel * ease(kk)
            y = cy + math.sin(ang) * vel * ease(kk) + 260 * kk * kk
            cola_escala(f, moeda, x, y, 0.8, al * (1 - kk))

    def medalha_tag(self, f, t):
        m0, m1, m2, bronze, prata, et_b, et_p = self.medalha
        if not (m0 <= t < m2):
            return
        segunda = t >= m1
        a0 = m1 if segunda else m0
        k = t - a0
        d = (m2 - m1) if segunda else (m1 - m0)
        med, et = (prata, et_p) if segunda else (bronze, et_b)
        al = janela(t - m0, m2 - m0, 0.3, 0.3)
        # etiqueta
        cx = 960 + 70
        cola_escala(f, et, cx, 40 + et.shape[0] / 2, 0.75 + 0.25 * ease_back(k / 0.4), al)
        # medalha cai e gira (giro da moeda: escala x = |cos|)
        ang = (1 - ease(k / 1.1)) * 3 * math.pi
        esx = max(0.06, abs(math.cos(ang)))
        y = 40 + 95 - (1 - ease_back(k / 0.6, 1.6)) * 160
        mx = cx - et.shape[1] / 2 - 70
        cola_escala(f, med, mx, y, esx, al, escy=1.0)
        # brilho
        if k > 1.2:
            s = ((k - 1.2) % 2.2) / 0.5
            if s < 1:
                cv2.line(f, (int(mx - 60 + 120 * s), int(y - 50)), (int(mx - 90 + 120 * s), int(y + 60)),
                         (255, 255, 255), 3, cv2.LINE_AA)

    def painel(self, f, t, p):
        for a, b, base, its in self.paineis:
            if a - 0.6 <= t < b + 0.6 and p > 0.01:
                x = 1364 + (1 - p) * 620
                y = 60
                card = base[0].copy()
                yy = base[1]
                vistos = [i for i, it in enumerate(its) if t >= it[0]]
                atual = vistos[-1] if vistos else -1
                # linha da trilha
                if len(its) > 1:
                    ytop, ybot = yy + 22, yy + 22 + (len(its) - 1) * PASSO_P
                    cv2.line(card, (54, ytop), (54, ybot), (100, 75, 55, 255), 4, cv2.LINE_AA)
                    if atual >= 0:
                        k = clamp01((t - its[atual][0]) / 0.5)
                        yfim = ytop + (max(0, atual - 1) + (k if atual > 0 else 0)) * PASSO_P
                        cv2.line(card, (54, ytop), (54, int(yfim)), YEL + (255,), 4, cv2.LINE_AA)
                for i, (ti, spr_n, spr_h, det) in enumerate(its):
                    cy = yy + i * PASSO_P
                    k = t - ti
                    if k >= 0:
                        e = ease(k / 0.4)
                        r = int(16 + 4 * (1 - ease(k / 0.3)) * (k < 0.3))
                        cv2.circle(card, (54, cy + 22), r + 3, (44, 22, 10, 255), -1, cv2.LINE_AA)
                        cv2.circle(card, (54, cy + 22), r, YEL + (255,), -1, cv2.LINE_AA)
                        cv2.polylines(card, [np.array([[46, cy + 22], [52, cy + 28], [63, cy + 15]], np.int32)],
                                      False, INK + (255,), 3, cv2.LINE_AA)
                        dx = int((1 - e) * 40)
                        tmp = np.zeros_like(card)
                        sobre(tmp, spr_h if i == atual else spr_n, 92 + dx, cy + 4)
                        sobre(tmp, det, 92 + dx, cy + 44)
                        tmp[:, :, 3] = (tmp[:, :, 3] * e).astype(np.uint8)
                        sobre(card, tmp, 0, 0)
                    else:
                        cv2.circle(card, (54, cy + 22), 14, (110, 84, 62, 255), 3, cv2.LINE_AA)
                cola(f, card, x, y, min(1.0, p * 1.4))

    # --- cartões de tela cheia
    def interludio(self, f, t, q):
        r = self.ativo_inter(t)
        if not r:
            return False
        a, b, tipo = r
        k, d = t - a, b - a
        al = janela(k, d, 0.35, 0.35)
        peq = cv2.resize(f, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
        peq = cv2.GaussianBlur(peq, (0, 0), 2)
        borr = cv2.resize(peq, (W, H), interpolation=cv2.INTER_LINEAR)
        escuro = (borr.astype(np.float32) * 0.35 + np.array(NAVY, np.float32) * 0.45)
        f[:] = (f.astype(np.float32) * (1 - al) + escuro * al).astype(np.uint8)
        if tipo not in self.inter_spr:
            self.inter_spr[tipo] = self.prepara_inter(tipo)
        S = self.inter_spr[tipo]
        esc = 0.94 + 0.06 * ease(k / 0.45)
        card = S['card']
        cola_escala(f, card, 960, 520, esc, al)
        getattr(self, 'inter_' + tipo)(f, k, d, al, S)
        return True

    def prepara_inter(self, tipo):
        w, h = 1500, 780
        card = caixa(w, h, (46, 22, 10), 34, 250, borda=(96, 70, 46), larg_borda=2)
        for x in range(30, w - 30, 40):
            for y in range(30, h - 30, 40):
                cv2.circle(card, (x, y), 1, (88, 64, 44, 255), -1, cv2.LINE_AA)
        cv2.rectangle(card, (40, 0), (w - 40, 6), YEL + (255,), -1)
        S = {'card': card}
        if tipo == 'titulo':
            S['chap'] = sprite_texto('NOVO NO MARKETPLACE CONNECT', 30, INK, fundo=YEL + (255,), pad=(18, 8), raio=10)
            S['big'] = sprite_texto('TREINO MAC', 190, WHITE, pad=(10, 0), contorno=6, cor_contorno=(30, 14, 6))
            S['sub'] = sprite_texto('Treinamento do zero com a IA', 58, YEL, pad=(0, 0), peso=800)
            S['c1'] = sprite_texto('ChatGPT', 38, WHITE, fundo=(80, 50, 28, 255), pad=(26, 12), raio=26)
            S['c2'] = sprite_texto('Claude', 38, WHITE, fundo=(80, 50, 28, 255), pad=(26, 12), raio=26)
            S['niv'] = sprite_texto('NÍVEL 1', 30, INK, fundo=YEL + (255,), pad=(14, 6), raio=8)
        elif tipo == 'zero':
            S['l1'] = sprite_texto('ADERIU AGORA?', 70, WHITE, pad=(0, 0))
            S['l2'] = sprite_texto('TEM DÚVIDAS?', 70, WHITE, pad=(0, 0))
            S['l3'] = sprite_texto('COMECE DO ZERO', 150, YEL, pad=(10, 0), contorno=6, cor_contorno=(30, 14, 6))
            S['nos'] = [sprite_texto(x, 30, WHITE, pad=(0, 0)) for x in ('NÍVEL 1', 'NÍVEL 2', 'NÍVEL 3', 'EXPERT')]
        elif tipo == 'versus':
            S['tit'] = sprite_texto('TREINO NA PRÁTICA', 92, WHITE, pad=(0, 0))
            S['e'] = caixa(600, 330, (60, 40, 30), 26, 255, borda=(110, 90, 75))
            S['d'] = caixa(600, 330, (40, 70, 95), 26, 255, borda=YEL, larg_borda=5)
            S['e_t'] = sprite_texto('Assistir vídeo, copiar o prompt e torcer para funcionar', 40, GREY, pad=(0, 0),
                                    larg_max=500, alinha='centro', peso=800)
            S['d_t'] = sprite_texto('Usar a plataforma de verdade, missão por missão', 40, WHITE, pad=(0, 0),
                                    larg_max=500, alinha='centro', peso=800)
            S['x'] = icone('x', 120, WHITE, RED)
            S['ok'] = icone('check', 120, INK, GREEN)
        elif tipo == 'programador':
            S['l1'] = sprite_texto('NÃO PRECISA SER', 96, WHITE, pad=(0, 0))
            S['l2'] = sprite_texto('PROGRAMADOR', 190, YEL, pad=(10, 0), contorno=6, cor_contorno=(30, 14, 6))
            S['l3'] = sprite_texto('Só precisa da licença do Marketplace Connect', 50, WHITE, pad=(0, 0), peso=700)
        return S

    def inter_titulo(self, f, k, d, al, S):
        cola_escala(f, S['chap'], 960, 250 - (1 - ease(k / 0.4)) * 30, 1.0, al * ease(k / 0.3))
        kb = k - 0.35
        if kb > 0:
            esc = ease_back(kb / 0.5, 2.2)
            cola_escala(f, S['big'], 960, 410, max(0.05, esc), al)
        ks = k - 1.0
        if ks > 0:
            cola_escala(f, S['sub'], 960, 560 + (1 - ease(ks / 0.4)) * 30, 1.0, al * ease(ks / 0.4))
        kc = k - 1.6
        if kc > 0:
            w = S['c1'].shape[1] + S['c2'].shape[1] + 30
            x1 = 960 - w / 2 + S['c1'].shape[1] / 2
            x2 = 960 + w / 2 - S['c2'].shape[1] / 2
            cola_escala(f, S['c1'], x1, 665 + (1 - ease(kc / 0.4)) * 40, 1.0, al * ease(kc / 0.4))
            kc2 = kc - 0.25
            if kc2 > 0:
                cola_escala(f, S['c2'], x2, 665 + (1 - ease(kc2 / 0.4)) * 40, 1.0, al * ease(kc2 / 0.4))
        kx = k - 2.4
        if kx > 0:
            prog = ease_io(kx / 2.2)
            x0, x1, y = 560, 1360, 812
            ov = f.copy()
            cv2.rectangle(ov, (x0, y - 12), (x1, y + 12), (80, 52, 30), -1, cv2.LINE_AA)
            cv2.rectangle(ov, (x0, y - 12), (int(x0 + (x1 - x0) * prog), y + 12), YEL, -1, cv2.LINE_AA)
            a2 = al * ease(kx / 0.3)
            f[:] = cv2.addWeighted(f, 1 - a2, ov, a2, 0)
            cola(f, S['niv'], x0 - S['niv'].shape[1] - 20, y - S['niv'].shape[0] / 2, a2)
            xp = sprite_texto('%d XP' % int(round(prog * 100)), 30, WHITE, pad=(0, 0))
            cola(f, xp, x1 + 20, y - xp.shape[0] / 2, a2)

    def inter_zero(self, f, k, d, al, S):
        for i, (nome, t0, y) in enumerate((('l1', 0.2, 250), ('l2', 1.3, 340))):
            kk = k - t0
            if kk > 0:
                cola_escala(f, S[nome], 960, y, 0.8 + 0.2 * ease_back(kk / 0.35), al * ease(kk / 0.3))
        k3 = k - 2.3
        if k3 > 0:
            cola_escala(f, S['l3'], 960, 490, max(0.05, ease_back(k3 / 0.5, 2.4)), al)
        k4 = k - 3.6
        if k4 > 0:
            xs = [480, 800, 1120, 1440]
            y = 720
            a2 = al * ease(k4 / 0.3)
            ov = f.copy()
            cv2.line(ov, (xs[0], y), (xs[-1], y), (90, 66, 44), 6, cv2.LINE_AA)
            prog = clamp01((k4 - 0.4) / 2.6) * 3
            cv2.line(ov, (xs[0], y), (int(xs[0] + (xs[-1] - xs[0]) * prog / 3), y), YEL, 6, cv2.LINE_AA)
            for i, x in enumerate(xs):
                on = prog >= i - 0.02
                cv2.circle(ov, (x, y), 30, YEL if on else (90, 66, 44), -1, cv2.LINE_AA)
                if i == 0 or on:
                    cv2.circle(ov, (x, y), 30, YEL, -1, cv2.LINE_AA)
            f[:] = cv2.addWeighted(f, 1 - a2, ov, a2, 0)
            for i, x in enumerate(xs):
                cola_escala(f, S['nos'][i], x, y + 62, 1.0, a2 * (1.0 if prog >= i - 0.02 else 0.45))
                if prog >= i - 0.02:
                    cv2.polylines(f, [np.array([[x - 12, y], [x - 3, y + 9], [x + 13, y - 9]], np.int32)], False,
                                  INK, 5, cv2.LINE_AA)

    def inter_versus(self, f, k, d, al, S):
        cola_escala(f, S['tit'], 960, 230, 0.85 + 0.15 * ease_back(k / 0.4), al * ease(k / 0.3))
        ke = k - 0.5
        if ke > 0:
            ae = al * ease(ke / 0.35)
            cola_escala(f, S['e'], 600, 560 + (1 - ease(ke / 0.4)) * 40, 1.0, ae)
            cola_escala(f, S['e_t'], 600, 590 + (1 - ease(ke / 0.4)) * 40, 1.0, ae)
            kx = ke - 1.2
            if kx > 0:
                cola_escala(f, S['x'], 600, 420, max(0.05, ease_back(kx / 0.35, 2.6)), al)
        kd = k - 2.6
        if kd > 0:
            ad = al * ease(kd / 0.35)
            esc = 0.9 + 0.1 * ease_back(kd / 0.45)
            cola_escala(f, S['d'], 1320, 560, esc, ad)
            cola_escala(f, S['d_t'], 1320, 590, esc, ad)
            ko = kd - 1.0
            if ko > 0:
                cola_escala(f, S['ok'], 1320, 420, max(0.05, ease_back(ko / 0.35, 2.6)), al)

    def inter_programador(self, f, k, d, al, S):
        cola_escala(f, S['l1'], 960, 300, 0.85 + 0.15 * ease_back(k / 0.4), al * ease(k / 0.3))
        k2 = k - 0.7
        if k2 > 0:
            cola_escala(f, S['l2'], 960, 470, max(0.05, 1.6 - 0.6 * ease(k2 / 0.35)), al * ease(k2 / 0.2))
        k3 = k - 3.6
        if k3 > 0:
            cola_escala(f, S['l3'], 960, 660 + (1 - ease(k3 / 0.4)) * 30, 1.0, al * ease(k3 / 0.4))


# ---------------------------------------------------------------- quadro do miolo
def quadro(n, q, palco, cam):
    t = n / FPS
    f, qq = palco.compoe(n, q)
    p = palco.p[n]
    em_inter = cam.interludio(f, t, qq)
    if not em_inter:
        cam.etiquetas(f, t, p)
        cam.medalha_tag(f, t)
        cam.xp_pop(f, t)
        cam.prompt_card(f, t)
        cam.painel(f, t, p)
        cam.passos_rodape(f, t)
    cam.capitulo(f, t)
    palco.camera(f, qq)
    return f


def encoder(caminho, audio=None, crf=19):
    cmd = [FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H),
           '-r', str(FPS), '-i', '-']
    if audio:
        cmd += ['-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p',
            '-video_track_timescale', '15360', '-movflags', '+faststart', caminho]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def parte(args):
    n0, n1, caminho = args
    palco, cam = Palco(), Camadas()
    alvo0 = int(round(fonte_t(n0 / FPS) * 30))
    br = Bruto(ini=max(0, alvo0 - 2))
    enc = encoder(caminho)
    for n in range(n0, n1):
        idx = int(round(fonte_t(n / FPS) * 30))
        q = br.quadro(idx)
        enc.stdin.write(quadro(n, q, palco, cam).tobytes())
    enc.stdin.close(); enc.wait()
    br.l.fecha()
    return caminho


def cartela_final(n, bg, S):
    f = bg[40:40 + H, 40:40 + W].copy()
    t = n / FPS
    a = ease(t / 0.5)
    cola_escala(f, S['chap'], 960, 300 - (1 - a) * 30, 1.0, a)
    cola_escala(f, S['l1'], 960, 430, max(0.05, ease_back((t - 0.2) / 0.5)), ease((t - 0.2) / 0.3))
    cola_escala(f, S['l2'], 960, 560, 1.0, ease((t - 0.6) / 0.4))
    pulso = 1 + 0.04 * math.sin(max(0, t - 1.2) * 4)
    cola_escala(f, S['bt'], 960, 720, pulso * (0.8 + 0.2 * ease_back((t - 1.0) / 0.4)), ease((t - 1.0) / 0.3))
    cola_escala(f, S['l3'], 960, 830, 1.0, ease((t - 1.4) / 0.4))
    fim = clamp01((t - (FINAL_DUR - 0.8)) / 0.8)
    if fim > 0:
        f = (f.astype(np.float32) * (1 - fim)).astype(np.uint8)
    return f


def sprites_cartela():
    return {'chap': sprite_texto('MARKETPLACE CONNECT', 32, INK, fundo=YEL + (255,), pad=(18, 8), raio=10),
            'l1': sprite_texto('TREINO MAC', 150, WHITE, pad=(10, 0), contorno=6, cor_contorno=(30, 14, 6)),
            'l2': sprite_texto('Comece a trilha no nível 1', 60, YEL, pad=(0, 0), peso=800),
            'bt': sprite_texto('SAIBA MAIS', 48, INK, fundo=YEL + (255,), pad=(46, 18), raio=40),
            'l3': sprite_texto('link na descrição do vídeo', 34, GREY, pad=(0, 0), peso=600)}


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if modo == 'sfx':
        json.dump(Camadas().eventos_sfx(), open(os.path.join(T, 'sfx.json'), 'w'))
        print('sfx ok')
        return
    if modo == 'quadros':
        ts = [float(x) for x in sys.argv[2].split(',')]
        palco, cam = Palco(), Camadas()
        for t in ts:
            n = int(t * FPS)
            br = Bruto(ini=int(round(fonte_t(t) * 30)))
            q = br.quadro(int(round(fonte_t(t) * 30)))
            br.l.fecha()
            cv2.imwrite(os.path.join(T, 'q-%07.2f.jpg' % t), quadro(n, q, palco, cam), [cv2.IMWRITE_JPEG_QUALITY, 88])
        return
    if modo == 'teste':
        a, b = float(sys.argv[2]), float(sys.argv[3])
        out = os.path.join(V, 'teste.mp4')
        parte((int(a * FPS), int(b * FPS), out))
        print(out)
        return
    if modo == 'cartela':
        bg, S = fundo_marca(), sprites_cartela()
        enc = encoder(os.path.join(V, 'parte-zz.mp4'))
        for n in range(int(FINAL_DUR * FPS)):
            enc.stdin.write(cartela_final(n, bg, S).tobytes())
        enc.stdin.close(); enc.wait()
        return
    # vídeo inteiro em pedaços paralelos
    NP = 6
    lim = np.linspace(0, N, NP + 1).astype(int)
    partes = [(lim[i], lim[i + 1], os.path.join(V, 'parte-%02d.mp4' % i)) for i in range(NP)]
    with Pool(NP) as pool:
        for c in pool.imap_unordered(parte, partes):
            print('ok', c, flush=True)
    bg, S = fundo_marca(), sprites_cartela()
    enc = encoder(os.path.join(V, 'parte-zz.mp4'))
    for n in range(int(FINAL_DUR * FPS)):
        enc.stdin.write(cartela_final(n, bg, S).tobytes())
    enc.stdin.close(); enc.wait()
    print('miolo %.2f s, %d quadros' % (DUR, N))
    tempos()


def tempos():
    ab = os.path.join(V, 'abertura.mp4')
    nab = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                              'stream=nb_read_frames', '-of', 'csv=p=0', ab], capture_output=True, text=True).stdout)
    json.dump({'abertura_s': nab / FPS, 'miolo_q': N, 'miolo_s': N / FPS, 'final_s': FINAL_DUR},
              open(os.path.join(T, 'tempos.json'), 'w'))


def junta():
    """abertura (reencodada no mesmo padrão) + partes + cartela + áudio -> videos/final.mp4"""
    ab = os.path.join(V, 'parte-aa.mp4')
    subprocess.run([FF, '-v', 'error', '-y', '-i', os.path.join(V, 'abertura.mp4'), '-an', '-c:v', 'libx264',
                    '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30',
                    '-video_track_timescale', '15360', ab], check=True)
    lista = os.path.join(T, 'partes.txt')
    with open(lista, 'w') as f:
        for p in ['parte-aa.mp4'] + ['parte-%02d.mp4' % i for i in range(6)] + ['parte-zz.mp4']:
            f.write("file '%s'\n" % os.path.join(V, p))
    subprocess.run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista,
                    '-i', os.path.join(T, 'audio_final.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                    os.path.join(V, 'final.mp4')], check=True)
    print(os.path.join(V, 'final.mp4'))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'junta':
        junta()
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == 'tempos':
        tempos()
        sys.exit(0)
    main()
