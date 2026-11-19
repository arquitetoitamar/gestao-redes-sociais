"""Edição do vídeo MoreLogin (gravação do Google Vids, 1920x1080, tela + câmera).

O que faz, no tempo do BRUTO:
  1. cortes: tropeços de fala (CORTES) e pausas > 0,35 s encurtadas para 0,24 s
  2. desfoque leve só onde há dado de conta (OCR: trab/ocr_hits.json + trab/ocr3_hits.json)
  3. tela em tela cheia (tira a moldura cinza do Vids) + zoom editorial (ZOOMS) com transição suave
  4. câmera em círculo no canto inferior direito
  5. motions (trab/mot/<peça>, renderizados por motions.py) nos tempos de plano_motions.json
Áudio original, sem tratamento (só emendas com fade de 8 ms).

uso: python3 monta.py edl          -> trab/edl.json (e mostra a duração final)
     python3 monta.py parte <i> <n> -> trab/parte_<i>.mp4  (renderiza a fatia i de n)
     python3 monta.py audio        -> trab/audio_final.wav
     python3 monta.py junta <n>    -> morelogin_final.mp4
"""
import glob, json, os, re, subprocess, sys, wave
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
T = lambda *p: os.path.join(AQUI, 'trab', *p)
BRUTO = T('bruto.mp4')
W, H, FPS = 1920, 1080, 30
TELA = (62, 74, 1652, 968)                     # região da tela no bruto (16:9)
CAM = (1615, 777, 1870, 1032)                  # bolha da câmera no bruto
CAM_SAIDA = 300                                # diâmetro da câmera no vídeo final
CAM_POS = (W - CAM_SAIDA - 34, H - CAM_SAIDA - 30)

INICIO, FIM = 4.30, 1586.40
# tropeços de fala (início, fim) no bruto — ver trab/leitura.txt
CORTES = [
    (285.60, 286.80),    # "o cloud. o cloud." repetido
    (783.76, 793.36),    # "deixa eu fechar aqui essa pasta, que eu vou ocultar aqui"
    (815.22, 816.88),    # "o CLI é,"
    (887.15, 891.50),    # "eu coloquei, só um minuto, eu coloquei"
    (952.20, 954.40),    # "então aqui você pode,"
    (1021.00, 1022.55),  # "para que não dê," repetido
    (1067.90, 1077.20),  # procurando o WhatsApp Web
    (1135.10, 1139.78),  # "tente novamente mais tarde... já estava fechado aqui"
    (1162.70, 1192.65),  # dúvida sobre perfil grátis (a oferta certa entra no CTA)
    (1569.55, 1571.85),  # "como de tudo,"
]
PAUSA_MIN, PAUSA_FICA = 0.30, 0.22

ZOOMS = [  # (início, fim, retângulo no bruto) — editorial, conferido em trab/zooms_*.jpg e trab/grade.jpg
    (117.0, 125.0, (792, 74, 1652, 558)),     # botão do chat da Shopee
    (478.0, 521.0, (430, 170, 1290, 654)),    # página do IP do perfil
    (540.0, 592.0, (360, 190, 1350, 747)),    # site do MoreLogin
    (612.0, 660.0, (180, 150, 1100, 668)),    # criação do perfil
    (662.0, 716.0, (180, 170, 1180, 733)),    # lista de perfis
    (758.0, 783.5, (520, 230, 1380, 714)),    # agente de IA
    (800.0, 918.0, (357, 140, 1607, 843)),    # janela do Claude
    (927.0, 1001.0, (357, 140, 1607, 843)),
    (1002.0, 1068.0, (402, 160, 1652, 863)),
    (1081.0, 1129.0, (402, 160, 1652, 863)),
    (1236.0, 1275.0, (262, 175, 1302, 760)),  # modelos de automação
    (1329.0, 1349.0, (792, 150, 1652, 634)),  # assistente de IA
    (1392.0, 1418.0, (380, 280, 1340, 820)),  # proxy
    (1505.0, 1530.0, (180, 150, 1100, 668)),  # centro de criação
    (1563.0, 1586.0, (402, 160, 1652, 863)),  # Claude no fim
]
TRANS = 0.7

SENS = re.compile(r'isantos|keiprod|kei\s?prod|ads\s?team|\b1\d\d\.1\d\d\.\d{1,3}\.\d{1,3}\b|[\w.]+@[\w-]+\.\w+|gmail', re.I)


# ---------------------------------------------------------------- linha do tempo
def pausas():
    t = open(T('silencios035.txt')).read()
    ini = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', t)]
    fim = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', t)]
    return list(zip(ini, fim))


def edl():
    tirar = list(CORTES)
    for a, b in pausas():
        if b - a > PAUSA_MIN:
            m = (PAUSA_FICA / 2)
            tirar.append((a + m, b - m))
    tirar.sort()
    segs, cur = [], INICIO
    for a, b in tirar:
        if b <= cur or a >= FIM:
            continue
        if a > cur:
            segs.append([cur, a])
        cur = max(cur, b)
    if cur < FIM:
        segs.append([cur, FIM])
    # quadros inteiros
    out, t_out = [], 0
    for a, b in segs:
        fa, fb = round(a * FPS), round(b * FPS)
        if fb - fa < 4:
            continue
        out.append({'fa': fa, 'fb': fb, 'oa': t_out})
        t_out += fb - fa
    return out


def src_para_out(edl_, t):
    f = t * FPS
    for s in edl_:
        if f < s['fa']:
            return s['oa'] / FPS
        if f < s['fb']:
            return (s['oa'] + f - s['fa']) / FPS
    return edl_[-1]['oa'] / FPS + (edl_[-1]['fb'] - edl_[-1]['fa']) / FPS


# ---------------------------------------------------------------- desfoque
def caixas_sensiveis():
    hits = []
    for nome, meia in (('ocr_hits.json', 0.55), ('ocr3_hits.json', 0.22), ('ocr_saida_hits.json', 0.2), ('ocr_saida30_hits.json', 0.5), ('ocr_manual_hits.json', 0.25)):
        if os.path.exists(T(nome)):
            for h in json.load(open(T(nome))):
                pv = h['palavra']
                if re.search(r'\b20\d\d-\d\d-\d\d|\d\d-\d\d-20\d\d|^154\.0\.', pv):   # datas e versão: não é dado de conta
                    continue
                if (nome != 'ocr_hits.json' or SENS.search(pv)) and not pv.startswith('http://127'):
                    c = list(h['caixa'])
                    if c[0] > 1480 and 165 < c[1] < 220:      # nome da loja no topo da Shopee: leva junto o avatar
                        c[0] -= 50
                    hits.append((h['t'], meia, c, h['palavra']))
    hits.sort()
    # preenche buracos: mesma caixa (aprox.) vista de novo em até 3 s
    def iou(a, b):
        ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
        i = ix * iy
        return i / max(1, (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i)
    spans = []
    for t, meia, c, _ in hits:
        for s in spans[::-1][:60]:
            if t - s[1] <= 3.0 and iou(s[2], c) > 0.3:
                s[1] = max(s[1], t + meia)
                break
        else:
            spans.append([t - meia, t + meia, c])
    return spans


# dado fixo achado por modelo (template), quadro a quadro: (segundo de onde tirar o modelo, recorte, área de busca, janela)
MODELOS = [
    (760.0, (1508, 138, 1630, 158), (1380, 110, 1652, 200), None),         # "isantos.ads team" no topo do MoreLogin
    (485.0, (762, 263, 956, 291), (560, 100, 1400, 920), (470.0, 527.0)),  # IP do perfil
    (35.6, (1262, 176, 1349, 196), (1100, 150, 1652, 240), None),          # avatar + nome da loja no topo da Shopee
    (363.4, (440, 396, 510, 466), (360, 150, 620, 900), None),             # logo da loja (KEI) no perfil da Shopee
]
_mod = None


def modelos():
    global _mod
    if _mod is None:
        _mod = []
        for t, r, busca, jan in MODELOS:
            out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', BRUTO, '-frames:v', '1', '-f', 'rawvideo',
                                  '-pix_fmt', 'gray', '-'], capture_output=True).stdout
            g = np.frombuffer(out, np.uint8).reshape(H, W)
            _mod.append((g[r[1]:r[3], r[0]:r[2]].copy(), busca, jan))
    return _mod


def caixas_modelo(src, ts):
    cx = []
    g = None
    for tpl, (bx0, by0, bx1, by1), jan in modelos():
        if jan and not (jan[0] <= ts < jan[1]):
            continue
        if g is None:
            g = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        area = g[by0:by1, bx0:bx1]
        escalas = (1.0,) if jan is None else (1.0, 0.9, 0.8, 0.72, 0.64)
        melhor = (0, None)
        for e in escalas:
            t = tpl if e == 1.0 else cv2.resize(tpl, None, fx=e, fy=e, interpolation=cv2.INTER_AREA)
            for parte in ((t, 0),) if jan is None else ((t, 0), (t[t.shape[0] // 2:], t.shape[0] // 2)):
                pt, dy = parte
                if pt.shape[0] > area.shape[0] or pt.shape[1] > area.shape[1]:
                    continue
                res = cv2.matchTemplate(area, pt, cv2.TM_CCOEFF_NORMED)
                _, mx, _, (x, y) = cv2.minMaxLoc(res)
                if mx > melhor[0]:
                    melhor = (mx, [bx0 + x, by0 + y - dy, bx0 + x + t.shape[1], by0 + y - dy + t.shape[0]])
        if melhor[0] > 0.6:
            cx.append(melhor[1])
    return cx


def desfoca(q, caixas):
    for x0, y0, x1, y1 in caixas:
        x0, y0, x1, y1 = max(0, x0 - 10), max(0, y0 - 6), min(W, x1 + 10), min(H, y1 + 6)
        roi = q[y0:y1, x0:x1]
        if roi.size == 0:
            continue
        h, w = roi.shape[:2]
        pe = cv2.resize(roi, (max(1, w // 14), max(1, h // 14)), interpolation=cv2.INTER_AREA)
        bl = cv2.GaussianBlur(cv2.resize(pe, (w, h), interpolation=cv2.INTER_LINEAR), (0, 0), 5)
        # borda suave: não vira um bloco duro na tela
        m = np.zeros((h, w), np.float32)
        cv2.rectangle(m, (3, 3), (w - 4, h - 4), 1.0, -1)
        m = cv2.GaussianBlur(m, (0, 0), 2.5)[..., None]
        q[y0:y1, x0:x1] = (bl * m + roi * (1 - m)).astype(np.uint8)
    return q


# ---------------------------------------------------------------- zoom
def ease(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def plano_zoom(edl_):
    """Lista de (t_out, rect) com chaves; entre chaves interpola em TRANS segundos."""
    cheio = TELA
    ch = []
    for a, b, r in ZOOMS:
        ch.append((src_para_out(edl_, a), src_para_out(edl_, b), r))
    return ch


def rect_em(ch, t):
    atual = TELA
    for i, (a, b, r) in enumerate(ch):
        if t < a - TRANS:
            break
        if a - TRANS <= t < a:                          # entrando
            prev = ch[i - 1][2] if i and ch[i - 1][1] >= a - TRANS - 0.05 else TELA
            k = ease((t - (a - TRANS)) / TRANS)
            return tuple(p + (n - p) * k for p, n in zip(prev, r))
        if a <= t < b:
            nxt = ch[i + 1] if i + 1 < len(ch) else None
            if nxt and nxt[0] - TRANS <= b + 0.05:      # emenda direto no próximo zoom
                return r
            if t >= b - TRANS:                          # saindo
                k = ease((t - (b - TRANS)) / TRANS)
                return tuple(p + (n - p) * k for p, n in zip(r, TELA))
            return r
    return atual


def reenquadra(q, r):
    x0, y0, x1, y1 = r
    # câmera invade o canto inferior direito da tela: completa com a coluna vizinha
    q[CAM[1]:TELA[3], CAM[0] - 3:TELA[2]] = q[CAM[1]:TELA[3], CAM[0] - 4:CAM[0] - 3]
    M = np.float32([[W / (x1 - x0), 0, -x0 * W / (x1 - x0)], [0, H / (y1 - y0), -y0 * H / (y1 - y0)]])
    out = cv2.warpAffine(q, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    z = W / (x1 - x0)
    if z > 1.3:                                         # zoom forte: devolve um pouco de nitidez
        bl = cv2.GaussianBlur(out, (0, 0), 1.1)
        out = cv2.addWeighted(out, 1.35, bl, -0.35, 0)
    return out


# ---------------------------------------------------------------- câmera e motions
_mask = None


def camera(dst, src):
    global _mask
    d = CAM_SAIDA
    c = src[CAM[1] + 6:CAM[3] - 6, CAM[0] + 6:CAM[2] - 6]
    c = cv2.resize(c, (d, d), interpolation=cv2.INTER_CUBIC)
    if _mask is None:
        m = np.zeros((d + 24, d + 24), np.float32)
        cv2.circle(m, ((d + 24) // 2, (d + 24) // 2), d // 2, 1.0, -1, cv2.LINE_AA)
        _mask = m
    x, y = CAM_POS
    reg = dst[y - 12:y + d + 12, x - 12:x + d + 12].astype(np.float32)
    # sombra
    sh = cv2.GaussianBlur(_mask, (0, 0), 9)[..., None] * 0.35
    reg = reg * (1 - sh)
    # anel em degradê (magenta -> azul)
    ring = np.zeros((d + 24, d + 24), np.float32)
    cv2.circle(ring, ((d + 24) // 2, (d + 24) // 2), d // 2 + 6, 1.0, -1, cv2.LINE_AA)
    gx = np.linspace(0, 1, d + 24, dtype=np.float32)[None, :, None]
    cor = (1 - gx) * np.float32([255, 0, 228]) + gx * np.float32([255, 51, 36])  # BGR: magenta -> azul
    reg = reg * (1 - ring[..., None]) + cor * ring[..., None]
    cc = np.zeros_like(reg)
    cc[12:12 + d, 12:12 + d] = c
    m = _mask[..., None]
    reg = reg * (1 - m) + cc * m
    dst[y - 12:y + d + 12, x - 12:x + d + 12] = reg.astype(np.uint8)
    return dst


class Motion:
    def __init__(self, nome, t0):
        self.pasta = T('mot', nome)
        self.n = len(glob.glob(os.path.join(self.pasta, 'f_*.png')))
        self.t0 = t0
        pos = json.load(open(os.path.join(self.pasta, 'pos.json')))
        self.x, self.y = pos['x'], pos['y']
        self.segura = nome == 'final'
        self.cheia = nome in ('intro', 'final')
        self._i, self._im = -1, None

    def ativo(self, t):
        return self.t0 <= t < self.t0 + (10 ** 6 if self.segura else self.n / FPS)

    def aplica(self, dst, t):
        i = min(self.n - 1, int((t - self.t0) * FPS))
        if i != self._i:
            im = cv2.imread(os.path.join(self.pasta, 'f_%05d.png' % i), cv2.IMREAD_UNCHANGED)
            if im.shape[2] == 3:
                im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
            self._i, self._im = i, im
        im = self._im
        h, w = im.shape[:2]
        reg = dst[self.y:self.y + h, self.x:self.x + w].astype(np.float32)
        a = im[..., 3:4].astype(np.float32) / 255
        dst[self.y:self.y + h, self.x:self.x + w] = (im[..., :3] * a + reg * (1 - a)).astype(np.uint8)
        return dst


def motions(edl_):
    p = json.load(open(os.path.join(AQUI, 'plano_motions.json')))
    lista = [Motion('intro', 0.0), Motion('nome', src_para_out(edl_, p['nome'])),
             Motion('final', src_para_out(edl_, p['final']))]
    for c in p['capitulos']:
        lista.append(Motion('cap%d' % c['num'], src_para_out(edl_, c['src'])))
    for d in p['destaques']:
        lista.append(Motion('dest_' + d['id'], src_para_out(edl_, d['src'])))
    for t in p['cta']:
        lista.append(Motion('cta', src_para_out(edl_, t)))
    return lista


# ---------------------------------------------------------------- render
def parte(i, n):
    e = json.load(open(T('edl.json')))
    tot = e[-1]['oa'] + e[-1]['fb'] - e[-1]['fa']
    o0, o1 = tot * i // n, tot * (i + 1) // n          # quadros de saída desta fatia
    segs = [s for s in e if s['oa'] + s['fb'] - s['fa'] > o0 and s['oa'] < o1]
    spans = caixas_sensiveis()
    ch = plano_zoom(e)
    mots = motions(e)
    f_ini = segs[0]['fa'] + max(0, o0 - segs[0]['oa'])
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', '%.4f' % (f_ini / FPS), '-i', BRUTO, '-f', 'rawvideo',
                            '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    saida = T('parte_%d.mp4' % i)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                            '-pix_fmt', 'yuv420p', '-g', '60', saida], stdin=subprocess.PIPE)
    tam = W * H * 3
    f = f_ini
    feitos = 0
    for s in segs:
        a = max(s['fa'], s['fa'] + o0 - s['oa'])
        b = min(s['fb'], s['fa'] + o1 - s['oa'])
        while f < a:                                    # pula o que foi cortado
            dec.stdout.read(tam); f += 1
        while f < b:
            buf = dec.stdout.read(tam)
            if len(buf) < tam:
                break
            src = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
            ts = f / FPS
            to = (s['oa'] + f - s['fa']) / FPS
            cx = [c for a_, b_, c in spans if a_ <= ts < b_] + caixas_modelo(src, ts)
            if cx:
                src = desfoca(src, cx)
            q = reenquadra(src.copy(), rect_em(ch, to))
            ativos = [m for m in mots if m.ativo(to)]
            for m in ativos:
                if m.cheia:
                    q = m.aplica(q, to)
            q = camera(q, src)
            for m in ativos:
                if not m.cheia:
                    q = m.aplica(q, to)
            enc.stdin.write(q.tobytes())
            f += 1
            feitos += 1
            if feitos % 1500 == 0:
                print('parte', i, feitos, flush=True)
    dec.kill()
    enc.stdin.close()
    enc.wait()
    print('parte', i, 'quadros', feitos, 'esperado', o1 - o0)


def audio():
    e = json.load(open(T('edl.json')))
    with wave.open(T('audio48.wav')) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    fade = int(0.008 * sr)
    rampa = np.linspace(0, 1, fade, dtype=np.float32)
    pedacos = []
    for s in e:
        a, b = s['fa'] * sr // FPS, s['fb'] * sr // FPS
        p = x[a:b].copy()
        p[:fade] *= rampa
        p[-fade:] *= rampa[::-1]
        pedacos.append(p)
    y = np.concatenate(pedacos)
    with wave.open(T('audio_final.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes())
    print('áudio', round(len(y) / sr, 2), 's')


def junta(n):
    lst = T('partes.txt')
    open(lst, 'w').write(''.join("file '%s'\n" % T('parte_%d.mp4' % i) for i in range(n)))
    saida = os.path.join(AQUI, 'morelogin_final.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', T('audio_final.wav'),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                    '-movflags', '+faststart', saida], check=True)
    print(saida)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'edl':
        e = edl()
        json.dump(e, open(T('edl.json'), 'w'))
        tot = (e[-1]['oa'] + e[-1]['fb'] - e[-1]['fa']) / FPS
        print('segmentos', len(e), '| duração final %.1f s (%d:%02d)' % (tot, tot // 60, tot % 60))
    elif cmd == 'parte':
        parte(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == 'audio':
        audio()
    elif cmd == 'junta':
        junta(int(sys.argv[2]))
