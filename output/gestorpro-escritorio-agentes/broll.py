#!/usr/bin/env python3
"""B-roll animado do vídeo "Escritório de Agentes no Mercado Livre" (GestorPro).

Cada cena vira um MP4 1920x1080 @30 fps, sem áudio, em videos/broll/, mais um
manifest.json. Quadros desenhados em 2x (3840x2160) com PIL e reduzidos, enviados
direto ao ffmpeg por pipe (nenhum PNG vai para o disco).

  python3 broll.py            renderiza todas as cenas
  python3 broll.py 3 5        só as cenas 3 e 5
  python3 broll.py folha      folha de quadros de cada clipe em trab/broll-folha-N.jpg

Nada de dado real de cliente: avatares sem nome, produtos como ícones.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, 'videos', 'broll')
FONT = os.path.join(AQUI, '..', 'reel-explica-marketplace-connect', 'assets', 'Inter.ttf')
EMOJI = '/System/Library/Fonts/Apple Color Emoji.ttc'
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
W, H, FPS, K = 1920, 1080, 30, 2

INK = (11, 11, 12); YEL = (245, 196, 0); BLUE = (47, 107, 255); WHITE = (245, 246, 248)
GRAY = (150, 156, 168); CARD = (22, 24, 29); CARD2 = (32, 35, 42); LINE = (52, 56, 66)
GREEN = (34, 197, 94); RED = (239, 68, 68); PURPLE = (168, 85, 247); CYAN = (56, 189, 248)
ORANGE = (251, 146, 60)


# ------------------------------------------------------------------ util
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, dur): return clamp((t - t0) / dur) if dur > 0 else float(t >= t0)
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x * x * x if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eback(x, s=1.7):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2
def lerp(a, b, u): return a + (b - a) * u
def smooth(a, b, x):
    u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u)
def bez(p0, p1, p2, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
            (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1])
def real(v): return 'R$ ' + ('%.2f' % v).replace('.', ',')

_fc = {}
def font(px, w='Bold'):
    k = (px, w)
    if k not in _fc:
        f = ImageFont.truetype(FONT, px)
        f.set_variation_by_name(w)
        _fc[k] = f
    return _fc[k]
def tw(txt, px, w='Bold'): return font(int(round(px * K)), w).getlength(txt) / K


class P:
    """Desenho em coordenadas 1x (com origem, escala e opacidade herdadas) sobre o quadro 2x."""
    def __init__(s, img, ox=0.0, oy=0.0, sc=1.0, a=1.0, d=None):
        s.img = img; s.d = d or ImageDraw.Draw(img, 'RGBA')
        s.ox, s.oy, s.sc, s.a = ox, oy, sc, a
    def at(s, x, y, sc=1.0, a=1.0):
        return P(s.img, s.ox + x * s.sc, s.oy + y * s.sc, s.sc * sc, s.a * a, s.d)
    def pt(s, x, y): return ((s.ox + x * s.sc) * K, (s.oy + y * s.sc) * K)
    def L(s, v): return v * s.sc * K
    def col(s, c, a=1.0):
        if c is None: return None
        base = c[3] / 255 if len(c) == 4 else 1.0
        return (int(c[0]), int(c[1]), int(c[2]), int(round(255 * clamp(base * a * s.a))))
    def wd(s, w): return max(1, int(round(s.L(w))))
    def rr(s, x0, y0, x1, y1, r, fill=None, outline=None, w=0, a=1.0):
        X0, Y0 = s.pt(x0, y0); X1, Y1 = s.pt(x1, y1)
        if X1 - X0 < 2 or Y1 - Y0 < 2 or s.a * a <= 0.003: return
        X0, Y0, X1, Y1 = int(round(X0)), int(round(Y0)), int(round(X1)), int(round(Y1))
        rad = int(min(s.L(r), (X1 - X0) // 2 - 1, (Y1 - Y0) // 2 - 1))
        s.d.rounded_rectangle([X0, Y0, X1, Y1], max(0, rad), fill=s.col(fill, a),
                              outline=s.col(outline, a), width=s.wd(w) if outline else 0)
    def circ(s, cx, cy, r, fill=None, outline=None, w=0, a=1.0):
        X, Y = s.pt(cx, cy); R = s.L(r)
        if R < 0.7 or s.a * a <= 0.003: return
        s.d.ellipse([X - R, Y - R, X + R, Y + R], fill=s.col(fill, a), outline=s.col(outline, a),
                    width=s.wd(w) if outline else 0)
    def ell(s, x0, y0, x1, y1, fill, a=1.0):
        X0, Y0 = s.pt(x0, y0); X1, Y1 = s.pt(x1, y1)
        if X1 - X0 < 1 or Y1 - Y0 < 1: return
        s.d.ellipse([X0, Y0, X1, Y1], fill=s.col(fill, a))
    def line(s, pts, fill, w, a=1.0):
        if s.a * a <= 0.003 or len(pts) < 2: return
        s.d.line([s.pt(x, y) for x, y in pts], fill=s.col(fill, a), width=s.wd(w), joint='curve')
    def poly(s, pts, fill=None, outline=None, w=0, a=1.0):
        if s.a * a <= 0.003: return
        s.d.polygon([s.pt(x, y) for x, y in pts], fill=s.col(fill, a), outline=s.col(outline, a),
                    width=s.wd(w) if outline else 0)
    def arc(s, cx, cy, r, a0, a1, fill, w, a=1.0):
        X, Y = s.pt(cx, cy); R = s.L(r)
        if R < 1 or s.a * a <= 0.003: return
        s.d.arc([X - R, Y - R, X + R, Y + R], a0, a1, fill=s.col(fill, a), width=s.wd(w))
    def text(s, x, y, txt, px, w='Bold', fill=WHITE, anchor='la', a=1.0):
        size = int(round(s.L(px)))
        if size < 4 or s.a * a <= 0.003: return
        s.d.text(s.pt(x, y), txt, font=font(size, w), fill=s.col(fill, a), anchor=anchor)
    def image(s, im, x, y, a=1.0):
        """cola uma imagem RGBA (já em 2x) com o canto superior esquerdo em (x, y)."""
        if s.a * a <= 0.01: return
        if abs(s.sc - 1) > 0.01:
            im = im.resize((max(1, int(im.width * s.sc)), max(1, int(im.height * s.sc))), Image.LANCZOS)
        al = im.getchannel('A')
        if s.a * a < 0.999:
            al = al.point(lambda v, k=s.a * a: int(v * k))
        X, Y = s.pt(x, y)
        s.img.paste(im.convert('RGB'), (int(X), int(Y)), al)


def dashed(p, x0, y0, x1, y1, col, w, dash=14, gap=10, a=1.0):
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1: return
    i = 0
    while True:
        s0 = i * (dash + gap) / L
        if s0 >= 1: break
        s1 = min(1, (i * (dash + gap) + dash) / L)
        p.line([(lerp(x0, x1, s0), lerp(y0, y1, s0)), (lerp(x0, x1, s1), lerp(y0, y1, s1))], col, w, a)
        i += 1


def wrap(txt, px, w, maxw):
    lines, cur = [], ''
    for word in txt.split(' '):
        tst = (cur + ' ' + word).strip()
        if tw(tst, px, w) <= maxw or not cur:
            cur = tst
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines


def emoji(ch, px):
    try:
        f = ImageFont.truetype(EMOJI, 160)
        im = Image.new('RGBA', (220, 220), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((110, 110), ch, font=f, embedded_color=True, anchor='mm')
        im = im.crop(im.getbbox())
        s = px * K / im.width
        return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    except Exception:
        return None


# ------------------------------------------------------------------ ícones (centrados na origem)
def ic_box(p, s, c, a=1.0):
    h = s / 2
    p.rr(-h, -h * .7, h, h * .85, s * .1, outline=c, w=s * .11, a=a)
    p.line([(-h, -h * .15), (h, -h * .15)], c, s * .1, a)
    p.line([(0, -h * .7), (0, -h * .15)], c, s * .1, a)
def ic_tag(p, s, c, a=1.0):
    h = s / 2
    p.poly([(-h, -h * .62), (h * .25, -h * .62), (h, 0), (h * .25, h * .62), (-h, h * .62)], outline=c, w=s * .1, a=a)
    p.circ(-h * .45, 0, s * .1, fill=c, a=a)
def ic_person(p, s, c, a=1.0):
    p.circ(0, -s * .2, s * .2, fill=c, a=a)
    p.rr(-s * .38, s * .06, s * .38, s * .55, s * .24, fill=c, a=a)
def ic_bubble(p, s, c, a=1.0):
    h = s / 2
    p.rr(-h, -h * .7, h, h * .45, s * .2, outline=c, w=s * .1, a=a)
    p.poly([(-h * .45, h * .4), (-h * .7, h * .9), (-h * .05, h * .42)], fill=c, a=a)
def ic_money(p, s, c, a=1.0): p.text(0, 0, 'R$', s * .55, 'ExtraBold', c, 'mm', a)
def ic_pct(p, s, c, a=1.0): p.text(0, 0, '%', s * .8, 'ExtraBold', c, 'mm', a)
def ic_card(p, s, c, a=1.0):
    h = s / 2
    p.rr(-h, -h * .7, h, h * .7, s * .12, outline=c, w=s * .1, a=a)
    p.line([(-h * .55, -h * .15), (h * .55, -h * .15)], c, s * .09, a)
    p.line([(-h * .55, h * .25), (h * .2, h * .25)], c, s * .09, a)
def ic_stack(p, s, c, a=1.0):
    h = s / 2
    for i, y in enumerate((-h * .55, 0, h * .55)):
        p.rr(-h * (.85 - i * .1), y - h * .2, h * (.85 - i * .1), y + h * .2, s * .06, fill=c, a=a)
def ic_check(p, s, c, a=1.0):
    h = s / 2
    p.line([(-h * .55, 0), (-h * .12, h * .42), (h * .6, -h * .45)], c, s * .16, a)
def ic_shield(p, s, c, a=1.0):
    h = s / 2
    p.poly([(0, -h), (h * .85, -h * .6), (h * .72, h * .35), (0, h), (-h * .72, h * .35), (-h * .85, -h * .6)],
           outline=c, w=s * .1, a=a)
    ic_check(p.at(0, 0), s * .6, c, a)
def ic_bag(p, s, c, a=1.0):
    h = s / 2
    p.arc(0, -h * .25, h * .38, 180, 360, c, s * .09, a)
    p.rr(-h * .75, -h * .25, h * .75, h * .85, s * .1, fill=c, a=a)
ICON = dict(box=ic_box, tag=ic_tag, person=ic_person, bubble=ic_bubble, money=ic_money, pct=ic_pct,
            card=ic_card, stack=ic_stack, check=ic_check, shield=ic_shield, bag=ic_bag)


# ------------------------------------------------------------------ peças comuns
def make_bg():
    w, h = W * K, H * K
    yy, xx = np.mgrid[0:h:4, 0:w:4].astype(np.float32) * 1.0
    base = np.zeros(xx.shape + (3,), np.float32) + np.array(INK, np.float32)
    def glow(cx, cy, r, col, s):
        d = ((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r)
        return (np.exp(-d) * s)[..., None] * np.array(col, np.float32)
    base += glow(w * .88, h * .05, w * .42, BLUE, .22)
    base += glow(w * .08, h * 1.0, w * .32, YEL, .07)
    v = ((xx / w - .5) ** 2 + (yy / h - .5) ** 2)
    base *= (1 - .35 * v)[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    d = ImageDraw.Draw(img, 'RGBA')
    for y in range(24 * K, h, 48 * K):
        for x in range(24 * K, w, 48 * K):
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 255, 13))
    return img


def headline(p, t, parts, y=112, px=56):
    a = eo(prog(t, 0.0, 0.45)); dy = 24 * (1 - a)
    total = sum(tw(s, px, 'ExtraBold') for s, _ in parts)
    x = 960 - total / 2
    for s, col in parts:
        p.text(x, y + dy, s, px, 'ExtraBold', col, 'lm', a=a)
        x += tw(s, px, 'ExtraBold')
    # traço amarelo embaixo
    lw = 90 * eo(prog(t, 0.15, 0.4))
    p.rr(960 - lw / 2, y + 44, 960 + lw / 2, y + 50, 3, fill=YEL, a=a)


def brand(p):
    t1, t2 = 'GestorPro', ' · escritório de agentes'
    w = tw(t1, 21, 'Bold') + tw(t2, 21, 'Regular') + 64
    p.rr(44, 1004, 44 + w, 1048, 22, fill=(20, 22, 27, 230), outline=LINE, w=1.5)
    p.circ(68, 1026, 7, fill=YEL)
    p.text(84, 1026, t1, 21, 'Bold', WHITE, 'lm')
    p.text(84 + tw(t1, 21, 'Bold'), 1026, t2, 21, 'Regular', GRAY, 'lm')


def selo(p, x, y, txt, t, t0, fill=YEL, fg=INK, px=28, icon=None, dot=False):
    k = prog(t, t0, 0.45)
    if k <= 0: return
    s = max(0.05, eback(k, 2.2))
    q = p.at(x, y, sc=s, a=clamp(k * 4))
    w = tw(txt, px, 'ExtraBold') + 64 + (44 if (icon or dot) else 0)
    q.rr(-w / 2 - 6, -38, w / 2 + 6, 38, 38, fill=fill + (60,))
    q.rr(-w / 2, -32, w / 2, 32, 32, fill=fill)
    tx = -w / 2 + 32
    if dot:
        pulse = (t * 1.6) % 1
        q.circ(tx + 10, 0, 10 + 14 * pulse, fill=fg + (int(120 * (1 - pulse)),))
        q.circ(tx + 10, 0, 9, fill=fg)
        tx += 44
    elif icon:
        ICON[icon](q.at(tx + 14, 0), 34, fg)
        tx += 44
    q.text(tx, 1, txt, px, 'ExtraBold', fg, 'lm')


def chip(p, x, y, txt, icon, col, a=1.0, px=25):
    w = tw(txt, px, 'SemiBold') + 96
    p.rr(x - w / 2, y - 31, x + w / 2, y + 31, 31, fill=(28, 31, 38, 240), outline=(70, 76, 90), w=1.5, a=a)
    p.circ(x - w / 2 + 33, y, 21, fill=col, a=a)
    ICON[icon](p.at(x - w / 2 + 33, y), 22, INK, a)
    p.text(x - w / 2 + 66, y, txt, px, 'SemiBold', WHITE, 'lm', a=a)


def blink(t, at=(1.3, 3.25)):
    for b in at:
        d = abs(t - b)
        if d < 0.08: return 0.12 + 0.88 * d / 0.08
    return 1.0


def robot(p, t, part='all', eye=YEL, arms='type', look=0.0, variant=1, talk=0.0):
    WH = (236, 239, 245); WH2 = (208, 214, 225); DK = (18, 20, 26)
    if variant == 2:
        WH = (210, 222, 242); WH2 = (176, 192, 220)
    if part in ('all', 'body'):
        pulse = 0.5 + 0.5 * math.sin(t * 6)
        if variant == 1:
            p.line([(0, -170), (0, -206)], WH2, 7)
            p.circ(0, -214, 12 + 9 * pulse, fill=eye + (55,))
            p.circ(0, -214, 12, fill=eye)
        else:
            for sx in (-1, 1):
                p.line([(sx * 40, -165), (sx * 62, -200)], WH2, 6)
                p.circ(sx * 62, -204, 9, fill=eye)
        p.circ(-102, -92, 16, fill=WH2); p.circ(102, -92, 16, fill=WH2)
        if variant == 1:
            p.rr(-100, -172, 100, -12, 52, fill=WH)
        else:
            p.circ(0, -92, 96, fill=WH)
        p.rr(-75, -136, 75, -48, 38, fill=DK)
        bl = blink(t)
        for ex in (-34, 34):
            x = ex + look
            p.circ(x, -92, 24 + 4 * talk, fill=eye + (45 + int(70 * talk),))
            hh = 15 * bl
            p.ell(x - 15, -92 - hh, x + 15, -92 + hh, fill=eye)
        if variant == 1:
            p.arc(look * .5, -78, 15, 35, 145, eye, 4)
        p.rr(-22, -16, 22, 16, 6, fill=WH2)
        p.rr(-92, 10, 92, 196, 44, fill=WH)
        p.rr(-46, 48, 46, 112, 16, fill=DK)
        for i, cx in enumerate((-22, 0, 22)):
            on = int(t * 5) % 3 == i
            p.circ(cx, 80, 8, fill=eye if on else (70, 76, 90))
    if part in ('all', 'arms'):
        sides = []
        if arms == 'type':
            for sx, ph in ((-1, 0.0), (1, math.pi)):
                dy = 7 * math.sin(t * 2 * math.pi * 4 + ph)
                sides.append([(sx * 86, 52), (sx * 128, 140), (sx * 58, 186 + dy)])
        elif arms == 'idle':
            for sx in (-1, 1):
                sw = 4 * math.sin(t * 2.4 + sx)
                sides.append([(sx * 86, 52), (sx * 118, 128), (sx * 108 + sw, 194)])
        elif arms == 'point':
            sw = 4 * math.sin(t * 2.4)
            sides.append([(-86, 52), (-118, 128), (-108 + sw, 194)])
            wv = 6 * math.sin(t * 7)
            sides.append([(86, 52), (150, 30), (196 + wv, -26)])
        for pts in sides:
            p.line(pts, WH2, 25)
            for j in range(2): p.circ(pts[j][0], pts[j][1], 12.5, fill=WH2)
            p.circ(pts[2][0], pts[2][1], 20, fill=WH)


# ------------------------------------------------------------------ cenas
CHIPS1 = [('Pedido separado', 'box', GREEN), ('Etiqueta emitida', 'tag', CYAN),
          ('Mensagem enviada', 'bubble', BLUE), ('Pergunta respondida', 'bubble', PURPLE),
          ('Preço ajustado', 'money', YEL), ('Estoque conferido', 'stack', ORANGE),
          ('Promoção revisada', 'pct', GREEN)]

def s1(p, t, D):
    headline(p, t, [('Seus agentes ', WHITE), ('sempre trabalhando', YEL)])
    k = eo(prog(t, 0.05, 0.5))
    r = p.at(640, 555 + 50 * (1 - k), a=k)
    robot(r, t, 'body', look=6)
    q = p.at(0, 30 * (1 - k), a=k)
    q.rr(330, 742, 1250, 772, 12, fill=(50, 54, 66))
    q.rr(360, 772, 1220, 910, 10, fill=(27, 30, 37))
    q.rr(360, 772, 1220, 780, 0, fill=(0, 0, 0, 70))
    # monitor
    km = prog(t, 0.2, 0.5)
    if km > 0:
        m = p.at(990, 600, sc=max(.05, eback(km)), a=clamp(km * 3))
        m.rr(-182, -132, 182, 112, 26, outline=BLUE + (70,), w=8)
        m.rr(-172, -122, 172, 102, 20, fill=(19, 22, 29), outline=(66, 72, 88), w=4)
        m.rr(-150, -102, 150, -78, 9, fill=(36, 41, 52))
        for i, c in enumerate((RED, YEL, GREEN)): m.circ(-134 + i * 18, -90, 5, fill=c)
        off = (t * 70) % 40
        base = int(t * 70 // 40)
        lens = [190, 140, 215, 120, 175, 160, 105, 200]
        cols = [GREEN, BLUE, YEL, PURPLE]
        for i in range(7):
            y = -50 + i * 40 - off
            if y < -62 or y > 84: continue
            j = i + base
            fa = clamp((y + 62) / 20) * clamp((84 - y) / 20)
            m.circ(-132, y, 7, fill=cols[j % 4], a=fa)
            m.rr(-114, y - 8, -114 + lens[j % 8], y + 8, 8, fill=(60, 66, 80), a=fa)
            m.rr(-114, y - 8, -114 + lens[j % 8] * (0.35 + 0.65 * ((j * 37) % 10) / 10), y + 8, 8,
                 fill=cols[j % 4] + (90,), a=fa)
        m.rr(-14, 102, 14, 150, 4, fill=(62, 66, 78))
        m.rr(-64, 144, 64, 156, 6, fill=(62, 66, 78))
    q.rr(545, 730, 735, 748, 7, fill=(80, 86, 100))
    for i in range(9): q.rr(556 + i * 20, 735, 570 + i * 20, 743, 2, fill=(110, 117, 132))
    robot(r, t, 'arms', arms='type')
    # tarefas saindo do monitor
    for i, (txt, ic, col) in enumerate(CHIPS1):
        t0 = 0.75 + i * 0.48
        u = prog(t, t0, 1.75)
        if u <= 0 or u >= 1: continue
        ly = (390, 560, 470, 640)[i % 4]
        x, y = lerp(1170, 1560, eo(u)), ly - 40 * eo(u)
        a = clamp(u / 0.15) * clamp((1 - u) / 0.25)
        chip(p.at(0, 0, a=a), x, y, txt, ic, col)
    selo(p, 330, 300, 'TRABALHANDO 24H', t, 0.55, dot=True)


PROD2 = [(YEL, 'bag'), (BLUE, 'tag'), (GREEN, 'box')]

def s2(p, t, D):
    headline(p, t, [('A IA olha o cliente e ', WHITE), ('sugere produtos', YEL)])
    # card do cliente
    k = eo(prog(t, 0.05, 0.5))
    c = p.at(400 - 60 * (1 - k), 600, a=k)
    c.rr(-210, -220, 210, 220, 30, fill=CARD, outline=LINE, w=2)
    c.circ(0, -122, 64, fill=(52, 58, 72))
    ic_person(c.at(0, -118), 78, (150, 160, 180))
    c.text(0, -22, 'Cliente recorrente', 30, 'Bold', WHITE, 'mm')
    c.text(0, 16, 'Compra com frequência', 22, 'Regular', GRAY, 'mm')
    for i in range(3):
        ka = eo(prog(t, 0.35 + i * 0.15, 0.35))
        y = 72 + i * 48
        c.rr(-170, y - 18, -134, y + 18, 9, fill=(46, 51, 63), a=ka)
        ic_bag(c.at(-152, y), 22, (150, 160, 180), ka)
        c.rr(-118, y - 7, -118 + (190, 150, 210)[i] * ka, y + 7, 7, fill=(64, 70, 84), a=ka)
        c.circ(150, y, 13, fill=GREEN, a=ka)
        ic_check(c.at(150, y), 18, INK, ka)
    # fluxo cliente -> IA
    if t > 0.6:
        for j in range(4):
            u = (t * 0.9 + j / 4) % 1
            x = lerp(620, 860, u)
            c2 = p.at(0, 0, a=clamp((t - 0.6) * 3) * math.sin(u * math.pi))
            c2.circ(x, 600, 9, fill=YEL + (70,)); c2.circ(x, 600, 5, fill=YEL)
    p.line([(620, 600), (860, 600)], LINE, 3, a=k)
    # nó da IA
    kn = prog(t, 0.3, 0.5)
    if kn > 0:
        n = p.at(960, 600, sc=max(.05, eback(kn)), a=clamp(kn * 3))
        pulse = (t * 1.1) % 1
        n.circ(0, 0, 96 + 70 * pulse, outline=BLUE, w=3, a=(1 - pulse) * .7)
        n.circ(0, 0, 112, fill=BLUE + (40,))
        n.circ(0, 0, 94, fill=(18, 24, 40), outline=BLUE, w=5)
        rot = t * 70
        for s0 in range(0, 360, 45):
            n.arc(0, 0, 122, s0 + rot, s0 + rot + 24, YEL, 5)
        n.text(0, -6, 'IA', 66, 'Black', YEL, 'mm')
        n.text(0, 46, 'analisando', 18, 'SemiBold', GRAY, 'mm')
    # cards de produto
    for i, (col, ic) in enumerate(PROD2):
        cy = 365 + i * 235
        kc = eo(prog(t, 1.3 + i * 0.18, 0.5))
        if kc <= 0: continue
        lv = eo(prog(t, 1.15 + i * 0.12, 0.45))
        p0, p1, p2 = (1056, 600), (1150, cy), (1250 + 80 * (1 - kc), cy)
        pts = [bez(p0, p1, p2, u * lv / 20) for u in range(21)]
        p.line(pts, BLUE + (150,), 3)
        if t > 1.9:
            u = (t * 0.8 + i * 0.3) % 1
            x, y = bez(p0, p1, p2, u)
            p.circ(x, y, 6, fill=YEL, a=math.sin(u * math.pi))
        q = p.at(1470 + 80 * (1 - kc), cy, a=kc)
        q.rr(-220, -92, 220, 92, 24, fill=CARD, outline=LINE, w=2)
        q.rr(-200, -72, -64, 72, 18, fill=col)
        q.rr(-200, -72, -64, 0, 18, fill=(255, 255, 255, 40))
        ICON[ic](q.at(-132, 0), 64, INK)
        q.rr(-40, -54, 170, -34, 10, fill=(72, 78, 94))
        q.rr(-40, -18, 100, 0, 9, fill=(54, 59, 72))
        q.text(-40, 38, 'ver anúncio', 23, 'SemiBold', (96, 150, 255), 'lm')
        kb = prog(t, 2.05 + i * 0.32, 0.4)
        if kb > 0:
            b = q.at(118, -92, sc=max(.05, eback(kb, 2.4)), a=clamp(kb * 4))
            bw = tw('RECOMENDADO', 19, 'ExtraBold') + 56
            b.rr(-bw / 2, -21, bw / 2, 21, 21, fill=YEL)
            ic_check(b.at(-bw / 2 + 22, 0), 20, INK)
            b.text(-bw / 2 + 40, 1, 'RECOMENDADO', 19, 'ExtraBold', INK, 'lm')


MSG3 = 'Olá! Obrigado por comprar com a gente. Separei algumas sugestões que combinam com você'
EMO = None

def s3(p, t, D):
    global EMO
    if EMO is None: EMO = emoji('👇', 26) or False
    headline(p, t, [('O agente manda a ', WHITE), ('recomendação no WhatsApp', YEL)])
    k = eo(prog(t, 0.05, 0.5))
    # robô à esquerda
    r = p.at(470, 560 + 40 * (1 - k), sc=0.9, a=k)
    sending = 1.0 if 0.6 < t < 3.4 else 0.0
    robot(r, t, eye=YEL, arms='point', look=8, talk=sending)
    lab = p.at(470, 830, a=k)
    w = tw('Seu agente de IA', 24, 'Bold') + 50
    lab.rr(-w / 2, -26, w / 2, 26, 26, fill=CARD2, outline=LINE, w=1.5)
    lab.text(0, 1, 'Seu agente de IA', 24, 'Bold', WHITE, 'mm')
    # aviõezinhos de envio
    for i in range(6):
        t0 = 0.7 + i * 0.42
        u = prog(t, t0, 0.8)
        if u <= 0 or u >= 1: continue
        x, y = bez((660, 500), (800, 380 - i % 2 * 40), (990, 470), eo(u))
        a = math.sin(u * math.pi)
        ang = math.atan2(470 - 380, 990 - 800) * (u - .3)
        pl = p.at(x, y, a=a)
        ca, sa = math.cos(ang), math.sin(ang)
        pts = [(18, 0), (-14, -12), (-6, 0), (-14, 12)]
        pl.poly([(px * ca - py * sa, px * sa + py * ca) for px, py in pts], fill=YEL)
    # celular
    kp = eo(prog(t, 0.1, 0.55))
    ph = p.at(1230, 600 + 80 * (1 - kp), a=kp)
    ph.rr(-236, -440, 236, 440, 60, fill=(28, 30, 36), outline=(78, 82, 96), w=5)
    ph.rr(-216, -420, 216, 420, 46, fill=(11, 20, 26))
    ph.rr(-216, -420, 216, -318, 46, fill=(31, 44, 52))
    ph.rr(-216, -360, 216, -318, 0, fill=(31, 44, 52))
    ph.rr(-56, -410, 56, -390, 10, fill=(8, 9, 11))
    ph.circ(-156, -360, 27, fill=(96, 106, 124))
    ic_person(ph.at(-156, -356), 34, (190, 198, 212))
    ph.text(-116, -374, 'Cliente', 26, 'Bold', WHITE, 'lm')
    ph.text(-116, -344, 'online', 18, 'Regular', (134, 150, 160), 'lm')
    ph.rr(-44, -296, 44, -268, 14, fill=(31, 44, 52))
    ph.text(0, -282, 'Hoje', 17, 'SemiBold', (134, 150, 160), 'mm')
    # bolha 1 (digitando)
    lines = wrap(MSG3, 23, 'Regular', 300)
    total = len(MSG3)
    n = int(round(total * eio(prog(t, 0.6, 2.1))))
    if n > 0:
        bw = max(tw(l, 23, 'Regular') for l in lines) + 40
        shown, rem = [], n
        for l in lines:
            if rem <= 0: break
            shown.append(l[:rem]); rem -= len(l) + 1
        done = n >= total
        nl = len(shown)
        x1 = 198; x0 = x1 - bw; y0 = -246
        y1 = y0 + 18 + nl * 32 + (30 if done else 12)
        ph.rr(x0, y0, x1, y1, 16, fill=(0, 92, 75))
        ph.poly([(x1 - 10, y0), (x1 + 12, y0), (x1 - 2, y0 + 16)], fill=(0, 92, 75))
        for i, l in enumerate(shown):
            ph.text(x0 + 20, y0 + 16 + i * 32, l, 23, 'Regular', WHITE, 'la')
        if not done and int(t * 4) % 2 == 0:
            lx = x0 + 20 + tw(shown[-1], 23, 'Regular') + 3
            ph.rr(lx, y0 + 18 + (nl - 1) * 32, lx + 3, y0 + 42 + (nl - 1) * 32, 1, fill=WHITE)
        if done:
            if EMO:
                ex = x0 + 20 + tw(shown[-1], 23, 'Regular') + 8
                ph.image(EMO, ex, y0 + 14 + (nl - 1) * 32, a=prog(t, 2.7, 0.2))
            blue = t > 3.9
            ccol = (83, 189, 235) if blue else (134, 150, 160)
            ph.text(x1 - 58, y1 - 16, 'agora', 15, 'Regular', (180, 205, 200), 'rm')
            for dx in (0, 9):
                ph.line([(x1 - 50 + dx, y1 - 17), (x1 - 45 + dx, y1 - 12), (x1 - 36 + dx, y1 - 22)], ccol, 2.4)
        y_next = y1 + 16
    else:
        y_next = None
    # bolha 2: card do link
    kl = prog(t, 3.0, 0.4)
    if kl > 0 and y_next is not None:
        b = ph.at(198, y_next, sc=max(.05, eback(kl)), a=clamp(kl * 3))
        b.rr(-330, 0, 0, 238, 16, fill=(0, 92, 75))
        b.rr(-320, 10, -10, 128, 12, fill=YEL)
        b.rr(-320, 10, -10, 66, 12, fill=(255, 255, 255, 45))
        ic_bag(b.at(-210, 70), 58, INK); ic_tag(b.at(-120, 70), 50, INK)
        b.rr(-320, 128, -10, 216, 0, fill=(0, 74, 61))
        b.text(-306, 150, 'Sugestões para você', 22, 'Bold', WHITE, 'lm')
        b.text(-306, 180, 'ver anúncio no Mercado Livre', 19, 'SemiBold', (120, 210, 255), 'lm')
        b.text(-306, 206, 'mercadolivre.com.br', 16, 'Regular', (170, 200, 195), 'lm')
        b.text(-48, 228, 'agora', 14, 'Regular', (180, 205, 200), 'rm')
        ccol = (83, 189, 235) if t > 3.9 else (134, 150, 160)
        for dx in (0, 9):
            b.line([(-40 + dx, 227), (-35 + dx, 232), (-26 + dx, 222)], ccol, 2.4)
    # campo de digitação
    ph.rr(-200, 346, 136, 398, 26, fill=(31, 44, 52))
    ph.text(-176, 372, 'Mensagem', 20, 'Regular', (120, 134, 144), 'lm')
    ph.circ(168, 372, 27, fill=(0, 168, 132))
    ph.poly([(158, 360), (182, 372), (158, 384), (162, 372)], fill=WHITE)


MSGS4 = [('L', 'Contestação aberta para esta devolução.', 0.45),
         ('R', 'Recebido. Analisando o caso…', 1.35),
         ('L', 'Fotos e histórico do pedido enviados.', 2.2),
         ('R', 'Devolução revisada.', 3.05)]

def s4(p, t, D):
    headline(p, t, [('Contestação com a ', WHITE), ('IA do Mercado Livre', YEL)])
    k = eo(prog(t, 0.05, 0.5))
    act_l = any(s == 'L' and t0 <= t < t0 + 0.6 for s, _, t0 in MSGS4)
    act_r = any(s == 'R' and t0 - 0.35 <= t < t0 + 0.6 for s, _, t0 in MSGS4)
    robot(p.at(270, 560 + 40 * (1 - k), sc=0.78, a=k), t, arms='idle', look=10, talk=float(act_l))
    robot(p.at(1650, 560 + 40 * (1 - k), sc=0.78, a=k), t + 0.7, arms='idle', look=-10, variant=2,
          eye=(96, 165, 255), talk=float(act_r))
    for x, txt, col in ((270, 'Agente Tiops', YEL), (1650, 'IA do Mercado Livre', (96, 165, 255))):
        q = p.at(x, 800, a=k)
        w = tw(txt, 23, 'Bold') + 48
        q.rr(-w / 2, -25, w / 2, 25, 25, fill=CARD2, outline=col + (150,), w=2)
        q.text(0, 1, txt, 23, 'Bold', WHITE, 'mm')
    for i, (side, txt, t0) in enumerate(MSGS4):
        y = 300 + i * 112
        if side == 'R' and t0 - 0.38 <= t < t0:
            q = p.at(1400, y, a=clamp((t - t0 + 0.38) * 6))
            q.rr(-110, -30, 0, 30, 30, fill=(20, 32, 56), outline=BLUE + (150,), w=2)
            for j in range(3):
                bounce = 6 * max(0, math.sin(t * 14 - j * 0.9))
                q.circ(-82 + j * 27, -bounce, 7, fill=(150, 180, 230))
            continue
        kb = prog(t, t0, 0.35)
        if kb <= 0: continue
        kb = eo(kb)
        last = (i == len(MSGS4) - 1)
        w = tw(txt, 27, 'SemiBold') + 60 + (44 if last else 0)
        if side == 'L':
            q = p.at(520 - 30 * (1 - kb), y, a=kb)
            q.rr(0, -36, w, 36, 22, fill=(42, 37, 14), outline=YEL + (140,), w=2)
            q.poly([(0, 14), (-14, 30), (18, 30)], fill=(42, 37, 14))
            q.text(30, 1, txt, 27, 'SemiBold', WHITE, 'lm')
        else:
            q = p.at(1400 + 30 * (1 - kb), y, a=kb)
            fill = (14, 40, 26) if last else (20, 32, 56)
            oc = GREEN if last else BLUE
            q.rr(-w, -36, 0, 36, 22, fill=fill, outline=oc + (160,), w=2)
            q.text(-w + 30, 1, txt, 27, 'SemiBold', WHITE, 'lm')
            if last:
                q.circ(-40, 0, 16, fill=GREEN)
                ic_check(q.at(-40, 0), 20, INK)
    selo(p, 960, 790, 'REPUTAÇÃO PROTEGIDA', t, 3.6, fill=GREEN, fg=INK, icon='shield', px=30)


def s5(p, t, D):
    headline(p, t, [('Preço ajustado para entrar na ', WHITE), ('banda de margem', YEL)])
    k = eo(prog(t, 0.05, 0.5))
    g = p.at(0, 30 * (1 - k), a=k)
    g.rr(250, 220, 1670, 940, 30, fill=CARD, outline=LINE, w=2)
    X0, X1, YB, YT = 340, 1580, 880, 290
    yp = lambda v: YB - (v - 50) / 40 * (YB - YT)
    for i in range(6):
        y = YT + i * (YB - YT) / 5
        g.line([(X0, y), (X1, y)], (255, 255, 255, 14), 1.5)
    # faixa
    u = eio(prog(t, 1.35, 1.5))
    v = lerp(61.0, 78.9, u)
    inside = v >= 72
    glow = 0.5 + 0.5 * math.sin(t * 8) if inside else 0
    g.rr(X0, yp(86), X1, yp(72), 0, fill=GREEN + (int(34 + 40 * inside + 20 * glow),))
    dashed(g, X0, yp(86), X1, yp(86), GREEN + (170,), 2.5)
    dashed(g, X0, yp(72), X1, yp(72), GREEN + (170,), 2.5)
    g.text(X0 + 18, yp(86) + 26, 'BANDA DE MARGEM', 24, 'ExtraBold', GREEN, 'lm')
    # histórico
    kh = eo(prog(t, 0.3, 0.8))
    xe = lerp(X0, 900, kh)
    pts = [(x, yp(61 + 1.6 * math.sin(x / 55) + 0.8 * math.sin(x / 17))) for x in np.arange(X0, xe + 1, 8)]
    pts = [(x, y) for x, y in pts if x <= xe]
    if len(pts) > 1: g.line(pts, (150, 160, 180), 5)
    start = (900, yp(61 + 1.6 * math.sin(900 / 55) + 0.8 * math.sin(900 / 17)))
    end = (1290, yp(78.9))
    ctrl = (1110, start[1] + 10)
    if t > 1.0:
        ka = clamp((t - 1.0) * 4)
        if u > 0:
            tr = [bez(start, ctrl, end, u * j / 30) for j in range(31)]
            g.line(tr, YEL, 6)
            g.text(start[0], start[1] + 44, 'antes ' + real(61.0), 22, 'SemiBold', GRAY, 'mm', a=ka)
        x, y = bez(start, ctrl, end, u)
        col = GREEN if inside else YEL
        g.circ(x, y, 26 + 6 * glow, fill=col + (60,), a=ka)
        g.circ(x, y, 13, fill=col, outline=WHITE, w=3, a=ka)
        lw = tw(real(v), 34, 'ExtraBold') + 36
        g.rr(x - lw / 2, y - 92, x + lw / 2, y - 38, 14, fill=(30, 33, 40, 235), outline=col, w=2, a=ka)
        g.text(x, y - 65, real(v), 34, 'ExtraBold', WHITE, 'mm', a=ka)
    kt = prog(t, 3.05, 0.45)
    if kt > 0:
        c = g.at(1290, 690, sc=max(.05, eback(kt, 2.2)), a=clamp(kt * 4))
        txt = 'AJUSTE SUGERIDO · VOCÊ APROVA'
        w = tw(txt, 25, 'ExtraBold') + 100
        c.rr(-w / 2, -34, w / 2, 34, 34, fill=YEL)
        c.circ(-w / 2 + 34, 0, 18, fill=INK)
        ic_check(c.at(-w / 2 + 34, 0), 22, YEL)
        c.text(-w / 2 + 64, 1, txt, 25, 'ExtraBold', INK, 'lm')


def margem6(x):
    y = 430 + 14 * math.sin(x / 40)
    y = lerp(y, 562 + 11 * math.sin(x / 33), smooth(680, 745, x))
    y = lerp(y, 772, smooth(1095, 1180, x))
    y = lerp(y, 440 + 12 * math.sin(x / 45), smooth(1185, 1250, x))
    return y

def s6(p, t, D):
    headline(p, t, [('Promoção no ', WHITE), ('piloto automático', YEL)])
    k = eo(prog(t, 0.05, 0.5))
    g = p.at(0, 30 * (1 - k), a=k)
    g.rr(250, 220, 1670, 940, 30, fill=CARD, outline=LINE, w=2)
    X0, X1, YT, YB, FLOOR = 340, 1580, 290, 880, 700
    for i in range(6):
        y = YT + i * (YB - YT) / 5
        g.line([(X0, y), (X1, y)], (255, 255, 255, 14), 1.5)
    xr = lerp(X0, X1, eio(prog(t, 0.3, 3.0)))
    # período de promoção
    if xr > 700:
        xe = min(xr, 1182)
        g.rr(700, YT, xe, YB, 0, fill=YEL + (24,))
        g.text(lerp(700, xe, .5), YT + 24, 'EM PROMOÇÃO', 19, 'ExtraBold', YEL, 'mm', a=clamp((xe - 700) / 160))
    dashed(g, X0, FLOOR, X1, FLOOR, RED + (210,), 3, 18, 12)
    g.text(X0 + 14, FLOOR - 24, 'PISO DE MARGEM', 22, 'ExtraBold', RED, 'lm')
    g.text(X1, YB + 30, 'tempo →', 19, 'SemiBold', GRAY, 'rm')
    g.text(X0, YT - 22, 'margem', 19, 'SemiBold', GRAY, 'lm')
    pts = [(x, margem6(x)) for x in np.arange(X0, xr + 1, 6)]
    if len(pts) > 1:
        g.poly(pts + [(pts[-1][0], YB), (X0, YB)], fill=(90, 150, 255, 26))
        g.line(pts, (96, 156, 255), 6)
        hx, hy = pts[-1]
        below = hy > FLOOR
        col = RED if below else (96, 156, 255)
        g.circ(hx, hy, 22, fill=col + (70,)); g.circ(hx, hy, 10, fill=col, outline=WHITE, w=3)
    for xm, txt, fill, fg, dy, t_ic in ((700, 'ENTROU NA PROMOÇÃO', YEL, INK, -84, 'pct'),
                                         (1180, 'SAIU: MARGEM ABAIXO DO PISO', RED, WHITE, 66, 'check')):
        if xr < xm: continue
        km = prog(xr, xm, 70)
        ym = margem6(xm)
        dashed(g, xm, ym, xm, ym + dy, fill + (200,), 2.5, 8, 6, a=km)
        c = g.at(xm, ym + dy, sc=max(.05, eback(km, 2.2)), a=clamp(km * 3))
        w = tw(txt, 22, 'ExtraBold') + 46
        c.rr(-w / 2, -28, w / 2, 28, 28, fill=fill)
        c.text(0, 1, txt, 22, 'ExtraBold', fg, 'mm')
        g.circ(xm, ym, 9, fill=fill, outline=WHITE, w=2.5, a=km)


NODES7 = [('Pedidos', 'box'), ('Produtos', 'tag'), ('Clientes', 'person'),
          ('Anúncios', 'card'), ('Estoque', 'stack'), ('Promoções', 'pct')]

def s7(p, t, D):
    headline(p, t, [('O ', WHITE), ('cérebro', YEL), (' da sua operação', WHITE)])
    cx, cy = 960, 590
    pos = []
    for i in range(6):
        a = math.radians(-60 + 60 * i + 4 * math.sin(t * .7 + i))
        pos.append((cx + 560 * math.cos(a), cy + 280 * math.sin(a)))
    # ligações entre vizinhos
    for i in range(6):
        ka = prog(t, 1.0, 0.6)
        x0, y0 = pos[i]; x1, y1 = pos[(i + 1) % 6]
        p.line([(x0, y0), (x1, y1)], (96, 140, 255, 40), 2, a=ka)
    for i, (x, y) in enumerate(pos):
        u = eo(prog(t, 0.2 + 0.07 * i, 0.4))
        if u <= 0: continue
        p.line([(cx, cy), (lerp(cx, x, u), lerp(cy, y, u))], (96, 140, 255, 120), 3)
        if t > 0.9:
            for kk in range(2):
                f = (t * 0.75 + kk * 0.5 + i * 0.17) % 1
                ff = f if kk == 0 else 1 - f
                px_, py_ = lerp(cx, x, ff), lerp(cy, y, ff)
                al = math.sin(f * math.pi) * clamp((t - 0.9) * 3)
                p.circ(px_, py_, 14, fill=YEL + (60,), a=al)
                p.circ(px_, py_, 6, fill=YEL, a=al)
    # nós satélites
    for i, ((x, y), (txt, ic)) in enumerate(zip(pos, NODES7)):
        kn = prog(t, 0.4 + 0.08 * i, 0.45)
        if kn <= 0: continue
        n = p.at(x, y, sc=max(.05, eback(kn)), a=clamp(kn * 3))
        km = clamp((t - 0.9) * 2)
        for j in range(4):
            a = math.radians(i * 40 + j * 90 + t * 28)
            mx, my = 96 * math.cos(a), 96 * math.sin(a) * .8
            n.line([(0, 0), (mx, my)], (96, 140, 255, 70), 1.5, a=km)
            n.circ(mx, my, 7, fill=(96, 140, 255), a=km)
        n.circ(0, 0, 66, fill=BLUE + (40,))
        n.circ(0, 0, 56, fill=CARD2, outline=(96, 140, 255), w=4)
        ICON[ic](n, 46, WHITE)
        n.text(0, 90, txt, 26, 'Bold', WHITE, 'mm')
    # nó central
    kc = prog(t, 0.05, 0.5)
    if kc > 0:
        c = p.at(cx, cy, sc=max(.05, eback(kc)), a=clamp(kc * 3))
        pulse = (t * 1.0) % 1
        c.circ(0, 0, 100 + 150 * pulse, outline=YEL, w=3, a=(1 - pulse) * .6)
        c.circ(0, 0, 114 + 6 * math.sin(t * 5), fill=YEL + (50,))
        c.circ(0, 0, 98, fill=YEL)
        c.text(0, -14, 'AGENTES', 31, 'Black', INK, 'mm')
        c.text(0, 24, 'de IA', 22, 'Bold', INK, 'mm')


FEED8 = [('Preço ajustado', 'Guardião de margem', YEL, 'money'),
         ('Pergunta respondida', 'Atendente', BLUE, 'bubble'),
         ('Promoção revisada', 'Comprador de mídia', PURPLE, 'pct'),
         ('Estoque atualizado', 'Analista de estoque', GREEN, 'stack'),
         ('Etiqueta emitida', 'Expedição', CYAN, 'tag'),
         ('Anúncio otimizado', 'Curador de catálogo', ORANGE, 'card'),
         ('Mensagem enviada', 'Pós-venda', BLUE, 'bubble'),
         ('Margem conferida', 'Guardião de margem', YEL, 'money'),
         ('Devolução contestada', 'Pós-venda', GREEN, 'shield')]

def s8(p, t, D):
    headline(p, t, [('Os agentes trabalham ', WHITE), ('o dia inteiro', YEL)])
    k = eo(prog(t, 0.05, 0.5))
    c = p.at(540, 580 + 40 * (1 - k), a=k)
    c.circ(0, 0, 248, fill=BLUE + (30,))
    c.circ(0, 0, 232, fill=CARD, outline=LINE, w=6)
    c.circ(0, 0, 206, outline=(44, 48, 58), w=2)
    for h in range(12):
        a = math.radians(h * 30)
        r1 = 168 if h % 3 == 0 else 184
        c.line([(r1 * math.sin(a), -r1 * math.cos(a)), (200 * math.sin(a), -200 * math.cos(a))],
               WHITE if h % 3 == 0 else (120, 126, 140), 7 if h % 3 == 0 else 4)
    spin = t * 1.5 * 360
    for j in range(7, 0, -1):
        a = math.radians(spin - j * 7)
        c.line([(0, 0), (160 * math.sin(a), -160 * math.cos(a))], YEL + (int(70 - j * 9),), 8)
    a = math.radians(spin)
    c.line([(0, 0), (162 * math.sin(a), -162 * math.cos(a))], YEL, 9)
    a = math.radians(spin / 12 + 40)
    c.line([(0, 0), (105 * math.sin(a), -105 * math.cos(a))], WHITE, 13)
    c.circ(0, 0, 17, fill=YEL); c.circ(0, 0, 6, fill=INK)
    selo(p, 540, 880, 'O DIA INTEIRO', t, 0.5, dot=True, px=30)
    # feed
    kf = eo(prog(t, 0.1, 0.5))
    f = p.at(60 * (1 - kf), 0, a=kf)
    f.rr(880, 230, 1690, 950, 28, fill=CARD, outline=LINE, w=2)
    pulse = (t * 1.4) % 1
    f.circ(926, 284, 8 + 12 * pulse, fill=GREEN + (int(120 * (1 - pulse)),))
    f.circ(926, 284, 8, fill=GREEN)
    f.text(948, 284, 'Atividade dos agentes', 28, 'Bold', WHITE, 'lm')
    f.text(1654, 284, 'ao vivo', 21, 'SemiBold', GREEN, 'rm')
    f.line([(904, 326), (1666, 326)], LINE, 2)
    TOP, RH, BOT = 346, 96, 938
    times = [0.3 + 0.42 * j for j in range(len(FEED8))]
    for kk, (txt, who, col, ic) in enumerate(FEED8):
        if t < times[kk]: continue
        pushed = sum(eo(prog(t, times[j], 0.32)) for j in range(kk + 1, len(FEED8)))
        y = TOP + pushed * RH + RH / 2
        ap = eo(prog(t, times[kk] + 0.2, 0.3))
        al = ap * clamp((BOT - (y + 42)) / 50)
        if al <= 0.01: continue
        newer = sum(1 for j in range(kk + 1, len(FEED8)) if t >= times[j])
        r = f.at(-40 * (1 - ap), 0, a=al)
        fl = 1 - prog(t, times[kk], 0.9)
        r.rr(904, y - 42, 1666, y + 42, 18, fill=(30, 33, 40))
        if fl > 0: r.rr(904, y - 42, 1666, y + 42, 18, fill=YEL + (int(40 * fl),), outline=YEL + (int(160 * fl),), w=2)
        r.circ(954, y, 26, fill=col)
        ICON[ic](r.at(954, y), 28, INK)
        r.text(996, y - 13, txt, 27, 'Bold', WHITE, 'lm')
        r.text(996, y + 19, who, 20, 'Regular', GRAY, 'lm')
        r.text(1640, y, 'agora' if newer < 2 else 'há 1 min', 19, 'SemiBold', GRAY, 'rm')


CENAS = [
    (1, '01-robo-trabalhando.mp4', 41.6, 4.5, s1, 'Robô da Tiops digitando numa mesa com monitor; tarefas (pedido, etiqueta, mensagem, preço…) saindo da tela; selo TRABALHANDO 24H.'),
    (2, '02-recomendacao-ia.mp4', 69.6, 4.5, s2, 'Card de cliente recorrente (sem nome) → nó da IA → 3 cards de produto em ícone com selo RECOMENDADO.'),
    (3, '03-agente-whatsapp.mp4', 206.5, 5.0, s3, 'Agente mandando mensagem: celular estilo WhatsApp com a recomendação sendo digitada, card do link do Mercado Livre e check azul.'),
    (4, '04-contestacao-ia-ml.mp4', 489.0, 5.0, s4, 'Agente Tiops e IA do Mercado Livre trocando mensagens: contestação aberta → devolução revisada; selo REPUTAÇÃO PROTEGIDA.'),
    (5, '05-banda-de-margem.mp4', 563.0, 4.5, s5, 'Gráfico: preço sobe de R$ 61,00 para R$ 78,90 e entra na faixa verde BANDA DE MARGEM; selo AJUSTE SUGERIDO · VOCÊ APROVA.'),
    (6, '06-promocao-automatica.mp4', 753.0, 4.5, s6, 'Linha de margem no tempo com piso: ENTROU NA PROMOÇÃO e depois SAIU: MARGEM ABAIXO DO PISO.'),
    (7, '07-cerebro-operacao.mp4', 854.0, 4.5, s7, 'Rede de nós pulsando: Pedidos, Produtos, Clientes, Anúncios, Estoque e Promoções ligados ao nó central AGENTES.'),
    (8, '08-dia-inteiro.mp4', 883.0, 4.5, s8, 'Relógio girando rápido + feed de ações dos agentes rolando (sem contagens); selo O DIA INTEIRO.'),
]


def render(cena, BG):
    n, nome, _, dur, fn, _ = cena
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, nome)
    nf = int(round(dur * FPS))
    pr = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                           '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(nf):
        t = i / FPS
        img = BG.copy()
        ex = eo(prog(t, dur - 0.3, 0.3))
        sc = 1 - 0.04 * ex
        root = P(img, 960 * (1 - sc), 540 * (1 - sc), sc, 1 - ex)
        fn(root, t, dur)
        brand(P(img, a=1 - ex))
        pr.stdin.write(img.reduce(K).tobytes())
    pr.stdin.close(); pr.wait()
    print('ok', nome, '%.1fs' % dur)


def folha():
    for n, nome, _, dur, _, _ in CENAS:
        src = os.path.join(OUT, nome)
        ts = [0.15, dur * .3, dur * .55, dur * .8, dur - 0.35]
        ims = []
        for t in ts:
            r = subprocess.run([FF, '-v', 'error', '-ss', '%.2f' % t, '-i', src, '-frames:v', '1', '-vf', 'scale=640:-2',
                                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
            ims.append(Image.frombytes('RGB', (640, 360), r.stdout))
        sheet = Image.new('RGB', (640 * 5, 360))
        for i, im in enumerate(ims): sheet.paste(im, (640 * i, 0))
        sheet.save(os.path.join(AQUI, 'trab', 'broll-folha-%d.jpg' % n), quality=85)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['folha']:
        folha(); sys.exit()
    BG = make_bg()
    sel = [int(a) for a in args] if args else [c[0] for c in CENAS]
    for c in CENAS:
        if c[0] in sel: render(c, BG)
    man = [dict(arquivo=c[1], momento_bruto_s=c[2], duracao_s=c[3], descricao=c[5]) for c in CENAS
           if os.path.exists(os.path.join(OUT, c[1]))]
    json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1, ensure_ascii=False)
