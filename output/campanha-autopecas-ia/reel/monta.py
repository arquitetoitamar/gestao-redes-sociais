"""Reel "tabela de compatibilidade gerando reclamação" (autopeças, GestorPro).
Gêmeo digital do Itamar (HeyGen, look nov26, voz c463ef5b) + cartões da página de autopeças + foto Higgsfield
+ legenda palavra a palavra. Sem música (entra pelo app, se quiser).

  python3 monta.py           -> reel_autopecas.mp4 (1080x1920, 30 qps)
  python3 monta.py stills    -> trab/stills.png (folha de conferência)
"""
import json, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
FONTE = os.path.join(AQUI, 'assets', 'Inter.ttf')
INK, WHITE = (19, 20, 23), (255, 255, 255)
GREEN, AMBER, RED = (10, 143, 96), (180, 83, 9), (194, 65, 12)
INICIO = json.load(open(os.path.join(AQUI, 'trab', 'inicio.json')))
TOTAL = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                              os.path.join(AQUI, 'audio', 'voz.wav')], capture_output=True, text=True).stdout)


def fonte(px, peso=900):
    f = ImageFont.truetype(FONTE, px)
    f.set_variation_by_axes([32 if px >= 40 else 14, peso])
    return f


def palavras(nid):
    ws = json.load(open(os.path.join(AQUI, 'audio', nid + '.words.json')))
    off = ws[0]['start']
    return [(w['text'], INICIO[nid] + w['start'] - off, INICIO[nid] + w['end'] - off) for w in ws]


PAL = {n: palavras(n) for n in INICIO}
FIM = {n: PAL[n][-1][2] for n in PAL}


def cue(nid, p):
    for txt, a, b in PAL[nid]:
        if txt.lower().strip('.,:!?').startswith(p.lower()):
            return a
    raise KeyError((nid, p))


ease = lambda x: x * x * (3 - 2 * x)


def janela(t, t0, t1, d=0.35):
    """0..1 entrando em t0, saindo em t1."""
    a = ease(min(max((t - t0) / d, 0), 1))
    b = ease(min(max((t1 - t) / d, 0), 1))
    return min(a, b)


# ------------------------------------------------------------------ fontes de imagem
class Avatar:
    """Lê o mp4 do HeyGen (25 qps) em ordem e devolve o quadro do instante t, com zoom no busto."""
    ZOOM, Y0 = 1.42, 70

    def __init__(self, arq):
        self.cap = cv2.VideoCapture(arq)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.i, self.im = -1, None

    def quadro(self, t):
        alvo = int(t * self.fps)
        while self.i < alvo:
            ok, im = self.cap.read()
            if not ok:
                break
            self.i, self.im = self.i + 1, im
        cw, ch = int(W / self.ZOOM), int(H / self.ZOOM)
        x0 = (W - cw) // 2
        crop = self.im[self.Y0:self.Y0 + ch, x0:x0 + cw]
        crop = cv2.resize(crop, (W, H), interpolation=cv2.INTER_CUBIC)
        return Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)).convert('RGBA')


BROLL = Image.open(os.path.join(AQUI, '..', 'img', 'hf-pastilha-oficina.png')).convert('RGB')
def _card(n):
    c = Image.open(os.path.join(AQUI, 'cards', n + '.png')).convert('RGBA')
    return c.resize((1040, round(c.height * 1040 / c.width)), Image.LANCZOS)


CARDS = {n: _card(n) for n in ('tabela', 'curador', 'atendente')}


def broll(t, t0, t1):
    """Ken Burns lento na foto da pastilha."""
    u = min(max((t - t0) / (t1 - t0), 0), 1)
    z = 1.04 + 0.08 * u
    bw, bh = BROLL.size
    s = max(W / bw, H / bh) * z
    im = BROLL.resize((int(bw * s), int(bh * s)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * (0.35 + 0.15 * u))
    return im.crop((x, y, x + W, y + H)).convert('RGBA')


# ------------------------------------------------------------------ texto
def caixas(d, y, linhas, f, destaque=None, fundo=WHITE, cor=INK, cor_dest=GREEN, pad=(28, 14)):
    asc, desc = f.getmetrics()
    alt = asc + desc + 2 * pad[1]
    for l in linhas:
        txt = ' '.join(w[0] for w in l)
        tw = d.textlength(txt, font=f)
        x = (W - tw) / 2
        d.rounded_rectangle((x - pad[0], y, x + tw + pad[0], y + alt), 16, fill=fundo)
        for w in l:
            c = cor_dest if (destaque is not None and w is destaque) else (w[3] if len(w) > 3 else cor)
            d.text((x, y + pad[1]), w[0], font=f, fill=c)
            x += d.textlength(w[0] + ' ', font=f)
        y += alt + 10
    return y


F_LEG = fonte(54, 900)
F_HOOK = fonte(70, 900)


def legenda(d, t, y):
    for nid in ('n1', 'n2', 'n3', 'n4'):
        ws = PAL[nid]
        if ws[0][1] - 0.1 <= t <= ws[-1][2] + 0.3:
            break
    else:
        return
    up = [(w[0].upper(), w[1], w[2]) for w in ws]
    linhas = [[]]
    for w in up:
        if d.textlength(' '.join(x[0] for x in linhas[-1] + [w]), font=F_LEG) > 880 and linhas[-1]:
            linhas.append([])
        linhas[-1].append(w)
    atual = 0
    for li, l in enumerate(linhas):
        if any(w[1] <= t for w in l):
            atual = li
    vis = linhas[(atual // 2) * 2:(atual // 2) * 2 + 2]
    cur = None
    for l in vis:
        for w in l:
            if w[1] <= t < w[2] + 0.05:
                cur = w
    caixas(d, y, vis, F_LEG, destaque=cur)


def camada(im, fn, a=1.0):
    if a <= 0.003:
        return im
    L = Image.new('RGBA', im.size, (0, 0, 0, 0))
    fn(L, ImageDraw.Draw(L))
    if a < 0.997:
        L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    return Image.alpha_composite(im, L)


def cartao(nome, y):
    c = CARDS[nome]
    def fn(L, d):
        L.alpha_composite(c, ((W - c.width) // 2, int(y)))
    return fn


# ------------------------------------------------------------------ roteiro visual
T_TAB = (INICIO['n1'] - 0.05, INICIO['n2'] - 0.1)
T_BROLL = (INICIO['n2'] - 0.1, INICIO['n3'] - 0.05)
T_CHIP = cue('n2', 'Na')
T_CUR = (cue('n3', 'Curador') - 0.3, INICIO['n4'] - 0.1)
T_ATE = (INICIO['n4'] - 0.05, INICIO['n5'] - 0.1)
T_FIM = INICIO['n5'] - 0.05


def quadro(t, av):
    base = av.quadro(t)
    # cartões sobre o avatar escurecem um pouco o fundo
    k_tab = janela(t, *T_TAB)
    k_cur = janela(t, *T_CUR)
    k_ate = janela(t, *T_ATE)
    k = max(k_tab, k_cur, k_ate)
    im = base
    if k > 0:
        im = camada(im, lambda L, d: d.rectangle((0, 0, W, H), fill=(0, 0, 0, 80)), k)
    kb = janela(t, *T_BROLL, d=0.25)
    if kb > 0:
        b = broll(t, *T_BROLL)
        im = Image.blend(im, b, kb) if kb < 1 else b
        im = camada(im, lambda L, d: d.rectangle((0, 0, W, H), fill=(0, 0, 0, 60)), kb)
    for nome, kk in (('tabela', k_tab), ('curador', k_cur), ('atendente', k_ate)):
        if kk > 0:
            y = H - CARDS[nome].height - 110 + (1 - kk) * 90
            im = camada(im, cartao(nome, y), kk)
    # selo da reclamação sobre a foto
    kc = janela(t, T_CHIP, T_BROLL[1], d=0.3) * (kb > 0)
    if kc > 0:
        def chip(L, d):
            f1, f2 = fonte(44, 900), fonte(34, 700)
            x0, y0, x1, y1 = 90, 300, 990, 520
            d.rounded_rectangle((x0, y0, x1, y1), 34, fill=WHITE)
            d.rounded_rectangle((x0 + 30, y0 + 34, x0 + 120, y0 + 124), 22, fill=(253, 232, 225))
            d.text((x0 + 75, y0 + 79), '!', font=fonte(56, 900), fill=RED, anchor='mm')
            d.text((x0 + 150, y0 + 36), 'Reclamação', font=f2, fill=(123, 129, 144))
            d.text((x0 + 150, y0 + 80), 'Não serve no veículo', font=f1, fill=INK)
            d.rounded_rectangle((x0 + 150, y0 + 150, x0 + 420, y0 + 196), 23, fill=(253, 232, 225))
            d.text((x0 + 285, y0 + 173), 'prazo 1d 18h', font=fonte(28, 800), fill=RED, anchor='mm')
        im = camada(im, chip, kc)
    # textos
    d = ImageDraw.Draw(im)
    if t < INICIO['n1'] - 0.1:
        a = janela(t, 0.0, INICIO['n1'] - 0.1, d=0.2)
        linhas = [[('SUA TABELA DE', 0, 0)], [('COMPATIBILIDADE PODE', 0, 0)],
                  [('ESTAR GERANDO', 0, 0)], [('RECLAMAÇÃO', 0, 0, WHITE)]]
        def hook(L, dd):
            y = caixas(dd, 930, linhas[:3], F_HOOK)
            asc, desc = F_HOOK.getmetrics()
            tw = dd.textlength('RECLAMAÇÃO', font=F_HOOK)
            x = (W - tw) / 2
            dd.rounded_rectangle((x - 28, y, x + tw + 28, y + asc + desc + 28), 16, fill=AMBER)
            dd.text((x, y + 14), 'RECLAMAÇÃO', font=F_HOOK, fill=WHITE)
        im = camada(im, hook, a)
        d = ImageDraw.Draw(im)
        # rótulo do público
        f = fonte(34, 800)
        txt = 'LOJA DE AUTOPEÇAS'
        tw = d.textlength(txt, font=f)
        d.rounded_rectangle(((W - tw) / 2 - 22, 852, (W + tw) / 2 + 22, 906), 27, fill=GREEN)
        d.text((W / 2, 879), txt, font=f, fill=WHITE, anchor='mm')
    elif t >= T_FIM:
        a = janela(t, T_FIM, TOTAL + 1, d=0.3)
        def fim(L, dd):
            caixas(dd, 860, [[('BLACK FRIDAY CHEGANDO:', 0, 0)], [('CONFERE SEUS ANÚNCIOS', 0, 0)]], fonte(60, 900))
            x0, y0, x1, y1 = 90, 1100, 990, 1570
            dd.rounded_rectangle((x0, y0, x1, y1), 44, fill=WHITE)
            dd.text((W / 2, y0 + 80), 'Comenta', font=fonte(48, 800), fill=(74, 79, 90), anchor='mm')
            dd.text((W / 2, y0 + 220), 'PEÇA', font=fonte(190, 900), fill=GREEN, anchor='mm')
            dd.text((W / 2, y0 + 370), 'que eu te mando o link', font=fonte(44, 700), fill=(74, 79, 90), anchor='mm')
        im = camada(im, fim, a)
    else:
        if kb > 0.5:
            y = 1480
        elif k > 0.5:
            nome = 'tabela' if k_tab > 0.5 else 'curador' if k_cur > 0.5 else 'atendente'
            y = H - CARDS[nome].height - 110 - 270
        else:
            y = 1480
        im = camada(im, lambda L, dd: legenda(dd, t, y))
    return im.convert('RGB')


def video():
    av = Avatar(os.path.join(AQUI, 'trab', 'avatar.mp4'))
    out = os.path.join(AQUI, 'reel_autopecas.mp4')
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                           '-r', str(FPS), '-i', '-', '-i', os.path.join(AQUI, 'audio', 'voz.wav'),
                           '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:v', 'libx264', '-crf', '19', '-preset', 'medium',
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest',
                           '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    n = int(TOTAL * FPS)
    for i in range(n):
        ff.stdin.write(np.asarray(quadro(i / FPS, av)).tobytes())
        if i % 150 == 0:
            print('%d/%d' % (i, n), flush=True)
    ff.stdin.close()
    ff.wait()
    print(out)


def stills(ts):
    av = Avatar(os.path.join(AQUI, 'trab', 'avatar.mp4'))
    ims = [quadro(t, av).resize((270, 480)) for t in ts]
    f = Image.new('RGB', (len(ims) * 280 + 10, 500), WHITE)
    for i, im in enumerate(ims):
        f.paste(im, (10 + i * 280, 10))
    f.save(os.path.join(AQUI, 'trab', 'stills.png'))


if __name__ == '__main__':
    if sys.argv[1:2] == ['stills']:
        stills([1.5, 8.0, 13.0, 16.5, 22.0, 28.5, 35.0])
    else:
        video()
