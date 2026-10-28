#!/usr/bin/env python3
"""Montagem final do vídeo "Escritório de Agentes no Mercado Livre".

Abertura (videos/abertura.mp4) + gravação acelerada (cortes.py) com:
- desfoque à prova de falha da janela do navegador (só rótulos do app lidos
  pelo OCR, a ilustração do escritório e a câmera ficam nítidos);
- selo "dados de clientes ocultos", faixa de capítulo, cartões de prompt;
- B-roll animado (videos/broll) em cartão grande por cima da tela;
- painel lateral com vídeo vertical da Imersão em algumas transições;
- cartela final com o link.

  python3 render.py                     vídeo inteiro -> videos/final.mp4
  python3 render.py teste <ini> <fim>   só o miolo entre ini e fim (s, tempo final) -> videos/teste.mp4
  python3 render.py quadros t1,t2,...   PNGs de conferência (tempo final do miolo)
"""
import bisect, glob, json, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import ocr

AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, 'trab')
V = os.path.join(AQUI, 'videos')
SRC = os.path.join(V, 'bruto.mp4')
W, H, FPS = 1920, 1080, 30
NQ = 28577
PASSO = 6
WIN = (63, 100, 1652, 968)                 # janela do navegador abaixo da barra do macOS
CAM = (1612, 772, 1876, 1036)              # balão da câmera
FONTE = '/Users/itamar/git/gestao-redes-sociais/output/reel-explica-marketplace-connect/assets/Inter.ttf'
YEL, INK, BRANCO = (0, 196, 245), (12, 11, 11), (255, 255, 255)   # BGR
DRIVE = os.path.expanduser('~/Library/CloudStorage/GoogleDrive-isantos.ads@gmail.com/Meu Drive/Fotos e videos de imersao')

SEG = json.load(open(os.path.join(T, 'segmentos.json')))
FAT = SEG['fat']
SEGS = SEG['seg']
C0S = [s[0] for s in SEGS]
DUR = SEGS[-1][1] / FAT                    # duração do miolo (s)

CAPITULOS = [  # (tempo no bruto, título)
    (0.0, 'O que é o GestorPro'),
    (23.3, 'CRM de clientes'),
    (63.3, 'Recomendação de produtos com IA'),
    (144.5, 'Recomendação pelo WhatsApp com o Claude'),
    (381.4, 'Link pelo chat do pedido'),
    (442.4, 'Pós-venda e devoluções'),
    (477.8, 'Contestação com a IA do Mercado Livre'),
    (508.9, 'Concorrentes e decisões para aprovar'),
    (562.1, 'Ajuste de preço na banda de margem'),
    (628.7, 'Margem por canal e análise do anúncio'),
    (708.7, 'Ads e promoções do anúncio'),
    (731.0, 'Campanhas e promoções automáticas'),
    (809.8, 'Perguntas, expedição e nota fiscal'),
    (854.8, 'Como os agentes enxergam a operação'),
    (896.4, 'Reunião e conversa com os agentes'),
    (924.8, 'Como começar'),
]
PROMPTS = [  # (bruto ini, bruto fim, texto) — o chat fica desfocado, o pedido aparece em cartão
    (182.5, 196.0, 'Mande o link das recomendações por WhatsApp. Não envie sem eu conferir antes.'),
    (291.2, 299.5, 'Envie os links e a mensagem pelo WhatsApp.'),
]
LATERAIS = [  # (bruto ini, arquivo vertical da Imersão, início no clipe)
    (235.0, 'IMG_9714.MOV', 6.0),
    (466.0, 'IMG_9716.MOV', 5.0),
    (608.0, 'IMG_9806.MOV', 66.0),
    (806.0, 'IMG_9715.MOV', 12.0),
    (925.0, 'IMG_9703.MOV', 18.0),
]
LAT_DUR = 6.0


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


# ---------------------------------------------------------------- texto
_fontes = {}


def fonte(px):
    if px not in _fontes:
        f = ImageFont.truetype(FONTE, px)
        try:
            f.set_variation_by_name('Black')
        except Exception:
            try:
                f.set_variation_by_axes([900])
            except Exception:
                pass
        _fontes[px] = f
    return _fontes[px]


def sprite_texto(txt, px, cor=(255, 255, 255), fundo=None, pad=(18, 10), raio=10, larg_max=None):
    """BGRA com o texto (quebra linhas se larg_max)."""
    f = fonte(px)
    linhas = [txt]
    if larg_max:
        linhas, cur = [], ''
        for p in txt.split():
            tst = (cur + ' ' + p).strip()
            if f.getlength(tst) > larg_max and cur:
                linhas.append(cur)
                cur = p
            else:
                cur = tst
        linhas.append(cur)
    lw = int(max(f.getlength(l) for l in linhas))
    lh = int(px * 1.25)
    w, h = lw + 2 * pad[0], lh * len(linhas) + 2 * pad[1]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if fundo:
        d.rounded_rectangle([0, 0, w - 1, h - 1], raio, fill=fundo)
    for k, l in enumerate(linhas):
        d.text((pad[0], pad[1] + k * lh), l, font=f, fill=cor)
    a = np.array(im)
    return cv2.cvtColor(a, cv2.COLOR_RGBA2BGRA)


def cola(dst, spr, x, y, alpha=1.0):
    h, w = spr.shape[:2]
    x, y = int(x), int(y)
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (s[:, :, 3:4].astype(np.float32) / 255.0) * alpha
    roi = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (roi * (1 - a) + s[:, :, :3].astype(np.float32) * a).astype(np.uint8)


def arredonda(img, raio):
    h, w = img.shape[:2]
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (raio, 0), (w - raio, h), 255, -1)
    cv2.rectangle(m, (0, raio), (w, h - raio), 255, -1)
    for cx, cy in ((raio, raio), (w - raio, raio), (raio, h - raio), (w - raio, h - raio)):
        cv2.circle(m, (cx, cy), raio, 255, -1, cv2.LINE_AA)
    return np.dstack([img, m])


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


# ---------------------------------------------------------------- desfoque
class Privacidade:
    def __init__(self):
        self.ocr = {}
        for f in glob.glob(os.path.join(T, 'ocr', '*.json')):
            for k, v in json.load(open(f)).items():
                self.ocr[int(k)] = v
        tpl = cv2.imread(os.path.join(T, 'office_tpl.png'))
        self.tpl = cv2.resize(cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY), None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        self.amostra = None           # (índice, cinza) do último quadro com OCR
        self.prontas = {}
        self.faltando = 0

    def ve_amostra(self, idx, quadro):
        if idx % PASSO == 0:
            self.amostra = (idx, cv2.cvtColor(quadro, cv2.COLOR_BGR2GRAY))

    def aplica(self, idx, q):
        x0, y0, x1, y1 = WIN
        out = q.copy()
        reg = q[y0:y1, x0:x1]
        peq = cv2.resize(reg, ((x1 - x0) // 10, (y1 - y0) // 10), interpolation=cv2.INTER_AREA)
        peq = cv2.GaussianBlur(peq, (0, 0), 1.6)
        out[y0:y1, x0:x1] = cv2.resize(peq, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
        g = cv2.cvtColor(q, cv2.COLOR_BGR2GRAY)
        # rótulos do app (só se o quadro não mudou desde a leitura do OCR)
        k = idx - idx % PASSO
        caixas = self.ocr.get(k)
        if caixas is not None and k not in self.prontas:
            self.prontas[k] = ocr.caixas_nitidas(caixas)
        caixas = self.prontas.get(k)
        if caixas is None:
            self.faltando += 1
        elif self.amostra and self.amostra[0] == k:
            ga = self.amostra[1]
            for bx0, by0, bx1, by1 in caixas:
                bx0, by0 = max(bx0, x0), max(by0, y0)
                bx1, by1 = min(bx1, x1), min(by1, y1)
                if bx1 <= bx0 or by1 <= by0:
                    continue
                if np.mean(cv2.absdiff(g[by0:by1, bx0:bx1], ga[by0:by1, bx0:bx1])) < 5:
                    out[by0:by1, bx0:bx1] = q[by0:by1, bx0:bx1]
        # ilustração do escritório (sem a faixa de legenda, que cita produto)
        gp = cv2.resize(g[y0:y1, x0:x1], None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        r = cv2.matchTemplate(gp, self.tpl, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(r)
        if mx > 0.55:
            ox, oy = x0 + loc[0] * 4, y0 + loc[1] * 4
            th, tw = self.tpl.shape[0] * 4, self.tpl.shape[1] * 4
            out[oy:oy + th, ox:ox + tw] = q[oy:oy + th, ox:ox + tw]
        cx0, cy0, cx1, cy1 = CAM
        out[cy0:cy1, cx0:cx1] = q[cy0:cy1, cx0:cx1]
        return out


# ---------------------------------------------------------------- leitura de vídeo
class Leitor:
    def __init__(self, caminho, w=W, h=H, ss=0.0, vf=None):
        self.w, self.h = w, h
        cmd = ['ffmpeg', '-v', 'error', '-ss', '%.3f' % ss, '-i', caminho]
        filtro = vf or 'scale=%d:%d' % (w, h)
        cmd += ['-vf', filtro + ',fps=30', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
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
    """Lê o bruto em sequência e entrega o quadro de índice pedido (sempre crescente)."""
    def __init__(self, priv, ini=0):
        self.priv = priv
        self.idx = ini - 1
        self.l = Leitor(SRC, ss=ini / 30)
        self.q = None

    def quadro(self, alvo):
        while self.idx < alvo:
            self.q = self.l.proximo()
            self.idx += 1
            self.priv.ve_amostra(self.idx, self.q)
        return self.q


# ---------------------------------------------------------------- camadas
class Camadas:
    def __init__(self):
        self.selo = sprite_texto('DADOS DE CLIENTES OCULTOS', 22, (255, 255, 255), fundo=(20, 20, 24, 225), pad=(16, 8), raio=16)
        cad = sprite_texto('●', 22, (230, 70, 70))
        self.selo_dot = cad
        self.cap = [(final_t(s), t) for s, t in CAPITULOS]
        self.cap_spr = {}
        self.prompts = [(final_t(a), final_t(b), txt) for a, b, txt in PROMPTS]
        self.prompt_spr = {}
        man = json.load(open(os.path.join(V, 'broll', 'manifest.json'))) if os.path.exists(os.path.join(V, 'broll', 'manifest.json')) else []
        self.broll = []
        for m in man:
            arq = os.path.join(V, 'broll', m['arquivo'])
            if os.path.exists(arq):
                self.broll.append([final_t(float(m['momento_bruto_s'])), float(m['duracao_s']), arq, None])
        self.lat = [[final_t(s), os.path.join(V, 'lat', a.replace('.MOV', '.mp4')), 0.0, None] for s, a, ss in LATERAIS]
        self.sombra = None

    def capitulo(self, f, t):
        for i, (t0, titulo) in enumerate(self.cap):
            if t0 <= t < t0 + 4.2 and t > 0.3:
                k = t - t0
                a = ease(k / 0.35) * (1 - ease((k - 3.7) / 0.5))
                if i not in self.cap_spr:
                    num = sprite_texto('%02d' % (i + 1), 34, (11, 11, 12), fundo=(245, 196, 0, 255), pad=(14, 6), raio=8)
                    tit = sprite_texto(titulo.upper(), 34, (255, 255, 255), fundo=(12, 11, 11, 235), pad=(16, 6), raio=8)
                    self.cap_spr[i] = (num, tit)
                num, tit = self.cap_spr[i]
                dx = (1 - ease(k / 0.4)) * -60
                cola(f, num, 70 + dx, 990, a)
                cola(f, tit, 70 + num.shape[1] + 8 + dx, 990, a)

    def prompt(self, f, t):
        for i, (a0, a1, txt) in enumerate(self.prompts):
            if a0 <= t < a1:
                if i not in self.prompt_spr:
                    tag = sprite_texto('PEDIDO AO AGENTE', 22, (11, 11, 12), fundo=(245, 196, 0, 255), pad=(12, 5), raio=6)
                    corpo = sprite_texto('“' + txt + '”', 40, (255, 255, 255), fundo=(12, 11, 11, 240), pad=(26, 18), raio=14, larg_max=820)
                    self.prompt_spr[i] = (tag, corpo)
                tag, corpo = self.prompt_spr[i]
                k = t - a0
                al = ease(k / 0.3) * (1 - ease((k - (a1 - a0 - 0.3)) / 0.3))
                y = 360 + (1 - ease(k / 0.35)) * 40
                x = 1180 - corpo.shape[1] // 2
                cola(f, corpo, x, y, al)
                cola(f, tag, x + 22, y - tag.shape[0] + 6, al)

    def broll_em(self, t):
        for b in self.broll:
            if b[0] <= t < b[0] + b[1]:
                return b
        return None

    def aplica_broll(self, f, t, b):
        t0, dur, arq, lr = b
        k = t - t0
        if lr is None:
            b[3] = lr = Leitor(arq)
        clip = lr.proximo()
        e = ease(k / 0.3) * (1 - ease((k - (dur - 0.3)) / 0.3))
        esc = 0.78 + 0.04 * e
        cw, ch = int(W * esc), int(H * esc)
        c = cv2.resize(clip, (cw, ch), interpolation=cv2.INTER_AREA)
        c = arredonda(c, 26)
        f[:] = (f.astype(np.float32) * (1 - 0.55 * e)).astype(np.uint8)
        cola(f, c, (W - cw) // 2, (H - ch) // 2 - 10, e)

    def lateral_em(self, t):
        for b in self.lat:
            if b[0] <= t < b[0] + LAT_DUR:
                return b
        return None

    def aplica_lateral(self, f, t, b):
        t0, arq, ss, lr = b
        k = t - t0
        if lr is None:
            b[3] = lr = Leitor(arq, w=405, h=720, ss=ss, vf='scale=405:720')
        clip = lr.proximo()
        e = ease(k / 0.45) * (1 - ease((k - (LAT_DUR - 0.45)) / 0.45))
        fundo = cv2.GaussianBlur(cv2.resize(f, (W // 8, H // 8)), (0, 0), 3)
        fundo = (cv2.resize(fundo, (W, H)) * 0.35 + np.array(INK) * 0.65).astype(np.uint8)
        esc = 1 - 0.27 * e
        sw, sh = int(W * esc), int(H * esc)
        tela = cv2.resize(f, (sw, sh), interpolation=cv2.INTER_AREA)
        x = int(0 + (40 - 0) * e)
        y = int((H - sh) / 2)
        base = fundo.copy()
        cola(base, arredonda(tela, int(24 * e) + 1), x, y)
        vx = int(W + 40 - (W + 40 - 1470) * e)
        cola(base, arredonda(clip, 22), vx, 150)
        if not hasattr(self, 'lat_tag'):
            self.lat_tag = sprite_texto('IMERSÃO IA PARA MARKETPLACES', 20, (11, 11, 12), fundo=(245, 196, 0, 255), pad=(12, 6), raio=6)
        cola(base, self.lat_tag, vx + 405 // 2 - self.lat_tag.shape[1] // 2, 150 + 720 + 16, e)
        f[:] = base

    def selo_on(self, f, t):
        a = ease((t - 0.5) / 0.5)
        cola(f, self.selo, 1652 - self.selo.shape[1], 28, a)


def cartela_final(n):
    """Últimos segundos: link do GestorPro."""
    f = np.zeros((H, W, 3), np.uint8)
    f[:] = INK
    t = n / FPS
    a = ease(t / 0.5)
    l1 = sprite_texto('CONHEÇA O GESTORPRO', 84, (255, 255, 255))
    l2 = sprite_texto('gestorpro.tiops.com.br', 64, (11, 11, 12), fundo=(245, 196, 0, 255), pad=(30, 14), raio=12)
    l3 = sprite_texto('link na descrição do vídeo', 36, (200, 200, 200))
    cola(f, l1, (W - l1.shape[1]) // 2, 380 - (1 - a) * 30, a)
    cola(f, l2, (W - l2.shape[1]) // 2, 520, ease((t - 0.3) / 0.5))
    cola(f, l3, (W - l3.shape[1]) // 2, 650, ease((t - 0.6) / 0.5))
    return f


FINAL_DUR = 8.0


def miolo(saida_frames, t_ini=0.0, t_fim=None, so=None):
    priv = Privacidade()
    cam = Camadas()
    t_fim = DUR if t_fim is None else t_fim
    n0, n1 = int(t_ini * FPS), int(t_fim * FPS)
    alvo0 = int(round(fonte_t(t_ini) * 30))
    br = Bruto(priv, ini=max(0, alvo0 - alvo0 % PASSO))
    for n in range(n0, n1):
        t = n / FPS
        idx = min(NQ - 1, int(round(fonte_t(t) * 30)))
        q = br.quadro(idx)
        if so is not None and n not in so:
            continue
        f = priv.aplica(idx, q)
        cam.selo_on(f, t)
        cam.prompt(f, t)
        lat = cam.lateral_em(t)
        b = cam.broll_em(t)
        if lat:
            cam.aplica_lateral(f, t, lat)
        if b:
            cam.aplica_broll(f, t, b)
        cam.capitulo(f, t)
        saida_frames(n, f)
    print('quadros sem OCR:', priv.faltando, file=sys.stderr)


def encoder(caminho, audio=None):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H),
           '-r', str(FPS), '-i', '-']
    if audio:
        cmd += ['-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart', caminho]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    if modo == 'quadros':
        ts = [float(x) for x in sys.argv[2].split(',')]
        alvos = {int(t * FPS): t for t in ts}
        for t in sorted(ts):
            def grava(n, f, t=t):
                cv2.imwrite(os.path.join(T, 'q-%07.2f.jpg' % (n / FPS)), f, [cv2.IMWRITE_JPEG_QUALITY, 88])
            miolo(grava, t, t + 1 / FPS)
        return
    if modo == 'teste':
        a, b = float(sys.argv[2]), float(sys.argv[3])
        out = os.path.join(V, 'teste.mp4')
        enc = encoder(out)
        miolo(lambda n, f: enc.stdin.write(f.tobytes()), a, b)
        enc.stdin.close(); enc.wait()
        print(out)
        return
    # vídeo inteiro: abertura + miolo + cartela
    tmp = os.path.join(V, 'final.mp4')
    enc = encoder(tmp, os.path.join(T, 'audio_final.wav'))
    ab = os.path.join(V, 'abertura.mp4')
    nab = 0
    if os.path.exists(ab):
        la = Leitor(ab)
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', ab],
                                 capture_output=True, text=True).stdout)
        nab = int(round(d * FPS))
        for _ in range(nab):
            enc.stdin.write(la.proximo().tobytes())
        la.fecha()
    miolo(lambda n, f: enc.stdin.write(f.tobytes()))
    for n in range(int(FINAL_DUR * FPS)):
        enc.stdin.write(cartela_final(n).tobytes())
    enc.stdin.close(); enc.wait()
    json.dump({'abertura_s': nab / FPS, 'miolo_s': DUR, 'final_s': FINAL_DUR}, open(os.path.join(T, 'tempos.json'), 'w'))
    print(tmp, nab / FPS, DUR)


if __name__ == '__main__':
    main()
