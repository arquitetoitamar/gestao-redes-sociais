"""Reel "emitindo NF-e pelo Claude": gravação real (homologação) + narração + títulos + legenda.

Fontes:
  captura/  gravação da janela do Claude (pedido -> prévia -> confirmação -> autorizada), ~10 qps
  rolagem/  a mesma conversa rolando pela prévia (o claude.ai não rolou sozinho na gravação), ~15 qps
uso: python3 monta.py [quadros|stills t1,t2|audio|video]   (sem argumento: tudo)
"""
import bisect, json, math, os, subprocess, sys
from multiprocessing import Process
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
FONTE = os.path.join(AQUI, 'assets', 'Inter.ttf')
ORANGE = (217, 119, 87)       # laranja do Claude
YELLOW = (250, 204, 21)
WHITE = (255, 255, 255)
GREY = (150, 150, 145)

# ---------------------------------------------------------------- narração
NARR = {n['id']: n['txt'] for n in json.load(open(os.path.join(AQUI, 'narracao.json')))}
INICIO = {'n0': 0.25, 'n1': 3.6, 'n2': 8.75, 'n3': 13.5, 'n4': 19.85, 'n5': 24.5, 'n6': 29.1, 'n7': 32.6}
TOTAL = 36.8


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


# ---------------------------------------------------------------- fontes de vídeo
class Fonte:
    def __init__(self, pasta, y0):
        self.pasta = os.path.join(AQUI, pasta)
        self.t = [float(x) for x in open(os.path.join(self.pasta, 'tempos.txt')).read().split()]
        self.y0 = y0
        self.cache = (None, None)

    def quadro(self, ts):
        i = max(0, bisect.bisect_right(self.t, ts) - 1)
        if self.cache[0] != i:
            im = cv2.imread(os.path.join(self.pasta, 'f%05d.jpg' % i))
            if self is A and ts >= 164.0:                 # chave de acesso tem o CNPJ: pixela
                x0, y0, x1, y1 = 250, 732, 1005, 790
                roi = im[y0:y1, x0:x1]
                p = cv2.resize(cv2.resize(roi, ((x1 - x0) // 22, (y1 - y0) // 22)), (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
                im[y0:y1, x0:x1] = cv2.GaussianBlur(p, (0, 0), 6)
            self.cache = (i, im)
        return self.cache[1]


A = Fonte('captura', 250)
B = Fonte('rolagem', 250)

# janela na tela do reel
CX0, CY0, CW, CH = 40, 470, 1000, 880
ASP = CH / CW

# segmentos: (início, fim, fonte, t_src_ini, t_src_fim, câmera_ini, câmera_fim, título)
# câmera = (centro x, centro y, largura) em pixels da gravação retina
FULL = (820, 968, 1590)
SEG = [
    (0.0, 3.6, 'A', 12.3, 17.44, (820, 780, 1350), (820, 772, 1390), 't0'),
    (3.6, 8.4, 'A', 17.44, 24.3, (820, 772, 1390), (820, 760, 1450), 't1'),
    (8.4, 9.4, 'A', 24.3, 27.0, (820, 800, 1590), (820, 800, 1590), 't1'),
    (9.4, 11.0, 'A', 27.0, 80.5, (820, 800, 1590), (820, 820, 1590), 't2'),
    (11.0, 13.4, 'B', 0.3, 13.0, (820, 968, 1590), (820, 968, 1590), 't2'),
    (13.4, 19.7, 'B', 16.5, 24.0, (820, 968, 1590), (735, 900, 1330), 't3'),
    (19.7, 21.3, 'A', 157.9, 168.5, (820, 700, 1590), (820, 700, 1590), 't4'),
    (21.3, 24.4, 'A', 168.5, 181.0, (800, 760, 1450), (705, 800, 1250), 't5'),
    (24.4, 29.1, 'A', 181.0, 190.0, (705, 800, 1250), (660, 880, 1150), 't6'),
]

TITULOS = {
    't0': ('EMITI UMA NOTA FISCAL', [('conversando com o ', WHITE), ('Claude', ORANGE)]),
    't1': ('1 · PEÇO EM PORTUGUÊS', [('pedido da minha loja virtual', GREY)]),
    't2': ('2 · ELE MONTA A PRÉVIA', [('sem gastar número da nota', GREY)]),
    't3': ('3 · ELE ME ALERTA', [('antes de emitir qualquer coisa', GREY)]),
    't4': ('4 · EU CONFIRMO', [('"pode emitir em homologação"', GREY)]),
    't5': ('NF-e AUTORIZADA ✓', [('na SEFAZ, com número e protocolo', GREY)]),
    't6': ('NF-e AUTORIZADA ✓', [('homologação: o ambiente de teste', GREY)]),
}


def fonte(px, peso=900):
    f = ImageFont.truetype(FONTE, px)
    f.set_variation_by_axes([32 if px >= 40 else 14, peso])
    return f


F_TIT = fonte(78, 900)
F_SUB = fonte(44, 600)
F_TAG = fonte(24, 700)
F_LEG = fonte(50, 800)

ease = lambda x: x * x * (3 - 2 * x)


def fundo():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32) + np.array([20, 20, 19], np.float32)
    g = np.exp(-(((x - 540) / 700) ** 2 + ((y - 200) / 520) ** 2))[..., None]
    base += g * (np.array(ORANGE, np.float32) - 20) * 0.22
    g2 = np.exp(-(((x - 540) / 900) ** 2 + ((y - 1900) / 500) ** 2))[..., None]
    base += g2 * np.array([37, 99, 235], np.float32) * 0.10
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


FUNDO = fundo()
MASK = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(MASK).rounded_rectangle((0, 0, CW - 1, CH - 1), 30, fill=255)
SOMBRA = Image.new('L', (W, H), 0)
ImageDraw.Draw(SOMBRA).rounded_rectangle((CX0, CY0 + 20, CX0 + CW, CY0 + CH + 20), 30, fill=150)
SOMBRA = SOMBRA.filter(ImageFilter.GaussianBlur(30))
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
    fonte_v = A if src == 'A' else B
    im = fonte_v.quadro(s0 + (s1 - s0) * u)
    k = ease(u)
    cx, cy, cw = [c0[i] + (c1[i] - c0[i]) * k for i in range(3)]
    ch = cw * ASP
    y_min, y_max = fonte_v.y0, im.shape[0]
    x0 = min(max(cx - cw / 2, 0), im.shape[1] - cw)
    y0 = min(max(cy - ch / 2, y_min), y_max - ch)
    M = np.float32([[CW / cw, 0, -x0 * CW / cw], [0, CH / ch, -y0 * CH / ch]])
    crop = cv2.warpAffine(im, M, (CW, CH), flags=cv2.INTER_AREA if cw > CW else cv2.INTER_CUBIC)
    return Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)), (tit, t - a)


def legenda(d, t):
    for nid in ('n0', 'n1', 'n2', 'n3', 'n4', 'n5'):
        ws = PAL[nid]
        if ws[0][1] - 0.15 <= t <= ws[-1][2] + 0.35:
            break
    else:
        return
    # quebra em linhas de até 900 px e mostra no máximo 2 linhas (a que contém a palavra atual)
    linhas, atual = [[]], 0
    for w in ws:
        teste = ' '.join(x[0] for x in linhas[-1] + [w])
        if d.textlength(teste, font=F_LEG) > 900 and linhas[-1]:
            linhas.append([])
        linhas[-1].append(w)
    for li, l in enumerate(linhas):
        if any(w[1] <= t for w in l):
            atual = li
    ini = (atual // 2) * 2
    y = 1395
    for l in linhas[ini:ini + 2]:
        tw = d.textlength(' '.join(w[0] for w in l), font=F_LEG)
        x = (W - tw) / 2
        for w in l:
            cor = WHITE if w[1] <= t else (110, 110, 105)
            if w[1] <= t < w[2] + 0.05:
                cor = YELLOW
            d.text((x, y), w[0], font=F_LEG, fill=cor, stroke_width=3, stroke_fill=(10, 10, 10))
            x += d.textlength(w[0] + ' ', font=F_LEG)
        y += 66


def pill(d, cx, y, txt, f, bg, fg, pad=(34, 16)):
    tw = d.textlength(txt, font=f)
    asc, desc = f.getmetrics()
    x0 = cx - tw / 2 - pad[0]
    d.rounded_rectangle((x0, y, cx + tw / 2 + pad[0], y + asc + desc + 2 * pad[1]), (asc + desc) / 2 + pad[1], fill=bg)
    d.text((x0 + pad[0], y + pad[1]), txt, font=f, fill=fg)


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
    if t < 32.45:
        a = aparece(t, 29.05)
        im = comp(im, lambda d: texto_centro(d, 430 - 30 * (1 - a), 'FUNCIONA NO', fonte(96), WHITE), a)
        itens = [('Claude', ORANGE, 'Claude'), ('ChatGPT', (16, 163, 127), 'ChatGPT'), ('API do seu sistema', (37, 99, 235), 'API')]
        for k, (txt, cor, palavra) in enumerate(itens):
            b = aparece(t, cue('n6', palavra) - 0.1, 0.3)
            y = 640 + k * 190 + 40 * (1 - b)
            f = fonte(64, 800)

            def pilula(d, txt=txt, cor=cor, y=y, f=f):
                tw = d.textlength(txt, font=f)
                x0 = (W - tw) / 2 - 70
                d.rounded_rectangle((x0, y, x0 + tw + 140, y + 130), 65, fill=(40, 40, 38, 255), outline=cor, width=4)
                d.ellipse((x0 + 34, y + 51, x0 + 62, y + 79), fill=cor)
                d.text((x0 + 92, y + 28), txt, font=f, fill=WHITE)
            im = comp(im, pilula, b)
        c = aparece(t, cue('n6', 'API') + 0.4)
        im = comp(im, lambda d: texto_centro(d, 1250, 'loja própria e marketplace', F_SUB, (200, 200, 195)), c)
        return im.convert('RGB')
    a = aparece(t, 32.45)
    im = comp(im, lambda d: texto_centro(d, 470 - 30 * (1 - a), 'COMENTA', fonte(130), WHITE), a)
    b = aparece(t, cue('n7', 'NOTA') - 0.12, 0.3)
    s = 0.7 + 0.3 * b + (0.03 * math.sin((t - 34.5) * 6) if t > 34.5 else 0)
    f = fonte(int(190 * s))

    def nota(d):
        tw = d.textlength('NOTA', font=f)
        asc, desc = f.getmetrics()
        d.rounded_rectangle((540 - tw / 2 - 50, 650, 540 + tw / 2 + 50, 650 + asc + desc + 20), 40, fill=YELLOW)
        d.text((540 - tw / 2, 660), 'NOTA', font=f, fill=(11, 22, 64))
    im = comp(im, nota, b)
    c = aparece(t, cue('n7', 'link') - 0.3)
    im = comp(im, lambda d: texto_centro(d, 960, 'que eu te mando o link', fonte(54, 700), (230, 230, 225)), c)
    e = aparece(t, cue('n7', 'link') + 0.2)
    if e > 0:
        def fim(d):
            d.rounded_rectangle((365, 1080, 715, 1240), 30, fill=WHITE)
            texto_centro(d, 1290, 'nfe.tiops.com.br', fonte(52, 800), (125, 211, 252))
        L = Image.new('RGBA', im.size, (0, 0, 0, 0))
        fim(ImageDraw.Draw(L))
        lg = LOGO.copy(); lg.thumbnail((300, 128))
        L.alpha_composite(lg, (540 - lg.width // 2, 1160 - lg.height // 2))
        if e < 0.997:
            L.putalpha(L.getchannel('A').point(lambda v: int(v * e)))
        im = Image.alpha_composite(im, L)
    return im.convert('RGB')


def quadro(t):
    if t >= 29.05:
        return cartao_final(t)
    im = FUNDO.copy()
    jan, info = janela(t)
    im.paste(Image.new('RGB', (W, H), (0, 0, 0)), (0, 0), SOMBRA)
    if jan is not None:
        im.paste(jan, (CX0, CY0), MASK)
    im = im.convert('RGBA')
    im = comp(im, lambda d: d.rounded_rectangle((CX0, CY0, CX0 + CW - 1, CY0 + CH - 1), 30, outline=(255, 255, 255, 40), width=2))
    im = comp(im, lambda d: texto_centro(d, 236, 'GRAVAÇÃO REAL  ·  AMBIENTE DE HOMOLOGAÇÃO', F_TAG, (170, 170, 165)))
    tit, dt = info
    l1, l2 = TITULOS[tit]
    # o título só anima quando muda
    muda = [s[0] for k, s in enumerate(SEG) if k == 0 or SEG[k - 1][7] != s[7]]
    t_ini = max(x for x in muda if x <= t)
    a = aparece(t, t_ini + 0.03, 0.3)
    f1 = F_TIT
    tw = ImageDraw.Draw(im).textlength(l1, font=f1)
    if tw > 1000:
        f1 = fonte(int(78 * 1000 / tw))
    im = comp(im, lambda d: texto_centro(d, 285 + 24 * (1 - a), l1, f1, WHITE), a)
    im = comp(im, lambda d: partes_centro(d, 382 + 20 * (1 - a), l2, F_SUB), a)
    im = comp(im, lambda d: legenda(d, t))
    return im.convert('RGB')


def worker(ids, out):
    for i in ids:
        quadro(i / FPS).save(os.path.join(out, 'q%05d.jpg' % i), quality=92)


def quadros():
    out = os.path.join(AQUI, 'quadros')
    os.makedirs(out, exist_ok=True)
    n = int(math.ceil(TOTAL * FPS))
    NP = 3
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
       '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(AQUI, 'reel_nfe_claude.mp4'))


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
