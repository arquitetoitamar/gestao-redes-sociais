"""Reel "emita nota pela IA" (público fora do marketplace): gêmeo digital do Itamar (HeyGen, voz oficial)
+ cartão com as animações da landing do Emissor + legenda em caixa branca (estilo da referência) + CTA NOTA.
Sem música: a música (meme) entra pelo app do Instagram na hora de publicar.

Fontes: trab/av/fXXXXX.jpg (avatar 25 qps) e trab/anim/aNN/fXXXXX.jpg (animações 30 qps).
uso: python3 monta.py [quadros|stills t1,t2|audio|video]   (sem argumento: tudo)
"""
import json, math, os, subprocess, sys
from multiprocessing import Process
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
FONTE = os.path.join(AQUI, 'assets', 'Inter.ttf')
NAVY = (11, 22, 64)
BLUE = (37, 99, 235)
YELLOW = (250, 204, 21)
WHITE = (255, 255, 255)
INK = (15, 15, 20)

INICIO = json.load(open(os.path.join(AQUI, 'trab', 'inicio.json')))
TOTAL = 35.0


def palavras(nid):
    ws = json.load(open(os.path.join(AQUI, 'audio', nid + '.words.json')))
    off = ws[0]['start']
    return [(w['text'], INICIO[nid] + w['start'] - off, INICIO[nid] + w['end'] - off) for w in ws]


PAL = {n: palavras(n) for n in INICIO}


def cue(nid, palavra):
    for txt, a, b in PAL[nid]:
        if txt.lower().strip('.,:!?').startswith(palavra.lower()):
            return a
    raise KeyError((nid, palavra))


def fonte(px, peso=900):
    f = ImageFont.truetype(FONTE, px)
    f.set_variation_by_axes([32 if px >= 40 else 14, peso])
    return f


ease = lambda x: x * x * (3 - 2 * x)


def aparece(t, t0, d=0.35):
    return ease(min(max((t - t0) / d, 0), 1))


# ---------------------------------------------------------------- fontes de imagem
class Seq:
    def __init__(self, pasta, fps, cobre=None):
        self.pasta, self.fps, self.cobre = pasta, fps, cobre
        self.n = len(os.listdir(pasta))
        self.cache = (None, None)

    def quadro(self, ts):
        i = min(max(int(round(ts * self.fps)), 0), self.n - 1)
        if self.cache[0] != i:
            im = cv2.imread(os.path.join(self.pasta, 'f%05d.jpg' % (i + 1)))
            if self.cobre:
                x0, y0, x1, y1 = self.cobre
                im[y0:y1, x0:x1] = 255
            self.cache = (i, im)
        return self.cache[1]


AV = Seq(os.path.join(AQUI, 'trab', 'av'), 25)
ANIM = {'01': Seq(os.path.join(AQUI, 'trab', 'anim', 'a01'), 30),
        '02': Seq(os.path.join(AQUI, 'trab', 'anim', 'a02'), 30, (815, 522, 1000, 584)),
        'CL': Seq(os.path.join(AQUI, 'trab', 'claude'), 30)}   # janela da gravação real (Reel do Claude, chave já borrada)

# cartão de tela
T_IN, T_OUT = cue('n1', 'Vendeu') + 0.1, cue('n4', 'Emitir') + 0.05
CX0, CY0, CW, CH = 40, 1056, 1000, 720
SUBIDA = 300                                        # quanto o avatar sobe com o cartão


def tela(t):
    """(animação, t_src, câmera) do cartão no instante t: venda no WhatsApp e para empresa, depois a IA emitindo."""
    manda = cue('n1', 'Manda')
    pts = [  # (t, anim, src, cx, cy, cw)
        (T_IN, '01', 8.8, 540, 980, 1000), (cue('n1', 'empresa') - 0.2, '01', 13.0, 540, 1000, 1000),
        (cue('n1', 'empresa') - 0.2, '01', 17.6, 540, 980, 1000), (manda, '01', 21.4, 540, 1000, 1000),
        (manda, 'CL', 0.3, 500, 440, 1000), (INICIO['n2'], 'CL', 8.6, 500, 440, 1000),
        (INICIO['n2'], 'CL', 9.4, 500, 440, 1000), (INICIO['n3'], 'CL', 15.5, 500, 440, 1000),
        (INICIO['n3'], 'CL', 19.7, 500, 440, 1000), (cue('n3', 'emitir') + 0.3, 'CL', 21.3, 500, 440, 1000),
        (cue('n3', 'emitir') + 0.3, 'CL', 21.3, 500, 440, 1000), (T_OUT, 'CL', 29.0, 500, 440, 1000),
    ]
    for (a, an, s0, x0, y0, w0), (b, an2, s1, x1, y1, w1) in zip(pts, pts[1:]):
        if a <= t < b and an == an2:
            u = (t - a) / (b - a)
            k = ease(u)
            return an, s0 + (s1 - s0) * u, (x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, w0 + (w1 - w0) * k)
    a = pts[-1]
    return a[1], a[2], a[3:]


def recorte(im, cam, cw_out, ch_out):
    cx, cy, cw = cam
    ch = cw * ch_out / cw_out
    x0 = min(max(cx - cw / 2, 0), im.shape[1] - cw) if cw <= im.shape[1] else (im.shape[1] - cw) / 2
    y0 = min(max(cy - ch / 2, 0), 1610 - ch)
    M = np.float32([[cw_out / cw, 0, -x0 * cw_out / cw], [0, ch_out / ch, -y0 * ch_out / ch]])
    out = cv2.warpAffine(im, M, (cw_out, ch_out), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


MASK = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(MASK).rounded_rectangle((0, 0, CW - 1, CH - 1), 36, fill=255)


# ---------------------------------------------------------------- textos
def caixa_branca(d, y, linhas, f, pad=(30, 14), cor_txt=INK, fundo=WHITE, destaque=None):
    """Caixas brancas centradas, uma por linha (estilo da referência). destaque = palavra atual em azul."""
    asc, desc = f.getmetrics()
    alt = asc + desc + 2 * pad[1]
    for li, l in enumerate(linhas):
        txt = ' '.join(w if isinstance(w, str) else w[0] for w in l)
        tw = d.textlength(txt, font=f)
        x = (W - tw) / 2
        d.rounded_rectangle((x - pad[0], y, x + tw + pad[0], y + alt), 16, fill=fundo)
        for w in l:
            p = w if isinstance(w, str) else w[0]
            cor = BLUE if (destaque is not None and not isinstance(w, str) and w is destaque) else cor_txt
            d.text((x, y + pad[1]), p, font=f, fill=cor)
            x += d.textlength(p + ' ', font=f)
        y += alt + 10
    return y


F_LEG = fonte(52, 900)


def legenda(d, t, y):
    for nid in ('n0', 'n1', 'n2', 'n3', 'n4', 'n5'):
        ws = PAL[nid]
        if ws[0][1] - 0.1 <= t <= ws[-1][2] + 0.25:
            break
    else:
        return
    if nid in ('n0', 'n5'):
        return                                   # o texto já está na caixa de cima
    if nid == 'n4':
        ws = [w for w in ws if w[1] >= cue('n4', 'Você') - 0.05]
        if t < ws[0][1] - 0.1:
            return
    up = [(w[0].upper(), w[1], w[2]) for w in ws]
    linhas = [[]]
    for w in up:
        teste = ' '.join(x[0] for x in linhas[-1] + [w])
        if d.textlength(teste, font=F_LEG) > 860 and linhas[-1]:
            linhas.append([])
        linhas[-1].append(w)
    atual = 0
    for li, l in enumerate(linhas):
        if any(w[1] <= t for w in l):
            atual = li
    ini = (atual // 2) * 2
    vis = linhas[ini:ini + 2]
    cur = None
    for l in vis:
        for w in l:
            if w[1] <= t < w[2] + 0.05:
                cur = w
    caixa_branca(d, y, vis, F_LEG, destaque=cur)


def comp(im, fn, a=1.0):
    if a <= 0.003:
        return im
    L = Image.new('RGBA', im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(L))
    if a < 0.997:
        L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    return Image.alpha_composite(im, L)


LOGO = Image.open(os.path.join(AQUI, 'assets', 'logo-tiops.png')).convert('RGBA')


def quadro(t):
    av = cv2.cvtColor(AV.quadro(t), cv2.COLOR_BGR2RGB)
    k = aparece(t, T_IN, 0.45) * (1 - aparece(t, T_OUT, 0.45))
    sob = int(SUBIDA * k)
    base = Image.fromarray(av)
    if sob:
        fundo = base.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(3)).resize((W, H))
        fundo.paste(base.crop((0, sob, W, H)), (0, 0))
        base = fundo
    im = base.convert('RGBA')
    # escurece um pouco a base para o cartão destacar
    if k > 0:
        im = comp(im, lambda d: d.rectangle((0, 0, W, H), fill=(0, 0, 0, 70)), k)
        an, ts, cam = tela(t)
        card = recorte(ANIM[an].quadro(ts), cam, CW, CH).convert('RGBA')
        y = int(CY0 + (1 - k) * 260)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sombra = Image.new('L', (W, H), 0)
        ImageDraw.Draw(sombra).rounded_rectangle((CX0 + 8, y + 18, CX0 + CW - 8, y + CH + 18), 36, fill=int(120 * k))
        L.paste((0, 0, 0, 255), (0, 0), sombra.filter(ImageFilter.GaussianBlur(24)))
        im = Image.alpha_composite(im, L)
        m = MASK.point(lambda v: int(v * k))
        im.paste(card, (CX0, y), m)
    # gancho e frases de efeito no topo
    if t < INICIO['n1'] - 0.05:
        a = aparece(t, 0.05, 0.3)
        im = comp(im, lambda d: caixa_branca(d, 150, [['ANTES', 'DE', 'CONTRATAR', 'ALGUÉM'], ['SÓ', 'PRA', 'EMITIR', 'NOTA', 'FISCAL']], fonte(62)), a)
    if T_OUT <= t < INICIO['n5']:
        a = aparece(t, cue('n4', 'Emitir') - 0.05, 0.3)
        b = aparece(t, cue('n4', 'É') - 0.05, 0.3)
        im = comp(im, lambda d: caixa_branca(d, 150, [['EMITIR', 'NOTA', 'NÃO', 'É', 'CARGO.']], fonte(64)), a)
        im = comp(im, lambda d: caixa_branca(d, 262, [['É', 'UMA', 'FRASE.']], fonte(80), fundo=YELLOW), b)
    if t >= INICIO['n5'] - 0.05:
        a = aparece(t, INICIO['n5'] - 0.05, 0.3)
        im = comp(im, lambda d: caixa_branca(d, 150, [['TESTE', 'GRÁTIS,', 'SEM', 'CARTÃO']], fonte(62)), a)
        c = aparece(t, cue('n5', 'Comenta') - 0.1, 0.3)
        s = 0.75 + 0.25 * c + (0.025 * math.sin((t - cue('n5', 'NOTA')) * 6) if t > cue('n5', 'NOTA') + 0.3 else 0)

        def cta(d):
            f1, f2 = fonte(70), fonte(int(190 * s))
            d.rounded_rectangle((170, 1120, 910, 1560), 48, fill=YELLOW)
            tw = d.textlength('COMENTA', font=f1)
            d.text(((W - tw) / 2, 1160), 'COMENTA', font=f1, fill=NAVY)
            tw = d.textlength('NOTA', font=f2)
            asc, desc = f2.getmetrics()
            d.text(((W - tw) / 2, 1250 + (190 - 190 * s) * 0.4), 'NOTA', font=f2, fill=NAVY)
            f3 = fonte(44, 700)
            txt = 'que eu te mando o link'
            tw = d.textlength(txt, font=f3)
            d.text(((W - tw) / 2, 1478), txt, font=f3, fill=NAVY)
        im = comp(im, cta, c)
    # legenda: sobre o peito sem cartão; logo abaixo do queixo com cartão
    y_leg = int(1210 - (1210 - 828) * k)
    im = comp(im, lambda d: legenda(d, t, y_leg))
    return im.convert('RGB')


def worker(ids, out):
    for i in ids:
        quadro(i / FPS).save(os.path.join(out, 'q%05d.jpg' % i), quality=92)


def quadros():
    out = os.path.join(AQUI, 'quadros')
    os.makedirs(out, exist_ok=True)
    n = int(math.ceil(TOTAL * FPS))
    NP = 4
    ps = [Process(target=worker, args=(list(range(k, n, NP)), out)) for k in range(NP)]
    [p.start() for p in ps]; [p.join() for p in ps]
    print('quadros', n)


def ff(*a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)


def audio():
    au = lambda f: os.path.join(AQUI, 'audio', f)
    ff('-i', au('voz_avatar.wav'), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89:level=disabled',
       '-ar', '48000', '-ac', '2', au('mix_final.wav'))


def video():
    ff('-framerate', str(FPS), '-i', os.path.join(AQUI, 'quadros', 'q%05d.jpg'), '-i', os.path.join(AQUI, 'audio', 'mix_final.wav'),
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
       '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(AQUI, 'reel_nfe_ia_avatar.mp4'))


if __name__ == '__main__':
    modo = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if modo == 'stills':
        out = os.path.join(AQUI, 'stills'); os.makedirs(out, exist_ok=True)
        for x in sys.argv[2].split(','):
            quadro(float(x)).save(os.path.join(out, 's_%05.2f.jpg' % float(x)), quality=88)
    if modo in ('quadros', 'tudo'):
        quadros()
    if modo in ('audio', 'tudo'):
        audio()
    if modo in ('video', 'tudo'):
        video()
