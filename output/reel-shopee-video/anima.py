"""Animação "Novidade: Shopee Vídeo no Marketplace Connect" (9:16, ~19 s, voz oficial do Itamar).
Serve de final do Remix com o Reel da @shopee_br (o Itamar faz o Remix pelo app) e, sozinha, de Short.
Cena 3 usa o vídeo de produto da própria loja do Itamar (Calça Jogger, loja Shopee 393364680).

uso: python3 anima.py [stills t1,t2|video|capa]   (sem argumento: video + capa)
"""
import json, math, os, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(AQUI, *p)
W, H, FPS = 1080, 1920, 30
NAVY0, NAVY1 = (8, 14, 38), (16, 28, 70)
ORANGE = (238, 77, 45)
YELLOW = (250, 204, 21)
WHITE = (255, 255, 255)
INK = (14, 18, 32)
MUTED = (150, 165, 205)
GAP = 0.35

NARR = json.load(open(A('narracao.json')))


def dur(nid):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                 A('audio', nid + '.wav')], capture_output=True, text=True).stdout)


INICIO, t = {}, 0.3
for it in NARR:
    INICIO[it['id']] = t
    t += dur(it['id']) + GAP
TOTAL = round(t + 0.6, 2)


def palavras(nid):
    ws = json.load(open(A('audio', nid + '.words.json')))
    off = ws[0]['start']
    return [(w['text'], INICIO[nid] + w['start'] - off, INICIO[nid] + w['end'] - off) for w in ws]


PAL = {it['id']: palavras(it['id']) for it in NARR}


def cue(nid, prefixo):
    for w in PAL[nid]:
        if w[0].lower().strip('.,:!?').startswith(prefixo.lower()):
            return w[1]
    raise KeyError((nid, prefixo))


def fonte(px, peso=900):
    f = ImageFont.truetype(A('assets', 'Inter.ttf'), px)
    f.set_variation_by_axes([32 if px >= 40 else 14, peso])
    return f


ease = lambda x: x * x * (3 - 2 * x)
clamp = lambda x: min(max(x, 0.0), 1.0)


def ap(t, t0, d=0.35):
    return ease(clamp((t - t0) / d))


def back(x, s=1.7):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


# ---------------------------------------------------------------- recursos
def fundo():
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(NAVY0) * (1 - g) + np.array(NAVY1) * g)[:, None, :].repeat(W, 1)
    im = Image.fromarray(arr.astype(np.uint8).reshape(H, W, 3)).convert('RGBA')
    d = ImageDraw.Draw(im)
    for x in range(0, W, 60):
        d.line((x, 0, x, H), fill=(24, 40, 88, 255))
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=(24, 40, 88, 255))
    brilho = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(brilho).ellipse((W / 2 - 520, 420, W / 2 + 520, 1400), fill=ORANGE + (60,))
    im.alpha_composite(brilho.filter(ImageFilter.GaussianBlur(160)))
    return im


FUNDO = fundo()


def logo(nome, alt):
    im = Image.open(A('assets', nome)).convert('RGBA')
    return im.resize((int(im.width * alt / im.height), alt), Image.LANCZOS)


SHOPEE = logo('shopee.png', 230)
SHOPEE_P = logo('shopee.png', 70)
CLAUDE = Image.open(A('assets', 'claude.png')).convert('RGBA').resize((92, 92), Image.LANCZOS)
GPT = logo('chatgpt.png', 64)
TIOPS = logo('tiops-icon.png', 90)

F = {k: fonte(*v) for k, v in {
    'selo': (34, 800), 'mega': (132, 900), 'sub': (46, 700), 'chat': (44, 600), 'chatb': (44, 800),
    'chip': (40, 800), 'leg': (50, 850), 'cta': (78, 900), 'cta2': (44, 700), 'url': (32, 600), 'mini': (30, 700)}.items()}


class Video:
    def __init__(self, arq):
        self.cap = cv2.VideoCapture(arq)
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.k, self.im = -1, None

    def quadro(self, t):
        k = int(t * self.fps) % self.n
        if k < self.k:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, k); self.k = k - 1
        while self.k < k:
            ok, im = self.cap.read()
            if not ok:
                break
            self.im, self.k = im, self.k + 1
        return Image.fromarray(cv2.cvtColor(self.im, cv2.COLOR_BGR2RGB))


PROD = Video(A('trab', 'video_calca_jogger.mp4'))


def centro(d, y, txt, f, cor, x0=0, x1=W):
    w = d.textlength(txt, font=f)
    d.text((x0 + (x1 - x0 - w) / 2, y), txt, font=f, fill=cor)


def colar(fr, im, x, y, a=1.0, esc=1.0):
    if a <= 0:
        return
    if esc != 1.0:
        im = im.resize((max(1, int(im.width * esc)), max(1, int(im.height * esc))), Image.LANCZOS)
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    fr.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def check(d, x, y, s, cor):
    d.line((x, y + s * 0.5, x + s * 0.38, y + s * 0.85, x + s, y + s * 0.1), fill=cor, width=max(4, int(s / 6)), joint='curve')


def camada():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def com_alfa(fr, cam, a):
    if a <= 0:
        return
    if a < 1:
        cam.putalpha(cam.getchannel('A').point(lambda v: int(v * a)))
    fr.alpha_composite(cam)


# ---------------------------------------------------------------- cenas
T1 = INICIO['n1'] - 0.15
T2 = INICIO['n2'] - 0.15
T3 = INICIO['n3'] - 0.15


def cena_titulo(fr, t):
    sai = 1 - ap(t, T1 - 0.25, 0.3)
    if sai <= 0:
        return
    cam = camada(); d = ImageDraw.Draw(cam)
    a = ap(t, 0.05)
    selo = 'NOVIDADE NO MARKETPLACE CONNECT'
    w = d.textlength(selo, font=F['selo'])
    d.rounded_rectangle(((W - w) / 2 - 30, 360, (W + w) / 2 + 30, 420), 30, fill=(255, 255, 255, int(235 * a)))
    centro(d, 370, selo, F['selo'], INK + (int(255 * a),))
    com_alfa(fr, cam, sai)
    colar(fr, SHOPEE, W / 2, 680, sai * ap(t, 0.25), 0.5 + 0.5 * back((t - 0.25) / 0.5))
    cam = camada(); d = ImageDraw.Draw(cam)
    a2 = ap(t, cue('n0', 'Shopee') - 0.2)
    y = 880 + (1 - a2) * 40
    centro(d, y, 'SHOPEE', F['mega'], WHITE + (int(255 * a2),))
    centro(d, y + 140, 'VÍDEO', F['mega'], ORANGE + (int(255 * a2),))
    a3 = ap(t, cue('n0', 'Shopee') + 0.4)
    centro(d, 1220, 'agora pelo ChatGPT e pelo Claude', F['sub'], MUTED + (int(255 * a3),))
    com_alfa(fr, cam, sai)


def bolha(d, x0, y0, x1, linhas, f, fundo_, cor, r=34, pad=30):
    alt = len(linhas) * (f.size + 14) + 2 * pad - 14
    d.rounded_rectangle((x0, y0, x1, y0 + alt), r, fill=fundo_)
    y = y0 + pad
    for l in linhas:
        d.text((x0 + pad, y), l, font=f, fill=cor)
        y += f.size + 14
    return y0 + alt


def cena_chat(fr, t):
    if t < T1 - 0.3 or t > T2 + 0.4:
        return
    a = ap(t, T1) * (1 - ap(t, T2 - 0.1, 0.35))
    cam = camada(); d = ImageDraw.Draw(cam)
    centro(d, 330, 'Você pede, em português:', F['sub'], MUTED + (255,))
    # logos ChatGPT e Claude
    d.rounded_rectangle((180, 420, 900, 540), 60, fill=(255, 255, 255, 255))
    cam.alpha_composite(GPT, (230, 448))
    d.text((230 + GPT.width + 30, 448), 'ou', font=F['chatb'], fill=INK + (255,))
    cam.alpha_composite(CLAUDE.resize((70, 70)), (230 + GPT.width + 110, 445))
    d.text((230 + GPT.width + 195, 450), 'Claude', font=F['chatb'], fill=INK + (255,))
    # pedido digitado
    pedido = ['Publica esse vídeo na', 'Shopee Vídeo, com o link', 'do produto Calça Jogger.']
    total = sum(len(l) for l in pedido)
    k = int(total * clamp((t - (T1 + 0.4)) / 2.4))
    vis, resto = [], k
    for l in pedido:
        vis.append(l[:max(0, resto)]); resto -= len(l)
    y = bolha(d, 200, 640, 1010, [v or ' ' for v in vis], F['chat'], (37, 99, 235, 255), WHITE + (255,))
    # resposta
    tr = T1 + 3.0
    ar = ap(t, tr, 0.3)
    if ar > 0:
        r = camada(); dr = ImageDraw.Draw(r)
        y2 = bolha(dr, 70, y + 50, 880, ['Pronto. Vídeo publicado', 'na Shopee Vídeo com o', 'produto vinculado.'], F['chat'],
                   (255, 255, 255, 255), INK + (255,))
        check(dr, 800, y + 85, 46, (22, 163, 74, 255))
        r = r.transform(r.size, Image.AFFINE, (1, 0, 0, 0, 1, -(1 - ar) * 40))
        com_alfa(cam, r, ar)
    com_alfa(fr, cam, a)


PH_W, PH_H = 520, 1040
PH_X, PH_Y = 70, 330


def cena_celular(fr, t):
    if t < T2 - 0.3 or t > T3 + 0.4:
        return
    a = ap(t, T2) * (1 - ap(t, T3 - 0.1, 0.35))
    cam = camada(); d = ImageDraw.Draw(cam)
    dx = (1 - ap(t, T2, 0.5)) * -120
    x0, y0 = PH_X + dx, PH_Y
    d.rounded_rectangle((x0 - 14, y0 - 14, x0 + PH_W + 14, y0 + PH_H + 14), 70, fill=(20, 22, 30, 255))
    v = PROD.quadro(t - T2).resize((PH_W, int(PH_W * 848 / 480)), Image.LANCZOS)
    tela = Image.new('RGBA', (PH_W, PH_H), (0, 0, 0, 255))
    tela.paste(v, (0, (PH_H - v.height) // 2))
    td = ImageDraw.Draw(tela)
    # marca "Shopee Vídeo" no topo e cartão do produto embaixo (ilustração genérica, não a interface real)
    td.rounded_rectangle((24, 30, 300, 92), 31, fill=(0, 0, 0, 150))
    tela.alpha_composite(SHOPEE_P.resize((40, 50)), (40, 36))
    td.text((92, 44), 'Shopee Vídeo', font=F['mini'], fill=WHITE)
    td.rounded_rectangle((24, PH_H - 190, PH_W - 24, PH_H - 50), 24, fill=(255, 255, 255, 235))
    td.text((48, PH_H - 172), 'Calça Jogger Unissex', font=F['mini'], fill=INK)
    td.rounded_rectangle((48, PH_H - 118, 250, PH_H - 72), 23, fill=ORANGE)
    td.text((70, PH_H - 112), 'Ver produto', font=fonte(26, 800), fill=WHITE)
    m = Image.new('L', (PH_W, PH_H), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, PH_W - 1, PH_H - 1), 58, fill=255)
    cam.paste(tela, (int(x0), y0), m)
    # recursos, cada um entra na palavra falada
    itens = [('Publica', 'publica'), ('Edita o título', 'edita'), ('Visualizações', 'visualiza'), ('Quem assiste', 'quem')]
    cx = 640
    for i, (txt, chave) in enumerate(itens):
        ai = ap(t, cue('n2', chave) - 0.05, 0.3)
        if ai <= 0:
            continue
        yy = 470 + i * 200 + (1 - ai) * 30
        c = camada(); dc = ImageDraw.Draw(c)
        dc.rounded_rectangle((cx, yy, W - 50, yy + 140), 30, fill=(255, 255, 255, 255))
        dc.ellipse((cx + 26, yy + 40, cx + 86, yy + 100), fill=ORANGE + (255,))
        check(dc, cx + 39, yy + 55, 34, WHITE + (255,))
        linhas = txt.split(' ', 1) if d.textlength(txt, font=F['chip']) > 280 else [txt]
        ty = yy + 70 - len(linhas) * 24
        for l in linhas:
            dc.text((cx + 108, ty), l, font=F['chip'], fill=INK + (255,)); ty += 48
        com_alfa(cam, c, ai)
    com_alfa(fr, cam, a)


def cena_cta(fr, t):
    a = ap(t, T3)
    if a <= 0:
        return
    cam = camada(); d = ImageDraw.Draw(cam)
    colar(cam, SHOPEE, W / 2, 560, 1, 0.75)
    y = 760 + (1 - a) * 50
    d.rounded_rectangle((90, y, W - 90, y + 250), 50, fill=YELLOW + (255,))
    centro(d, y + 40, 'COMENTA CONNECT', F['cta'], INK + (255,))
    centro(d, y + 160, 'que eu te mando o link', F['cta2'], INK + (255,))
    centro(d, y + 330, 'Shopee Vídeo pelo ChatGPT e pelo Claude', F['sub'], WHITE + (255,))
    centro(d, y + 470, 'marketplaces.tiops.com.br', F['url'], MUTED + (255,))
    com_alfa(fr, cam, a)


def legenda(fr, t):
    if t >= T3:
        return
    for it in NARR:
        ws = PAL[it['id']]
        if ws[0][1] - 0.1 <= t <= ws[-1][2] + 0.3:
            break
    else:
        return
    d = ImageDraw.Draw(fr)
    linhas = [[]]
    for w in ws:
        teste = ' '.join(x[0] for x in linhas[-1] + [w]).upper()
        if d.textlength(teste, font=F['leg']) > 930 and linhas[-1]:
            linhas.append([])
        linhas[-1].append(w)
    atual = max([i for i, l in enumerate(linhas) if l[0][1] <= t + 0.05] or [0])
    ini = (atual // 2) * 2
    faladas = [w for l in linhas[ini:ini + 2] for w in l if w[1] <= t + 0.03]
    viva = faladas[-1] if faladas else None
    y = 1500
    for l in linhas[ini:ini + 2]:
        txt = ' '.join(w[0] for w in l).upper()
        x = (W - d.textlength(txt, font=F['leg'])) / 2
        for w in l:
            p = w[0].upper()
            cor = YELLOW if w is viva else (WHITE if w[1] <= t + 0.03 else (110, 125, 165))
            d.text((x, y), p, font=F['leg'], fill=cor, stroke_width=3, stroke_fill=(5, 10, 28))
            x += d.textlength(p + ' ', font=F['leg'])
        y += F['leg'].size + 16


def quadro(t):
    fr = FUNDO.copy()
    cena_titulo(fr, t)
    cena_chat(fr, t)
    cena_celular(fr, t)
    cena_cta(fr, t)
    legenda(fr, t)
    d = ImageDraw.Draw(fr)
    d.rectangle((0, H - 12, int(W * t / TOTAL), H), fill=ORANGE)
    return fr.convert('RGB')


# ---------------------------------------------------------------- saída
def audio():
    ins, fc = [], []
    for i, it in enumerate(NARR):
        ins += ['-i', A('audio', it['id'] + '.wav')]
        fc.append('[%d:a]adelay=%d|%d[a%d]' % (i, INICIO[it['id']] * 1000, INICIO[it['id']] * 1000, i))
    fc.append('%samix=inputs=%d:normalize=0,apad,atrim=0:%.2f,loudnorm=I=-14:TP=-1.5[o]' % (
        ''.join('[a%d]' % i for i in range(len(NARR))), len(NARR), TOTAL))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[o]',
                    '-ac', '2', '-ar', '48000', A('trab', 'mix.wav')], check=True)


def video():
    audio()
    out = A('reel_shopee_video.mp4')
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                          '-r', str(FPS), '-i', '-', '-i', A('trab', 'mix.wav'), '-map', '0:v', '-map', '1:a',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for k in range(int(TOTAL * FPS)):
        p.stdin.write(quadro(k / FPS).tobytes())
    p.stdin.close(); p.wait()
    print('video', out, TOTAL)


def capa():
    fr = FUNDO.copy()
    d = ImageDraw.Draw(fr)
    selo = 'NOVA INTEGRAÇÃO'
    w = d.textlength(selo, font=F['selo'])
    d.rounded_rectangle(((W - w) / 2 - 30, 330, (W + w) / 2 + 30, 390), 30, fill=WHITE)
    centro(d, 340, selo, F['selo'], INK)
    colar(fr, SHOPEE, W / 2, 640, 1, 1.0)
    f = fonte(150, 900)
    centro(d, 820, 'SHOPEE', f, WHITE)
    centro(d, 980, 'VÍDEOS', f, ORANGE)
    centro(d, 1190, 'no Marketplace Connect', F['sub'], MUTED)
    centro(d, 1260, 'pelo ChatGPT e pelo Claude', F['sub'], MUTED)
    fr.convert('RGB').save(A('capa.jpg'), quality=92)
    print('capa', A('capa.jpg'))


if __name__ == '__main__':
    acao = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if acao == 'stills':
        os.makedirs(A('trab', 'stills'), exist_ok=True)
        for x in sys.argv[2].split(','):
            quadro(float(x)).save(A('trab', 'stills', 's_%05.2f.jpg' % float(x)), quality=88)
        print('TOTAL', TOTAL, INICIO)
    if acao in ('capa', 'tudo'):
        capa()
    if acao in ('video', 'tudo'):
        video()
