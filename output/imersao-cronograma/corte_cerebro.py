#!/usr/bin/env python3
"""Corte vertical da live da Imersão (youtu.be/7VVhSzlHfdI, 18:20-26:50):
o Itamar mostrando o cérebro da operação do Alberto (grafo do Obsidian na TV).

Layout 1080x1920: título no topo, grafo da TV em cima, Itamar embaixo (o
enquadramento segue o corpo pela pose do MediaPipe), legenda palavra a palavra.

Privacidade: depois do grafo a TV mostra arquivos .md com faturamento de 30 dias e
curva A em R$ da loja do Alberto. Nesses trechos o painel de cima usa o grafo
(escurecido, com cartão) e, no painel de baixo, a TV é desfocada atrás do Itamar
(máscara de pessoa do MediaPipe), então nenhum número da loja aparece.

Precisa de um Python com mediapipe (o python3 do sistema é 3.9 e não tem):
  python3.11 -m venv ~/venvs/mp && ~/venvs/mp/bin/pip install mediapipe
  modelo: storage.googleapis.com/mediapipe-models/pose_landmarker/
          pose_landmarker_full/float16/1/pose_landmarker_full.task  -> trab/cerebro-alberto/

  yt-dlp -f 232+140 --download-sections "*00:18:20-00:26:50" \
      -o trab/cerebro-alberto/bruto.mp4 https://youtu.be/7VVhSzlHfdI
  ~/venvs/mp/bin/python corte_cerebro.py      # -> videos/cerebro-alberto.mp4
"""
import json, os, re, subprocess, sys
import numpy as np, cv2

AQUI = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(AQUI, 'trab', 'cerebro-alberto')
BRUTO = os.path.join(TRAB, 'bruto.mp4')
MODELO = os.path.join(TRAB, 'pose_landmarker_full.task')
SAIDA = os.path.join(AQUI, 'videos', 'cerebro-alberto.mp4')
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
WHISPER = os.path.expanduser('~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin')

FPS, W, H = 30, 1080, 1920
SW, SH = 1280, 720                      # bruto
TOPO, SEAM = 320, 928                   # título 0-320 | grafo 320-928 | Itamar 928-1920
GRAFO = (566, 54, 600, 338)             # x, y, w, h da área do grafo na TV (sem a borda do dock)
TV = (412, 6, 1196, 452)                # tela da TV (x0, y0, x1, y1) no bruto
BH = 560                                # altura do recorte do Itamar no bruto
BW = round(BH * W / (H - SEAM) / 2) * 2
BY0 = 110
AMARELO_BGR = (94, 228, 255)            # #FFE45E

# Tempos no bruto (0 = 18:20 da live). topo: 'live' = a própria TV naquele instante;
# número = começa o grafo (B-roll) nesse tempo; 'seq' = continua o B-roll anterior.
TRECHOS = [
    dict(a=16.05, b=18.86, topo=56.0),    # o Alberto me autorizou a mostrar um negócio muito legal
    dict(a=22.24, b=29.62, topo='seq'),   # ele permitiu que eu conectasse na conta dele e gerasse o cérebro
    dict(a=137.43, b=140.20, topo='live'),  # ele, desde 2018, tá trabalhando no e-commerce
    dict(a=49.30, b=54.52, topo=108.0, trava=(50.90, 52.60)),  # quando eu vi o cérebro dele, travou. Bugou
    dict(a=69.72, b=73.42, topo='live'),  # a skill pega todas as lojas dele e todos os produtos
    dict(a=79.40, b=80.85, topo='live'),  # aí ele puxou tudo
    dict(a=82.24, b=87.50, topo='live'),  # se você pensar que é só uma animação, não é
    dict(a=90.76, b=97.10, topo='live'),  # cada item desse é uma coisa da loja dele; o canal da Shopee
    dict(a=102.57, b=107.62, topo='live'),  # olha como a IA enxerga as coisas
    dict(a=225.80, b=234.20, topo=111.0, cartao='md', xmax=4),  # ele gera um arquivo .md (selo da live inteiro)
    dict(a=235.10, b=238.45, topo='seq', cartao='md'),   # a IA vai gastar menos token
    dict(a=294.40, b=302.85, topo='seq', cartao='conta'),  # você exportou toda a sua conta pra um .md
    dict(a=497.65, b=501.86, topo=143.0),  # ele autorizou. Obrigado, viu, Alberto? Valeu mesmo
]

TITULO = ['A OPERAÇÃO INTEIRA DELE', 'VIROU UM CÉREBRO']
CARTELA = ['A IMERSÃO COMPLETA ESTÁ', 'DE GRAÇA NO YOUTUBE']
CARTELA_S = 3.6
FONTE = 'Avenir Next Condensed Heavy'
AMARELO, BRANCO, PRETO = '&H005EE4FF&', '&H00FFFFFF&', '&H00000000&'
CORRIGE = {'CLOUD': 'CLAUDE', 'MD': '.MD', 'SKILL': 'SKILL'}


def preparar():
    """Alinha os cortes ao quadro e calcula onde cada trecho entra no corte final."""
    off = 0
    for s in TRECHOS:
        s['fa'] = round(s['a'] * FPS)
        s['n'] = round(s['b'] * FPS) - s['fa']
        s['off'] = off
        off += s['n']
        s['tvlive'] = s['topo'] == 'live'
    return off


# ---------------------------------------------------------------- áudio e palavras
def audio(wav):
    f, xs = [], []
    for i, s in enumerate(TRECHOS):
        a, d = s['fa'] / FPS, s['n'] / FPS
        f.append('[0:a]atrim=%.4f:%.4f,asetpts=PTS-STARTPTS,afade=t=in:d=0.03,'
                 'afade=t=out:st=%.4f:d=0.04[a%d]' % (a, a + d, d - 0.04, i))
        xs.append('[a%d]' % i)
    f.append(''.join(xs) + 'concat=n=%d:v=0:a=1[a]' % len(xs))
    bruto = os.path.join(TRAB, 'audio_bruto.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-i', BRUTO, '-filter_complex', ';'.join(f), '-map', '[a]',
                    '-ar', '48000', '-ac', '2', bruto], check=True)
    m = subprocess.run([FF, '-hide_banner', '-i', bruto, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    ln = ('loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:'
          'offset=%s:linear=true' % (j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset']))
    subprocess.run([FF, '-v', 'error', '-y', '-i', bruto, '-af', ln, '-ar', '48000', wav], check=True)
    print('áudio: %s LUFS -> -14 (só ganho)' % j['input_i'])


def palavras(wav):
    w16 = os.path.join(TRAB, 'corte16k.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-i', wav, '-ar', '16000', '-ac', '1', w16], check=True)
    subprocess.run(['whisper-cli', '-m', WHISPER, '-l', 'pt', '-f', w16, '-ml', '1', '-sow', '-oj',
                    '-of', os.path.join(TRAB, 'palavras'), '-np'], check=True, capture_output=True)
    d = json.load(open(os.path.join(TRAB, 'palavras.json')))
    ws = []
    for s in d['transcription']:
        bruto = s['text'].strip()
        if not bruto:
            continue
        t = re.sub(r'[.,;:!…]+$', '', bruto).upper()
        t = CORRIGE.get(t, t)
        w = {'t': t, 'a': s['offsets']['from'] / 1000, 'b': s['offsets']['to'] / 1000,
             'fim': bool(re.search(r'[.?!…]$', bruto))}
        if ws and ws[-1]['t'] == 'PONTO' and t == '.MD':      # "ponto MD" -> ".MD"
            ws[-1].update(t='.MD', b=w['b'], fim=w['fim'])
            continue
        ws.append(w)
    for i in range(len(ws) - 2):                             # ele diz "e todos os produtos"
        if ws[i]['t'] == 'TROUXE' and ws[i + 1]['t'] == 'OS' and ws[i + 2]['t'] == 'PRODUTOS':
            ws[i]['t'] = 'TODOS'
    return ws


# ---------------------------------------------------------------- legenda (ASS)
def ts(s):
    s = max(0, s)
    return '%d:%02d:%05.2f' % (s // 3600, s % 3600 // 60, s % 60)


def acha(ws, palavra, depois):
    for w in ws:
        if w['a'] >= depois - 0.05 and w['t'].strip('?').startswith(palavra):
            return w['a']
    raise SystemExit('palavra não achada no corte: %s (depois de %.1f s)' % (palavra, depois))


def cartoes(ws):
    """Cartões dos trechos dos arquivos .md (a TV ali tem números da loja: não aparece)."""
    md = [s for s in TRECHOS if s.get('cartao') == 'md']
    conta = [s for s in TRECHOS if s.get('cartao') == 'conta']
    ini_md, fim_md = md[0]['off'] / FPS, (md[-1]['off'] + md[-1]['n']) / FPS
    ini_c, fim_c = conta[0]['off'] / FPS, (conta[-1]['off'] + conta[-1]['n']) / FPS
    linhas = [  # (estilo, texto, entra, sai, y)
        ('CardA', 'ARQUIVO .MD', acha(ws, 'ARQUIVO', ini_md), fim_md, 470),
        ('CardB', 'A IA ENTENDE MELHOR', acha(ws, 'ENTENDE', ini_md), fim_md, 590),
        ('CardB', 'EM VEZ DE {\\s1}PDF{\\s0}', acha(ws, 'PDF', ini_md), fim_md, 690),
        ('CardY', 'MENOS TOKEN', acha(ws, 'MENOS', ini_md), fim_md, 795),
        ('CardA', 'SUA CONTA INTEIRA', acha(ws, 'EXPORTOU', ini_c), fim_c, 500),
        ('CardB', 'VIROU ARQUIVO .MD', acha(ws, '.MD', ini_c), fim_c, 625),
        ('CardY', 'OS DADOS DO SEU LADO', acha(ws, 'DADOS', ini_c), fim_c, 745),
    ]
    L = []
    for est, txt, a, b, y in linhas:
        L.append('Dialogue: 3,%s,%s,%s,,0,0,0,,{\\an5\\pos(540,%d)\\fad(120,150)\\fscx60\\fscy60'
                 '\\t(0,160,\\fscx108\\fscy108)\\t(160,260,\\fscx100\\fscy100)}%s' % (ts(a), ts(b), est, y, txt))
    return L, [(ini_md, fim_md), (ini_c, fim_c)]


def legenda(ws, dur, ass):
    pags, cur = [], []
    for w in ws:
        if cur and (len(cur) >= 3 or sum(len(x['t']) + 1 for x in cur) + len(w['t']) > 16
                    or w['a'] - cur[-1]['b'] > 0.35 or cur[-1]['fim']):
            pags.append(cur)
            cur = []
        cur.append(w)
    if cur:
        pags.append(cur)
    L = []
    for k, p in enumerate(pags):
        prox = pags[k + 1][0]['a'] if k + 1 < len(pags) else dur
        fim_pag = min(p[-1]['b'] + 0.35, prox)
        for i, w in enumerate(p):
            fim = p[i + 1]['a'] if i + 1 < len(p) else fim_pag
            if fim - w['a'] < 0.02:
                continue
            partes = []
            for j, x in enumerate(p):
                if j < i:
                    partes.append(x['t'])
                elif j == i:
                    partes.append('{\\c%s\\fscx72\\fscy72\\t(0,90,\\fscx112\\fscy112)'
                                  '\\t(90,170,\\fscx100\\fscy100)}%s{\\r}' % (AMARELO, x['t']))
                else:
                    partes.append('{\\alpha&HFF&}%s' % x['t'])
            L.append('Dialogue: 1,%s,%s,Leg,,0,0,0,,{\\an5\\pos(540,1540)}%s' % (ts(w['a']), ts(fim), ' '.join(partes)))
    L.append('Dialogue: 2,%s,%s,Titulo,,0,0,0,,{\\an5\\pos(540,185)\\fscx60\\fscy60'
             '\\t(0,180,\\fscx106\\fscy106)\\t(180,280,\\fscx100\\fscy100)}%s' % (ts(0), ts(dur), '\\N'.join(TITULO)))
    card, janelas = cartoes(ws)
    L += card
    L.append('Dialogue: 3,%s,%s,Cartela,,0,0,0,,{\\an5\\pos(540,624)\\fad(200,0)\\fscx80\\fscy80'
             '\\t(0,200,\\fscx100\\fscy100)}%s' % (ts(dur - CARTELA_S), ts(dur), '\\N'.join(CARTELA)))
    cab = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,{F},112,{B},{B},{P},&H80000000&,1,0,0,0,100,100,1,0,1,7,3,5,60,60,0,1
Style: Titulo,{F},74,{P},{P},{A},&H00000000&,1,0,0,0,100,100,1,0,3,16,0,5,60,60,0,1
Style: Cartela,{F},84,{P},{P},{A},&H00000000&,1,0,0,0,100,100,1,0,3,18,0,5,60,60,0,1
Style: CardA,{F},104,{P},{P},{A},&H00000000&,1,0,0,0,100,100,1,0,3,16,0,5,60,60,0,1
Style: CardB,{F},80,{B},{B},{P},&H80000000&,1,0,0,0,100,100,1,0,1,6,3,5,60,60,0,1
Style: CardY,{F},80,{A},{A},{P},&H80000000&,1,0,0,0,100,100,1,0,1,6,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".replace('{F}', FONTE).replace('{B}', BRANCO).replace('{P}', PRETO).replace('{A}', AMARELO)
    open(ass, 'w').write(cab + '\n'.join(L) + '\n')
    return janelas


# ---------------------------------------------------------------- vídeo
def ler(t0, n, w=SW, h=SH, crop=None):
    cmd = [FF, '-v', 'error', '-ss', '%.4f' % t0, '-i', BRUTO, '-frames:v', str(n)]
    if crop:
        cmd += ['-vf', 'crop=%d:%d:%d:%d' % (crop[2], crop[3], crop[0], crop[1])]
    cmd += ['-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    tam = w * h * 3
    for _ in range(n):
        b = p.stdout.read(tam)
        if len(b) < tam:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.stdout.close()
    p.wait()


def suaviza(x, sigma):
    k = np.exp(-0.5 * (np.arange(-3 * sigma, 3 * sigma + 1) / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(x, 3 * sigma, mode='edge')
    return np.convolve(pad, k, mode='valid')


class Pose:
    def __init__(self):
        import mediapipe as mp
        from mediapipe.tasks import python as mpt
        from mediapipe.tasks.python import vision
        self.mp = mp
        self.det = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=mpt.BaseOptions(model_asset_path=MODELO), running_mode=vision.RunningMode.VIDEO,
            output_segmentation_masks=True, num_poses=1))
        self.ms = 0

    def __call__(self, img):
        self.ms += 34
        r = self.det.detect_for_video(self.mp.Image(image_format=self.mp.ImageFormat.SRGB,
                                                    data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), self.ms)
        if not r.pose_landmarks:
            return None, None
        lm = r.pose_landmarks[0]
        xs = [lm[k].x for k in (0, 11, 12) if lm[k].visibility > 0.5]
        cx = float(np.mean(xs)) * SW if xs else None
        m = r.segmentation_masks[0].numpy_view()[:, :, 0]
        return cx, cv2.resize(m, (SW // 2, SH // 2), interpolation=cv2.INTER_AREA)


def analisa(s, pose):
    """Centro do Itamar (suavizado) e máscara de pessoa de cada quadro do trecho."""
    cxs, masks = [], []
    for img in ler(s['fa'] / FPS, s['n']):
        cx, m = pose(img)
        if cx is None and m is not None and m.sum() > 50:
            cx = float((m.sum(0) * np.arange(m.shape[1])).sum() / m.sum()) * 2
        cxs.append(cx)
        masks.append(m)
    ult = next((c for c in cxs if c is not None), 420.0)
    for i, c in enumerate(cxs):
        cxs[i] = ult = c if c is not None else ult
    for i, m in enumerate(masks):              # sem máscara: usa a do quadro vizinho
        if m is None:
            masks[i] = next((masks[j] for j in range(i - 1, -1, -1) if masks[j] is not None),
                            np.zeros((SH // 2, SW // 2), np.float32))
    cx = suaviza(np.array(cxs), 18)
    x0 = np.clip(np.round(cx - BW / 2), 0, min(SW - BW, s.get('xmax', SW))).astype(int)
    return x0, masks


TVX0, TVY0, TVX1, TVY1 = TV
_r = np.zeros((TVY1 - TVY0, TVX1 - TVX0), np.float32)
_r[6:-6, 6:-6] = 1
TV_ALFA = cv2.GaussianBlur(_r, (0, 0), 3)


def esconde_tv(img, m):
    """Desfoca a tela da TV, menos onde está o Itamar (máscara de pessoa encolhida)."""
    img = img.copy()
    reg = img[TVY0:TVY1, TVX0:TVX1].astype(np.float32)
    h, w = reg.shape[:2]
    borr = cv2.resize(cv2.resize(reg, (w // 14, h // 14), interpolation=cv2.INTER_AREA), (w, h),
                      interpolation=cv2.INTER_LINEAR)
    borr = cv2.GaussianBlur(borr, (0, 0), 5) * 0.8
    pm = cv2.resize(m, (SW, SH), interpolation=cv2.INTER_LINEAR)
    pm = cv2.erode((pm > 0.5).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(np.float32)
    pm = cv2.GaussianBlur(pm, (0, 0), 2)[TVY0:TVY1, TVX0:TVX1]
    a = (TV_ALFA * (1 - pm))[:, :, None]
    img[TVY0:TVY1, TVX0:TVX1] = np.clip(reg * (1 - a) + borr * a, 0, 255).astype(np.uint8)
    return img


def topo_quadro(cr, l, dur, escuro):
    gh, gw = cr.shape[:2]
    z = 1 + 0.05 * l / max(dur, 0.1)
    w, h = gw / z, gh / z
    x, y = (gw - w) / 2, (gh - h) / 2
    M = np.float32([[W / w, 0, -x * W / w], [0, (SEAM - TOPO) / h, -y * (SEAM - TOPO) / h]])
    out = cv2.warpAffine(cr, M, (W, SEAM - TOPO), flags=cv2.INTER_CUBIC)
    if escuro:
        out = (cv2.GaussianBlur(out, (0, 0), 2) * 0.42).astype(np.uint8)
    return out


def glitch(img, i):
    rng = np.random.default_rng(1000 + i)
    dx = int(rng.integers(5, 18))
    b, g, r = cv2.split(img)
    out = cv2.merge([np.roll(b, -dx, 1), g, np.roll(r, dx, 1)])
    for _ in range(int(rng.integers(2, 6))):
        y = int(rng.integers(0, out.shape[0] - 40))
        hh = int(rng.integers(8, 44))
        out[y:y + hh] = np.roll(out[y:y + hh], int(rng.integers(-70, 70)), 1)
    sx, sy = rng.integers(-8, 9, 2)
    return np.roll(np.roll(out, int(sx), 1), int(sy), 0)


def baixo_quadro(img, x0):
    cr = img[BY0:BY0 + BH, x0:x0 + BW]
    out = cv2.resize(cr, (W, H - SEAM), interpolation=cv2.INTER_LANCZOS4)
    return cv2.addWeighted(out, 1.35, cv2.GaussianBlur(out, (0, 0), 2.2), -0.35, 0)


def render(total, janelas, ass, wav):
    pose = Pose()
    fundo = np.zeros((H, W, 3), np.uint8)
    fundo[:] = (20, 12, 10)
    enc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H),
                            '-r', str(FPS), '-i', '-', '-i', wav, '-vf', 'ass=' + ass, '-map', '0:v', '-map', '1:a',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', SAIDA],
                           stdin=subprocess.PIPE)
    dur = total / FPS
    cursor = None
    for k, s in enumerate(TRECHOS):
        x0s, masks = analisa(s, pose)
        n = s['n']
        f0 = f1 = n
        if s.get('trava'):
            f0 = round((s['trava'][0] - s['fa'] / FPS) * FPS)
            f1 = round((s['trava'][1] - s['fa'] / FPS) * FPS)
        idx = [i if i < f0 else (f0 if i < f1 else i - (f1 - f0)) for i in range(n)]
        if s['topo'] == 'live':
            t_topo = s['fa'] / FPS
        else:
            t_topo = cursor if s['topo'] == 'seq' else s['topo']
            cursor = t_topo + (max(idx) + 1) / FPS
        topos = list(ler(t_topo, max(idx) + 1, GRAFO[2], GRAFO[3], GRAFO))
        for i, img in enumerate(ler(s['fa'] / FPS, n)):
            t = (s['off'] + i) / FPS
            if not s['tvlive']:
                img = esconde_tv(img, masks[i])
            escuro = any(a <= t < b for a, b in janelas) or t >= dur - CARTELA_S
            top = topo_quadro(topos[min(idx[i], len(topos) - 1)], i / FPS, n / FPS, escuro)
            if f0 <= i < f1:
                top = glitch(top, i)
            c = fundo.copy()
            c[TOPO:SEAM] = top
            c[SEAM:] = baixo_quadro(img, x0s[i])
            c[SEAM - 3:SEAM + 3] = AMARELO_BGR
            enc.stdin.write(c.tobytes())
        print('trecho %2d: %5.2f-%6.2f  %3d quadros  topo=%s' % (k + 1, s['a'], s['b'], n, s['topo']), flush=True)
    enc.stdin.close()
    enc.wait()


def main():
    total = preparar()
    wav = os.path.join(TRAB, 'audio.wav')
    audio(wav)
    ws = palavras(wav)
    print(' '.join(w['t'] for w in ws))
    ass = os.path.join(TRAB, 'legenda.ass')
    janelas = legenda(ws, total / FPS, ass)
    if 'texto' in sys.argv:
        return
    render(total, janelas, ass, wav)
    print('%s: %.1f s' % (SAIDA, total / FPS))


if __name__ == '__main__':
    main()
