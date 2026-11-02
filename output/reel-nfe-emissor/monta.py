"""Reel do Emissor NF-e (v2, formato "dono falando" adaptado): animações da landing + voz clonada
+ título no topo + legenda palavra a palavra + cartão final "Comenta NOTA".

Fontes: build/aNN/fXXXXX.jpg (quadros das animações de ~/git/nfe-tiops/divulgacao/reel-animacoes, 30 qps).
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
GREY = (90, 102, 125)
VERDE = (22, 163, 74)

# ---------------------------------------------------------------- narração
NARR = {n['id']: n['txt'] for n in json.load(open(os.path.join(AQUI, 'narracao.json')))}
INICIO = {'n0': 0.2, 'n1': 3.35, 'n2': 10.5, 'n3': 18.9, 'n4': 23.4, 'n5': 28.95}
TOTAL = 35.4
T_CTA = 28.7


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


# ---------------------------------------------------------------- fontes (animações)
COBRE = {'02': (815, 522, 1000, 584), '03': (870, 618, 1010, 662), '04': (835, 288, 1005, 332)}


class Fonte:
    def __init__(self, k):
        self.k = k
        self.pasta = os.path.join(AQUI, 'build', 'a' + k)
        self.n = len(os.listdir(self.pasta))
        self.cache = (None, None)

    def quadro(self, ts):
        i = min(max(int(round(ts * FPS)), 0), self.n - 1)
        if self.cache[0] != i:
            im = cv2.imread(os.path.join(self.pasta, 'f%05d.jpg' % (i + 1)))
            if self.k in COBRE:                              # setas e pausa da animação
                x0, y0, x1, y1 = COBRE[self.k]
                im[y0:y1, x0:x1] = 255
            self.cache = (i, im)
        return self.cache[1]


FONTES = {k: Fonte(k) for k in ('01', '02', '03', '04')}

# janela no reel
CX0, CY0, CW, CH = 40, 400, 1000, 1000
ASP = CH / CW

# segmentos: (início, fim, animação, t_src_ini, t_src_fim, câmera_ini, câmera_fim, título)
# câmera = (centro x, centro y, largura) na animação 1080x1920
SEG = [
    (0.0, 3.3, '01', 29.4, 33.4, (540, 1020, 1060), (540, 1080, 1000), 't0'),
    (3.3, 10.45, '04', 0.0, 14.4, (540, 1060, 1060), (540, 1100, 960), 't1'),
    (10.45, 14.5, '01', 0.0, 8.6, (540, 900, 1060), (540, 960, 1040), 't2'),
    (14.5, 18.85, '01', 17.6, 26.2, (540, 960, 1040), (540, 1000, 1000), 't3'),
    (18.85, 23.35, '03', 2.2, 12.6, (465, 880, 850), (465, 1190, 850), 't4'),
    (23.35, 28.7, '02', 0.0, 11.5, (540, 1060, 1000), (540, 1060, 960), 't5'),
]

TITULOS = {
    't0': ('AINDA PAGA ALGUÉM', [('só pra emitir ', NAVY), ('nota fiscal?', BLUE)]),
    't1': ('TODO DIA, A MESMA COISA', [('campo, imposto, XML, pedido…', GREY)]),
    't2': ('A VENDA VIRA NOTA', [('CFOP, ICMS e DIFAL calculados', GREY)]),
    't3': ('DIRETO NA SEFAZ', [('site, WhatsApp, empresa, marketplace', GREY)]),
    't4': ('VAI SOZINHA PRO PEDIDO', [('Mercado Livre e Shopee', GREY)]),
    't5': ('PAINEL, API OU IA', [('é só pedir pro ', GREY), ('ChatGPT', (16, 163, 127)), (' ou pro ', GREY), ('Claude', (217, 119, 87))]),
}


def fonte(px, peso=900):
    f = ImageFont.truetype(FONTE, px)
    f.set_variation_by_axes([32 if px >= 40 else 14, peso])
    return f


F_TIT = fonte(80, 900)
F_SUB = fonte(44, 600)
F_LEG = fonte(52, 800)

ease = lambda x: x * x * (3 - 2 * x)


def fundo():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32) + np.array([244, 248, 255], np.float32)
    g = np.exp(-(((x - 540) / 700) ** 2 + ((y - 150) / 450) ** 2))[..., None]
    base += g * (np.array([214, 228, 255], np.float32) - 244) * 0.9
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


FUNDO = fundo()
MASK = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(MASK).rounded_rectangle((0, 0, CW - 1, CH - 1), 36, fill=255)
SOMBRA = Image.new('L', (W, H), 0)
ImageDraw.Draw(SOMBRA).rounded_rectangle((CX0 + 10, CY0 + 24, CX0 + CW - 10, CY0 + CH + 24), 36, fill=60)
SOMBRA = SOMBRA.filter(ImageFilter.GaussianBlur(28))
LOGO = Image.open(os.path.join(AQUI, 'assets', 'logo-tiops.png')).convert('RGBA')


def texto_centro(d, y, txt, f, cor, w=W):
    tw = d.textlength(txt, font=f)
    d.text(((w - tw) / 2, y), txt, font=f, fill=cor)


def partes_centro(d, y, partes, f):
    tw = sum(d.textlength(t, font=f) for t, _ in partes)
    x = (W - tw) / 2
    for t, c in partes:
        d.text((x, y), t, font=f, fill=c)
        x += d.textlength(t, font=f)


def janela(t):
    for s in SEG:
        if s[0] <= t < s[1]:
            break
    else:
        return None, None
    a, b, src, s0, s1, c0, c1, tit = s
    u = (t - a) / (b - a)
    im = FONTES[src].quadro(s0 + (s1 - s0) * u)
    k = ease(u)
    cx, cy, cw = [c0[i] + (c1[i] - c0[i]) * k for i in range(3)]
    ch = cw * ASP
    x0 = min(max(cx - cw / 2, 0), im.shape[1] - cw) if cw <= im.shape[1] else (im.shape[1] - cw) / 2
    y0 = min(max(cy - ch / 2, 0), 1610 - ch)                # nunca mostra os controles da base
    M = np.float32([[CW / cw, 0, -x0 * CW / cw], [0, CH / ch, -y0 * CH / ch]])
    crop = cv2.warpAffine(im, M, (CW, CH), flags=cv2.INTER_AREA if cw > CW else cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)), (tit, t - a)


def legenda(d, t):
    for nid in ('n0', 'n1', 'n2', 'n3', 'n4'):
        ws = PAL[nid]
        if ws[0][1] - 0.15 <= t <= ws[-1][2] + 0.35:
            break
    else:
        return
    linhas, atual = [[]], 0
    for w in ws:
        teste = ' '.join(x[0] for x in linhas[-1] + [w])
        if d.textlength(teste, font=F_LEG) > 880 and linhas[-1]:
            linhas.append([])
        linhas[-1].append(w)
    for li, l in enumerate(linhas):
        if any(w[1] <= t for w in l):
            atual = li
    ini = (atual // 2) * 2
    mostra = linhas[ini:ini + 2]
    y = 1440
    alt = 70 * len(mostra) + 34
    larg = max(d.textlength(' '.join(w[0] for w in l), font=F_LEG) for l in mostra) + 70
    d.rounded_rectangle(((W - larg) / 2, y - 18, (W + larg) / 2, y - 18 + alt), 34, fill=(14, 22, 48, 235))
    for l in mostra:
        tw = d.textlength(' '.join(w[0] for w in l), font=F_LEG)
        x = (W - tw) / 2
        for w in l:
            cor = WHITE if w[1] <= t else (120, 130, 155)
            if w[1] <= t < w[2] + 0.05:
                cor = YELLOW
            d.text((x, y), w[0], font=F_LEG, fill=cor)
            x += d.textlength(w[0] + ' ', font=F_LEG)
        y += 70


def comp(im, fn, a=1.0):
    if a <= 0.003:
        return im
    L = Image.new('RGBA', im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(L))
    if a < 0.997:
        L.putalpha(L.getchannel('A').point(lambda v: int(v * a)))
    return Image.alpha_composite(im, L)


def aparece(t, t0, d=0.35):
    return ease(min(max((t - t0) / d, 0), 1))


def cartao_final(t):
    im = FUNDO.convert('RGBA')
    a = aparece(t, T_CTA + 0.05)
    im = comp(im, lambda d: texto_centro(d, 330 - 30 * (1 - a), 'TESTE GRÁTIS', fonte(110), NAVY), a)
    im = comp(im, lambda d: texto_centro(d, 470 - 20 * (1 - a), 'em homologação, sem cartão', fonte(52, 700), GREY), a)
    b = aparece(t, cue('n5', 'Comenta') - 0.1)
    im = comp(im, lambda d: texto_centro(d, 650 - 30 * (1 - b), 'COMENTA', fonte(120), NAVY), b)
    c = aparece(t, cue('n5', 'NOTA') - 0.12, 0.3)
    s = 0.7 + 0.3 * c + (0.03 * math.sin((t - cue('n5', 'NOTA') - 0.4) * 6) if t > cue('n5', 'NOTA') + 0.4 else 0)
    f = fonte(int(200 * s))

    def nota(d):
        tw = d.textlength('NOTA', font=f)
        asc, desc = f.getmetrics()
        d.rounded_rectangle((540 - tw / 2 - 56, 820, 540 + tw / 2 + 56, 820 + asc + desc + 24), 44, fill=YELLOW)
        d.text((540 - tw / 2, 832), 'NOTA', font=f, fill=NAVY)
    im = comp(im, nota, c)
    e = aparece(t, cue('n5', 'link') - 0.3)
    im = comp(im, lambda d: texto_centro(d, 1130, 'que eu te mando o link', fonte(56, 700), NAVY), e)
    g = aparece(t, cue('n5', 'link') + 0.15)
    if g > 0:
        L = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        d.rounded_rectangle((350, 1250, 730, 1420), 34, fill=WHITE)
        texto_centro(d, 1450, 'nfe.tiops.com.br', fonte(54, 800), BLUE)
        lg = LOGO.copy(); lg.thumbnail((320, 140))
        L.alpha_composite(lg, (540 - lg.width // 2, 1335 - lg.height // 2))
        if g < 0.997:
            L.putalpha(L.getchannel('A').point(lambda v: int(v * g)))
        im = Image.alpha_composite(im, L)
    return im.convert('RGB')


def quadro(t):
    if t >= T_CTA:
        return cartao_final(t)
    im = FUNDO.copy()
    jan, info = janela(t)
    im.paste(Image.new('RGB', (W, H), (60, 80, 140)), (0, 0), SOMBRA)
    if jan is not None:
        im.paste(jan, (CX0, CY0), MASK)
    im = im.convert('RGBA')
    im = comp(im, lambda d: d.rounded_rectangle((CX0, CY0, CX0 + CW - 1, CY0 + CH - 1), 36, outline=(200, 214, 240, 255), width=3))
    tit, dt = info
    l1, l2 = TITULOS[tit]
    muda = [s[0] for k, s in enumerate(SEG) if k == 0 or SEG[k - 1][7] != s[7]]
    t_ini = max(x for x in muda if x <= t)
    a = aparece(t, t_ini + 0.03, 0.3)
    f1 = F_TIT
    tw = ImageDraw.Draw(im).textlength(l1, font=f1)
    if tw > 1000:
        f1 = fonte(int(80 * 1000 / tw))
    im = comp(im, lambda d: texto_centro(d, 190 + 24 * (1 - a), l1, f1, NAVY), a)
    im = comp(im, lambda d: partes_centro(d, 292 + 20 * (1 - a), l2, F_SUB), a)
    im = comp(im, lambda d: legenda(d, t))
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
    from scipy.io import wavfile
    SR = 48000
    N = int((TOTAL + 0.2) * SR)
    narr = np.zeros(N)
    for nid, t0 in INICIO.items():
        sr, x = wavfile.read(os.path.join(AQUI, 'audio', nid + '.wav'))
        x = x.astype(float) / 32768
        i = int(t0 * SR)
        narr[i:i + len(x)] += x[:N - i]
    wavfile.write(os.path.join(AQUI, 'audio', 'narracao_full.wav'), SR, (np.clip(narr, -1, 1) * 32767).astype(np.int16))
    au = lambda f: os.path.join(AQUI, 'audio', f)
    ff('-i', au('narracao_full.wav'), '-af', 'loudnorm=I=-16:TP=-2:LRA=9', '-ar', '48000', '-ac', '2', au('narr_norm.wav'))
    # trilha sintetizada do Reel de lançamento (sem direitos de terceiros), cortada e com fade
    ff('-i', os.path.join(AQUI, '..', 'reel-nfe-tiops', 'audio', 'musica.wav'), '-t', str(TOTAL + 0.2),
       '-af', 'afade=t=out:st=%.2f:d=2.5,loudnorm=I=-31:TP=-6:LRA=7' % (TOTAL - 2.3), '-ar', '48000', au('mus_norm.wav'))
    ff('-i', au('mus_norm.wav'), '-i', au('narr_norm.wav'), '-filter_complex',
       '[0][1]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=350[m];[m][1]amix=inputs=2:normalize=0:duration=longest[a]',
       '-map', '[a]', au('mix_pre.wav'))
    ff('-i', au('mix_pre.wav'), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89:level=disabled', '-ar', '48000', au('mix_final.wav'))


def video():
    ff('-framerate', str(FPS), '-i', os.path.join(AQUI, 'quadros', 'q%05d.jpg'), '-i', os.path.join(AQUI, 'audio', 'mix_final.wav'),
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
       '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(AQUI, 'reel_nfe_emissor.mp4'))


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
