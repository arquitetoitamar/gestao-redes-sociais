"""Cortes verticais da live de 02/11/2026 (youtu.be/e5RfKvZPLL4), no visual dos cortes de 06/10:
fundo azul-escuro, selo, título em duas linhas, tela da live num cartão, webcam num círculo,
legenda palavra a palavra e CTA "Comenta CONNECT".

Telas com dado sensível não aparecem: nesses trechos a tela congela num quadro seguro
(zoom lento), enquanto o áudio e a webcam seguem ao vivo.

Fonte: trab/live.mp4 (1280x720, baixado do YouTube Studio; fora do git).
uso: python3 monta.py <corte> [audio|palavras|stills|video|tudo]
"""
import json, os, re, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(AQUI, 'trab')
LIVE = os.path.join(TRAB, 'live.mp4')
FONTE = os.path.join(AQUI, 'assets', 'Inter.ttf')
W, H, FPS = 1080, 1920, 30
NAVY0, NAVY1 = (8, 14, 38), (14, 30, 72)
YELLOW = (250, 204, 21)
WHITE = (255, 255, 255)
CYAN = (94, 234, 212)

# webcam da live (overlay do OBS) e o círculo do rosto dentro dela
CAM_RECT = (918, 484, 1180, 632)
ROSTO = (978, 488, 1118, 628)

# cada segmento: (início, fim, tela, recorte)
#   tela = ('live',) | ('congela', t) | ('ate', t)  -> ao vivo até t e depois segura o quadro t
#   recorte = (x0, y0, largura) no quadro 1280x720; altura = largura * CH / CW
CORTES = {
    'c1': {
        'titulo': ('QUANDO O CHATGPT TRAVA,', 'USE O CODEX'),
        'segs': [
            (1560.08, 1578.00, ('congela', 1546.0), (310, 222, 580)),
            (1534.62, 1559.22, ('ate', 1553.5), (310, 222, 580)),
            (1816.64, 1833.66, ('live',), (380, 150, 640)),
            (1580.02, 1584.88, ('congela', 1832.0), (380, 150, 640)),
        ],
    },
    'c2': {
        'titulo': ('A MELHOR EQUIPE PRA USAR IA:', 'DONO + 1 FUNCIONÁRIO'),
        'segs': [
            (2334.12, 2342.30, ('live',), (150, 80, 760)),
            (3664.26, 3723.56, ('ate', 3800.0), (150, 80, 760)),
        ],
        'congela_inicio': {1: (3683.0, 3682.0)},   # seg 1: até 3682 a tela é o Studio -> segura 3683
    },
    'c3': {
        'titulo': ('ONDE FICA A ESTRATÉGIA', 'DA SUA LOJA?'),
        'segs': [
            (2614.18, 2625.46, ('live',), (150, 80, 760)),
            (2510.36, 2545.22, ('live',), (150, 80, 760)),
            (2483.28, 2491.04, ('live',), (150, 80, 760)),
        ],
    },
    'c4': {
        'titulo': ('A IA NÃO VAI AUMENTAR', 'SUAS VENDAS'),
        'segs': [
            (4292.36, 4304.12, ('ate', 4300.0), (130, 90, 700)),
            (4305.78, 4337.94, ('congela', 4310.0), (130, 90, 700)),   # tira "opa, tem alguém mandando mensagem"
        ],
        'segura_em': 4310.0,   # depois de 4300 a tela vira WhatsApp com receita: segura o quadro 4310
    },
}

PROMPT = ('Itamar, Tiops, Marketplace Connect, ChatGPT, Claude, Codex, Mercado Livre, Meli, Shopee, '
          'anúncio, API, token, GTIN, IA, sistema interno.')
CORRIGE = {'chat': None}   # tratado em junta_chatgpt
TROCA = {
    'cloud': 'Claude', 'cláudio': 'Claude', 'claudio': 'Claude', 'codex': 'Codex', 'melly': 'Meli',
    'tiopsis': 'Tiops', 'tiópis': 'Tiops', 't-ops': 'Tiops', 'doco': 'token', 'ia': 'IA', 'ipt': 'GPT',
}

CW, CH = 1000, 760
CX0, CY0 = 40, 470
CIRC = 290
CIRC_POS = (W - 40 - CIRC + 20, CY0 + CH - CIRC // 2 - 30)
LEG_Y = 1335
DUR_CTA = 3.2


def ff(*a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)


def fonte(px, peso=900):
    f = ImageFont.truetype(FONTE, px)
    f.set_variation_by_axes([32 if px >= 40 else 14, peso])
    return f


ease = lambda x: x * x * (3 - 2 * x)


# ---------------------------------------------------------------- áudio e palavras
def audio(c):
    segs = CORTES[c]['segs']
    fc, ins = [], []
    for i, (a, b, *_ ) in enumerate(segs):
        d = b - a
        fc.append('[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st=%.3f:d=0.05[s%d]' % (a, b, d - 0.05, i))
        ins.append('[s%d]' % i)
    fc.append('%sconcat=n=%d:v=0:a=1,aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11[o]' % (''.join(ins), len(segs)))
    ff('-i', LIVE, '-filter_complex', ';'.join(fc), '-map', '[o]', '-ac', '2', '-ar', '48000', os.path.join(TRAB, c + '.wav'))
    ff('-i', os.path.join(TRAB, c + '.wav'), '-ac', '1', '-ar', '16000', os.path.join(TRAB, c + '_16k.wav'))
    print('audio', c, duracao(c))


def duracao(c):
    return sum(b - a for a, b, *_ in CORTES[c]['segs'])


def palavras(c):
    base = os.path.join(TRAB, c + '_w')
    subprocess.run(['whisper-cli', '-m', os.path.expanduser('~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin'),
                    '-l', 'pt', '-ml', '1', '-sow', '-oj', '-of', base, '--prompt', PROMPT,
                    '-f', os.path.join(TRAB, c + '_16k.wav')], check=True, capture_output=True)
    js = json.load(open(base + '.json'))
    ws = []
    for s in js['transcription']:
        t = s['text'].strip()
        if not t:
            continue
        ws.append([t, s['offsets']['from'] / 1000, s['offsets']['to'] / 1000])
    # "chat" + "GPT/IPT/de EPT" -> ChatGPT
    out = []
    for w in ws:
        k = w[0].lower().strip('.,!?')
        if out and out[-1][0].lower() == 'chat' and k in ('gpt', 'ipt', 'apt', 'ept', 'de', 'epete'):
            out[-1] = ['ChatGPT' + w[0][len(k):], out[-1][1], w[2]]
            continue
        if k in TROCA:
            w = [TROCA[k] + w[0][len(k):], w[1], w[2]]
        out.append(w)
    json.dump(out, open(os.path.join(AQUI, c + '_palavras.json'), 'w'), ensure_ascii=False, indent=0)
    print(c, ' '.join(w[0] for w in out))


# ---------------------------------------------------------------- tela da live
class Leitor:
    """Lê quadros da live em ordem crescente de tempo (seek só quando salta)."""
    def __init__(self):
        self.cap = cv2.VideoCapture(LIVE)
        self.t = -1
        self.im = None

    def quadro(self, t):
        n = int(round(t * FPS))
        if self.im is None or n < self.t or n > self.t + 45:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, n)
            self.t = n - 1
        while self.t < n:
            ok, im = self.cap.read()
            if not ok:
                break
            self.im, self.t = im, self.t + 1
        return self.im


def cobre_cam(im):
    """Apaga o overlay da webcam na tela (o rosto vai no círculo)."""
    x0, y0, x1, y1 = CAM_RECT
    cor = np.median(im[y0:y1, x0 - 14:x0 - 4].reshape(-1, 3), axis=0)
    im = im.copy()
    im[y0:y1, x0:x1] = cor
    return im


def recorte(im, x0, y0, w, zoom=1.0):
    h = w * CH / CW
    cx, cy = x0 + w / 2, y0 + h / 2
    w2, h2 = w / zoom, h / zoom
    M = np.float32([[CW / w2, 0, -(cx - w2 / 2) * CW / w2], [0, CH / h2, -(cy - h2 / 2) * CH / h2]])
    out = cv2.warpAffine(im, M, (CW, CH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


MASK_CARD = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(MASK_CARD).rounded_rectangle((0, 0, CW - 1, CH - 1), 34, fill=255)
MASK_CIRC = Image.new('L', (CIRC * 4, CIRC * 4), 0)
ImageDraw.Draw(MASK_CIRC).ellipse((0, 0, CIRC * 4 - 1, CIRC * 4 - 1), fill=255)
MASK_CIRC = MASK_CIRC.resize((CIRC, CIRC), Image.LANCZOS)


def rosto(im):
    x0, y0, x1, y1 = ROSTO
    r = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
    r = cv2.resize(r, (CIRC, CIRC), interpolation=cv2.INTER_LANCZOS4)
    p = Image.fromarray(r).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return p


# ---------------------------------------------------------------- fundo e textos
def fundo():
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(NAVY0) * (1 - g) + np.array(NAVY1) * g)[:, None, :].repeat(W, 1)
    im = Image.fromarray(arr.astype(np.uint8).reshape(H, W, 3))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 60):
        d.line((x, 0, x, H), fill=(22, 40, 86), width=1)
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=(22, 40, 86), width=1)
    return im


F_SELO = fonte(30, 800)
F_TIT = fonte(66, 900)
F_LEG = fonte(54, 850)
F_RODA = fonte(30, 600)
F_CTA = fonte(64, 900)


def centro(d, y, txt, f, cor):
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=cor)


def base(c):
    im = fundo()
    d = ImageDraw.Draw(im)
    selo = 'IA PARA MARKETPLACE · LIVE'
    w = d.textlength(selo, font=F_SELO)
    d.rounded_rectangle(((W - w) / 2 - 26, 150, (W + w) / 2 + 26, 202), 26, fill=(18, 52, 92))
    centro(d, 158, selo, F_SELO, CYAN)
    l1, l2 = CORTES[c]['titulo']
    f1 = F_TIT
    while d.textlength(max(l1, l2, key=len), font=f1) > W - 90:
        f1 = fonte(f1.size - 4, 900)
    centro(d, 240, l1, f1, WHITE)
    centro(d, 240 + f1.size + 14, l2, f1, YELLOW)
    centro(d, 1800, 'marketplaces.tiops.com.br', F_RODA, (150, 170, 210))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((CX0 + 6, CY0 + 14, CX0 + CW + 6, CY0 + CH + 14), 34, fill=(0, 0, 0, 120))
    im = im.convert('RGBA')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    return im


def legenda(d, t, ws):
    linhas, cur = [[]], None
    for w in ws:
        teste = ' '.join(x[0] for x in linhas[-1] + [w]).upper()
        if d.textlength(teste, font=F_LEG) > 940 and linhas[-1]:
            linhas.append([])
        linhas[-1].append(w)
    # blocos de 2 linhas; o bloco ativo é o da última palavra já falada
    atual = 0
    for li, l in enumerate(linhas):
        if l[0][1] <= t + 0.05:
            atual = li
    ini = (atual // 2) * 2
    vis = linhas[ini:ini + 2]
    if not vis or t > vis[-1][-1][2] + 0.6:
        return
    faladas = [w for l in vis for w in l if w[1] <= t + 0.03]
    viva = faladas[-1] if faladas and t < faladas[-1][2] + 0.25 else None
    y = LEG_Y
    for l in vis:
        txt = ' '.join(w[0] for w in l).upper()
        x = (W - d.textlength(txt, font=F_LEG)) / 2
        for w in l:
            p = w[0].upper()
            falada = w[1] <= t + 0.03
            ativa = w is viva
            cor = YELLOW if ativa else (WHITE if falada else (120, 135, 170))
            d.text((x, y), p, font=F_LEG, fill=cor, stroke_width=3, stroke_fill=(5, 10, 28))
            x += d.textlength(p + ' ', font=F_LEG)
        y += F_LEG.size + 18


def cta(im, a):
    if a <= 0:
        return
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y = int(LEG_Y - 10 + (1 - ease(a)) * 60)
    d.rounded_rectangle((90, y, W - 90, y + 150), 40, fill=YELLOW + (int(255 * a),))
    t1 = 'COMENTA CONNECT'
    w = d.textlength(t1, font=F_CTA)
    d.text(((W - w) / 2, y + 18), t1, font=F_CTA, fill=(10, 16, 40, int(255 * a)))
    t2 = 'que eu te mando o link'
    f2 = fonte(34, 700)
    w2 = d.textlength(t2, font=f2)
    d.text(((W - w2) / 2, y + 98), t2, font=f2, fill=(10, 16, 40, int(255 * a)))
    im.alpha_composite(ov)


# ---------------------------------------------------------------- composição
def plano(c):
    """Lista de (t_saida_ini, t_saida_fim, seg) para mapear tempo de saída -> tempo da live."""
    out, t = [], 0.0
    for i, s in enumerate(CORTES[c]['segs']):
        out.append((t, t + s[1] - s[0], i, s))
        t += s[1] - s[0]
    return out


def fonte_tela(c, i, s, tl, tseg):
    """Tempo do quadro de tela (pode ser congelado) e zoom."""
    a, b, tela, rec = s
    extra = CORTES[c].get('congela_inicio', {}).get(i)
    if extra and tl <= extra[1]:
        return extra[0], 1.0 + 0.04 * tseg / (b - a)
    if tela[0] == 'congela':
        return tela[1], 1.0 + 0.06 * tseg / (b - a)
    if tela[0] == 'ate' and tl > tela[1]:
        alvo = CORTES[c].get('segura_em', tela[1])
        return alvo, 1.0 + 0.06 * (tl - tela[1]) / max(b - tela[1], 1)
    return tl, 1.0


def quadros(c, tempos=None):
    BASE = base(c).convert('RGBA')
    ws = json.load(open(os.path.join(AQUI, c + '_palavras.json')))
    total = duracao(c)
    pl = plano(c)
    vivo, tela = Leitor(), Leitor()
    n = int(total * FPS)
    idx = range(n) if tempos is None else [int(t * FPS) for t in tempos]
    for k in idx:
        t = k / FPS
        for (o0, o1, i, s) in pl:
            if o0 <= t < o1 or (o1 >= total - 1e-6 and t >= o0):
                break
        tseg = t - o0
        tl = s[0] + tseg
        im_vivo = vivo.quadro(tl)
        ts, zoom = fonte_tela(c, i, s, tl, tseg)
        im_tela = im_vivo if abs(ts - tl) < 1e-6 else tela.quadro(ts)
        fr = BASE.copy()
        # cartão (a sombra já está na base)
        card = recorte(cobre_cam(im_tela), *s[3], zoom=zoom)
        fr.paste(card, (CX0, CY0), MASK_CARD)
        d = ImageDraw.Draw(fr)
        d.rounded_rectangle((CX0, CY0, CX0 + CW, CY0 + CH), 34, outline=(60, 90, 150), width=3)
        # webcam
        cx, cy = CIRC_POS
        d.ellipse((cx - 8, cy - 8, cx + CIRC + 8, cy + CIRC + 8), fill=WHITE)
        fr.paste(rosto(im_vivo), (cx, cy), MASK_CIRC)
        # legenda / CTA
        a_cta = min(max((t - (total - DUR_CTA)) / 0.35, 0), 1)
        if a_cta < 1:
            legenda(d, t, ws)
        cta(fr, a_cta)
        # barra de progresso
        d.rectangle((0, H - 14, int(W * t / total), H), fill=YELLOW)
        yield k, fr.convert('RGB')


def stills(c, tempos):
    os.makedirs(os.path.join(TRAB, 'stills'), exist_ok=True)
    for k, im in quadros(c, tempos):
        im.save(os.path.join(TRAB, 'stills', '%s_%05d.jpg' % (c, k)), quality=88)
    print('stills', c, tempos)


def video(c):
    out = os.path.join(AQUI, c + '.mp4')
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                          '-r', str(FPS), '-i', '-', '-i', os.path.join(TRAB, c + '.wav'),
                          '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                          '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest',
                          '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for k, im in quadros(c):
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    print('video', out)


if __name__ == '__main__':
    c = sys.argv[1]
    acao = sys.argv[2] if len(sys.argv) > 2 else 'tudo'
    if acao in ('audio', 'tudo'):
        audio(c)
    if acao in ('palavras', 'tudo'):
        palavras(c)
    if acao == 'stills':
        stills(c, [float(x) for x in sys.argv[3].split(',')])
    if acao in ('video', 'tudo'):
        video(c)
