"""Peças visuais compartilhadas (texto, sprites, ícones, easing) — copiadas do motor de
mc-treinamento-do-zero/render.py para a aula não depender daquele projeto."""
import math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FONTE = '/Users/itamar/git/gestao-redes-sociais/output/reel-explica-marketplace-connect/assets/Inter.ttf'
YEL = (0, 196, 245)
INK = (12, 11, 11)
NAVY = (48, 22, 10)
CYAN = (255, 200, 60)
GREEN = (110, 200, 50)
RED = (70, 70, 230)
WHITE = (255, 255, 255)
GREY = (190, 182, 176)


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


