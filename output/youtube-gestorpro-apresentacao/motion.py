"""Animações sobre o tutorial acelerado (work/tut_fast.mov, 1920x1080@30):
- zoom automático de câmera nos destaques laranja da tela
- cartão animado de capítulo (tipografia pesada) no silêncio antes de cada capítulo
- barra de progresso com marcas de capítulo e selo "conta demonstração"
uso: python3 motion.py detect | still t1,t2.. | render"""
import json, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "work", "tut_fast.mov")
W, H, FPS = 1920, 1080, 30
FONT = "/Users/itamar/git/gestao-redes-sociais/output/reel-explica-marketplace-connect/assets/Inter.ttf"
YEL = (245, 196, 0); INK = (11, 11, 12); AMB = (168, 120, 10)

# início da fala de cada capítulo no tempo acelerado: (t_srt - 2.0) / 1.1
CH = [
    (1.726, "O que é o GestorPro", "GESTORPRO."),
    (27.908, "O time de agentes", "O TIME DE AGENTES."),
    (55.683, "Sala de comando", "SALA DE COMANDO."),
    (82.738, "Vendas e margem", "VENDAS E MARGEM."),
    (105.755, "Custos e regras", "CUSTOS E REGRAS."),
    (128.272, "Saúde da loja", "SAÚDE DA LOJA."),
    (142.062, "Promoções", "PROMOÇÕES."),
    (169.290, "Perguntas", "PERGUNTAS."),
    (184.934, "Pós-venda", "PÓS-VENDA."),
    (198.811, "Atividade e relatórios", "ATIVIDADE E RELATÓRIOS."),
    (219.407, "Como começar", "COMO COMEÇAR."),
]
CARD = 1.0          # duração do cartão (s), termina 0.05 s antes da fala
OPEN = 1.6          # cartão de abertura

def cards():
    out = []
    for i, (t, _, word) in enumerate(CH):
        if i == 0: out.append((0.0, OPEN, i, word))
        else: out.append((t - CARD - 0.05, CARD, i, word))
    return out

# ---------------------------------------------------------------- tipografia
def font(size, wght=900):
    f = ImageFont.truetype(FONT, int(size))
    try:
        axes = f.get_variation_axes()
        vals = []
        for a in axes:
            nm = a.get("name", b"")
            nm = nm.decode() if isinstance(nm, bytes) else str(nm)
            vals.append(wght if "eight" in nm.lower() else a["maximum"] if "ptical" in nm.lower() else a["default"])
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f

def text_img(txt, size, fill, track=-0.05, wght=900):
    f = font(size, wght)
    xs, x = [], 0.0
    for ch in txt:
        xs.append(x); x += f.getlength(ch) + track * size
    w = int(x - track * size) + 40; h = int(size * 1.25) + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for ch, cx in zip(txt, xs):
        d.text((20 + cx, 10), ch, font=f, fill=fill)
    bb = im.getbbox()
    return im.crop((bb[0] - 4, 0, bb[2] + 4, h)) if bb else im

def fit_word(word, color, maxw=1640, size=230):
    im = text_img(word, size, color)
    if im.width <= maxw: return [im]
    if im.width * 0.62 <= maxw or " " not in word:
        s = size * maxw / im.width
        if s >= 150 or " " not in word: return [text_img(word, s, color)]
    # duas linhas
    ws = word.split(" "); best = None
    for k in range(1, len(ws)):
        a, b = " ".join(ws[:k]), " ".join(ws[k:])
        m = max(len(a), len(b))
        if best is None or m < best[0]: best = (m, a, b)
    a, b = best[1], best[2]
    ia, ib = text_img(a, size, color), text_img(b, size, color)
    s = min(1.0, maxw / max(ia.width, ib.width))
    return [text_img(a, size * s, color), text_img(b, size * s, color)]

def pill(txt, size, bg, fg, padx=30, pady=16, wght=800, track=0.0):
    t = text_img(txt, size, fg, track=track, wght=wght)
    w, h = t.width + 2 * padx, int(size * 1.1) + 2 * pady
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg)
    im.alpha_composite(t, (padx, (h - t.height) // 2 + 2))
    return im

def build_card_layers():
    """por cartão: fundo (RGB), camada do texto grande (RGBA) e camada fixa (RGBA)"""
    L = []
    for (t0, d, i, word) in cards():
        dark = (i % 2 == 0)
        bg = np.zeros((H, W, 3), np.uint8)
        if dark:
            yy, xx = np.mgrid[0:H, 0:W]
            r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.55) / H) ** 2)
            g = np.clip(1 - r * 1.6, 0, 1)[..., None]
            bg[:] = (np.array([11, 11, 12]) + g * np.array([16, 14, 4])).astype(np.uint8)
        else:
            bg[:] = YEL
        fg = (255, 255, 255, 255) if dark else INK + (255,)
        lines = fit_word(word, fg)
        big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tot = sum(l.height for l in lines) - 30 * (len(lines) - 1)
        y = (H - tot) // 2 + 10
        for l in lines:
            big.alpha_composite(l, ((W - l.width) // 2, y)); y += l.height - 30
        fix = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(fix)
        hc = (255, 255, 255, 115) if dark else (0, 0, 0, 140)
        hf = font(26, 700)
        dd.ellipse((80, 72, 96, 88), fill=YEL + (255,) if dark else INK + (255,))
        dd.text((112, 66), "GESTORPRO  ·  ESCRITÓRIO DE AGENTES", font=hf, fill=hc)
        num = f"{i + 1:02d} / {len(CH):02d}"
        dd.text((W - 80 - hf.getlength(num), 66), num, font=hf, fill=hc)
        lab = ("APRESENTAÇÃO · PARTE 1" if i == 0 else f"CAPÍTULO {i + 1:02d}")
        lt = text_img(lab, 34, (YEL + (255,)) if dark else (INK + (200,)), track=0.18, wght=800)
        top_of_word = (H - tot) // 2 + 10
        fix.alpha_composite(lt, ((W - lt.width) // 2, top_of_word - 70))
        if i == 0:
            p = pill("Escritório de agentes de IA para marketplaces", 40, YEL + (255,), INK + (255,))
            fix.alpha_composite(p, ((W - p.width) // 2, top_of_word + tot + 40))
        L.append({"t0": t0, "d": d, "bg": bg, "big": big, "fix": fix})
    return L

# ---------------------------------------------------------------- detecção dos destaques
def detect():
    cap = cv2.VideoCapture(SRC); res = []; f = 0
    while True:
        ok, fr = cap.read()
        if not ok: break
        if f % 2 == 0:
            sm = cv2.resize(fr, (W // 2, H // 2), interpolation=cv2.INTER_AREA).astype(np.int16)
            b, g, r = sm[..., 0], sm[..., 1], sm[..., 2]
            m = ((r > 200) & (g > 60) & (g < 150) & (b < 110) & (r - g > 80)).astype(np.uint8)
            n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
            best = None
            for k in range(1, n):
                x, y, w, h, a = st[k]
                if w > 25 and h > 12 and a / (w * h) < 0.22:
                    if best is None or w * h > best[2] * best[3]: best = (x, y, w, h)
            res.append([f] + ([int(v * 2) for v in best] if best else []))
        f += 1
    json.dump({"n": f, "boxes": res}, open(os.path.join(HERE, "work", "boxes.json"), "w"))
    print("frames", f, "com destaque", sum(1 for r in res if len(r) > 1))

def camera_path(n):
    """zoom e centro por quadro, suavizados (mola amortecida)"""
    D = json.load(open(os.path.join(HERE, "work", "boxes.json")))
    box = [None] * n
    for r in D["boxes"]:
        if len(r) > 1:
            for k in (r[0], r[0] + 1):
                if k < n: box[k] = r[1:]
    # preenche buracos curtos (< 0.6 s) com o último destaque
    last, gap = None, 0
    for k in range(n):
        if box[k] is not None: last, gap = box[k], 0
        else:
            gap += 1
            if last is not None and gap < 18: box[k] = last
    # sem zoom durante os cartões
    for (t0, d, _, _) in cards():
        for k in range(int(t0 * FPS), min(n, int((t0 + d) * FPS) + 1)): box[k] = None
    tz, tx, ty = np.ones(n), np.full(n, W / 2), np.full(n, H / 2)
    for k in range(n):
        if box[k] is None: continue
        x, y, w, h = box[k]
        z = min(0.60 * W / max(w, 1), 0.60 * H / max(h, 1), 1.6)
        z = max(1.0, z)
        if z < 1.12: continue
        tz[k] = z; tx[k] = x + w / 2; ty[k] = y + h / 2
    # mola crítica
    z, x, y, vz, vx, vy = 1.0, W / 2, H / 2, 0, 0, 0
    om = 2 * math.pi / 1.1; dt = 1 / FPS
    Z, X, Y = np.zeros(n), np.zeros(n), np.zeros(n)
    for k in range(n):
        for (p, v, tgt) in ((0, 0, 0),):
            pass
        az = om * om * (tz[k] - z) - 2 * om * vz; vz += az * dt; z += vz * dt
        ax = om * om * (tx[k] - x) - 2 * om * vx; vx += ax * dt; x += vx * dt
        ay = om * om * (ty[k] - y) - 2 * om * vy; vy += ay * dt; y += vy * dt
        Z[k], X[k], Y[k] = z, x, y
    return Z, X, Y

def apply_cam(fr, z, cx, cy):
    if z < 1.003: return fr
    vw, vh = W / z, H / z
    cx = min(max(cx, vw / 2), W - vw / 2); cy = min(max(cy, vh / 2), H - vh / 2)
    M = np.float32([[z, 0, W / 2 - z * cx], [0, z, H / 2 - z * cy]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# ---------------------------------------------------------------- composição
def over(dst, rgba, alpha=1.0, scale=1.0, blur=0.0, dy=0):
    """cola camada RGBA (tamanho W x H) sobre dst com escala/desfoque pelo centro"""
    a = rgba
    if scale != 1.0:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, scale); M[1, 2] += dy
        a = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
    elif dy:
        a = np.roll(a, int(dy), axis=0)
    if blur > 0.5: a = cv2.GaussianBlur(a, (0, 0), blur)
    al = a[..., 3:4].astype(np.float32) / 255 * alpha
    dst[:] = (dst.astype(np.float32) * (1 - al) + a[..., :3].astype(np.float32) * al).astype(np.uint8)

def eo(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def expo(x): x = min(max(x, 0), 1); return 1 if x >= 1 else 1 - 2 ** (-10 * x)

def card_frame(fr, C, t):
    u = t - C["t0"]; d = C["d"]
    if u < 0 or u > d: return fr
    # entrada: fundo do cartão cobre a tela em 0.12 s (com zoom-punch da tela)
    kin = eo(u / 0.12); kout = eo((u - (d - 0.16)) / 0.16) if u > d - 0.16 else 0
    base = fr
    if kin < 1:
        base = apply_cam(fr, 1 + 0.25 * kin, W / 2, H / 2)
    out = (base.astype(np.float32) * (1 - kin) + C["bg"].astype(np.float32) * kin).astype(np.uint8)
    # texto grande: desfoque + escala
    e = expo(u / 0.22)
    sc = 1.22 - 0.22 * e + 0.04 * max(0, u - 0.22) / d
    bl = 22 * (1 - e)
    if kout > 0: sc += 0.12 * kout; bl += 22 * kout
    over(out, C["big_np"], alpha=min(1, u / 0.08) * (1 - kout), scale=sc, blur=bl)
    over(out, C["fix_np"], alpha=eo((u - 0.05) / 0.2) * (1 - kout), dy=int(20 * (1 - eo((u - 0.05) / 0.25))))
    if kout > 0:  # saída: a tela volta com zoom-punch
        back = apply_cam(fr, 1 + 0.18 * (1 - kout), W / 2, H / 2)
        out = (out.astype(np.float32) * (1 - kout) + back.astype(np.float32) * kout).astype(np.uint8)
    return out

def build_static():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = pill("CONTA DEMONSTRAÇÃO · DADOS FICTÍCIOS", 19, (11, 11, 12, 170), (255, 255, 255, 235), padx=18, pady=10, wght=700, track=0.08)
    ov.alpha_composite(p, (W - p.width - 24, H - p.height - 22))
    return cv2.cvtColor(np.array(ov), cv2.COLOR_RGBA2BGRA)

def progress(fr, t, total):
    y0 = H - 6
    fr[y0:, :] = (fr[y0:, :].astype(np.float32) * 0.55).astype(np.uint8)
    x = int(W * t / total)
    fr[y0:, :x] = (0, 196, 245)  # BGR amarelo
    for (tc, _, _) in CH[1:]:
        xc = int(W * (tc - 1.05) / total)
        fr[y0 - 4:, xc - 2:xc + 2] = (255, 255, 255)

def render(stills=None):
    cap = cv2.VideoCapture(SRC)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total = n / FPS
    Z, X, Y = camera_path(n)
    C = build_card_layers()
    for c in C:
        c["big_np"] = cv2.cvtColor(np.array(c["big"]), cv2.COLOR_RGBA2BGRA)
        c["fix_np"] = cv2.cvtColor(np.array(c["fix"]), cv2.COLOR_RGBA2BGRA)
        c["bg"] = cv2.cvtColor(c["bg"], cv2.COLOR_RGB2BGR)
    badge = build_static()
    enc = None
    if stills is None:
        enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", os.path.join(HERE, "work", "tut_motion.mp4")],
                               stdin=subprocess.PIPE)
    want = set(int(s * FPS) for s in (stills or []))
    for f in range(n):
        ok, fr = cap.read()
        if not ok: break
        if stills is not None and f not in want: continue
        t = f / FPS
        out = apply_cam(fr, Z[f], X[f], Y[f])
        in_card = False
        for c in C:
            if c["t0"] <= t <= c["t0"] + c["d"]:
                out = card_frame(out, c, t); in_card = True
        if not in_card and t < total - 3.5:
            over(out, badge)
        if not in_card: progress(out, t, total)
        if stills is not None:
            cv2.imwrite(os.path.join(HERE, "work", f"still_{t:07.2f}.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 85])
        else:
            enc.stdin.write(out.tobytes())
    if enc: enc.stdin.close(); enc.wait(); print("ok", n)

if __name__ == "__main__":
    if sys.argv[1] == "detect": detect()
    elif sys.argv[1] == "still": render([float(x) for x in sys.argv[2].split(",")])
    else: render()
