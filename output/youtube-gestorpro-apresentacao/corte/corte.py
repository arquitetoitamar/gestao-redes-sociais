"""Corte vertical (1080x1920) do tutorial GestorPro: Vendas e margem + Promoções.
uso: python3 corte.py still t1,t2 | render"""
import os, sys, json, math, subprocess, re
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import motion as M
from motion import text_img, font, pill, eo, expo

HERE = os.path.dirname(os.path.abspath(__file__))
PAR = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 30
SW, SH = 1920, 1080
YEL = (245, 196, 0); INK = (11, 11, 12)

# trechos no tempo do tutorial acelerado (work/tut_fast.mov / work/tut_mix.wav)
HOOK = (81.72, 1.00)                       # impacto do cartão original + título
SEG1 = (82.72, 104.60, "VENDAS E MARGEM")
CARD = (141.00, 0.90, "PROMOÇÕES.")
SEG2 = (141.90, 168.25, "PROMOÇÕES")
END = (168.24, 3.20)                       # só música (impacto no início)

T_HOOK = 0.0
T_S1 = HOOK[1]
T_CARD = T_S1 + SEG1[1] - SEG1[0]
T_S2 = T_CARD + CARD[1]
T_END = T_S2 + SEG2[1] - SEG2[0]
TOTAL = T_END + END[1]

def out_to_src(t):
    if T_S1 <= t < T_CARD: return SEG1[0] + (t - T_S1), SEG1[2]
    if T_S2 <= t < T_END: return SEG2[0] + (t - T_S2), SEG2[2]
    return None, None

# ---------------- legendas: frases da SRT divididas em pedaços de ~6 palavras
def load_caps():
    src = open("/Users/itamar/Downloads/gestorpro-tutorial.srt").read()
    def s(t): h, m, x = t.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(x)
    caps = []
    for blk in src.strip().split("\n\n"):
        L = blk.split("\n"); a, b = L[1].split(" --> ")
        a, b = (s(a) - 2) / 1.1, (s(b) - 2) / 1.1
        txt = " ".join(L[2:]).strip()
        words = txt.split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 6 or (len(cur) >= 3 and re.search(r"[.,:;—?!]$", w)):
                chunks.append(" ".join(cur)); cur = []
        if cur: chunks.append(" ".join(cur))
        tot = sum(len(c) for c in chunks); t = a
        for c in chunks:
            d = (b - a) * len(c) / tot
            caps.append((t, t + d, c)); t += d
    return caps
CAPS = load_caps()

# ---------------- elementos fixos
def bg():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
    g = np.clip(1 - r * 1.5, 0, 1)[..., None]
    b = (np.array([12, 11, 11]) + g * np.array([10, 16, 22])).astype(np.uint8)  # BGR
    return b
BG = bg()

def rgba_to_bgra(im): return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)
def layer(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def title_layer():
    L = layer(); d = ImageDraw.Draw(L)
    hf = font(24, 700)
    d.ellipse((70, 108, 84, 122), fill=YEL + (255,))
    d.text((98, 101), "GESTORPRO · ESCRITÓRIO DE AGENTES", font=hf, fill=(255, 255, 255, 120))
    l1 = text_img("QUANTO SOBRA", 112, (255, 255, 255, 255))
    l2 = text_img("DE CADA VENDA?", 112, (255, 255, 255, 255))
    s = min(1, 940 / max(l1.width, l2.width))
    if s < 1:
        l1 = text_img("QUANTO SOBRA", 112 * s, (255, 255, 255, 255)); l2 = text_img("DE CADA VENDA?", 112 * s, (255, 255, 255, 255))
    L.alpha_composite(l1, ((W - l1.width) // 2, 160)); L.alpha_composite(l2, ((W - l2.width) // 2, 160 + l1.height - 22))
    return L, 160, 160 + l1.height - 22 + l2.height
TITLE, TITLE_TOP, TITLE_BOT = title_layer()
TITLE_NP = rgba_to_bgra(TITLE)

def chip_np(txt):
    L = layer(); p = pill(txt, 30, YEL + (255,), INK + (255,), padx=26, pady=12, wght=900, track=0.06)
    L.alpha_composite(p, ((W - p.width) // 2, 468)); return rgba_to_bgra(L)
CHIPS = {SEG1[2]: chip_np(SEG1[2]), SEG2[2]: chip_np(SEG2[2])}

def note_np():
    L = layer(); t = text_img("conta demonstração · dados fictícios", 23, (255, 255, 255, 105), track=0.02, wght=600)
    L.alpha_composite(t, ((W - t.width) // 2, 1392)); return rgba_to_bgra(L)
NOTE = note_np()

PX, PY, PW, PH = 40, 545, 1000, 835       # painel da tela
RADIUS = 28
pmask = np.zeros((PH, PW), np.uint8)
cv2.rectangle(pmask, (RADIUS, 0), (PW - RADIUS, PH), 255, -1); cv2.rectangle(pmask, (0, RADIUS), (PW, PH - RADIUS), 255, -1)
for cx, cy in ((RADIUS, RADIUS), (PW - RADIUS, RADIUS), (RADIUS, PH - RADIUS), (PW - RADIUS, PH - RADIUS)):
    cv2.circle(pmask, (cx, cy), RADIUS, 255, -1, cv2.LINE_AA)
pmask = cv2.GaussianBlur(pmask, (3, 3), 0).astype(np.float32)[..., None] / 255
shadow = np.zeros((H, W), np.float32); shadow[PY + 30:PY + PH + 40, PX + 10:PX + PW - 10] = 1
shadow = cv2.GaussianBlur(shadow, (0, 0), 30)[..., None] * 0.55

cap_cache = {}
def caption_np(txt):
    if txt in cap_cache: return cap_cache[txt]
    L = layer(); f = font(50, 800)
    words = txt.split(); lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.getlength(test) > 880 and cur: lines.append(cur); cur = w
        else: cur = test
    lines.append(cur)
    y = 1450
    for ln in lines[:2]:
        t = text_img(ln, 50, (255, 255, 255, 255), track=-0.01, wght=800)
        # contorno escuro para ler em qualquer fundo
        sh = Image.new("RGBA", t.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 200), (0, 0), t)
        from PIL import ImageFilter
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        x = (W - t.width) // 2
        L.alpha_composite(sh, (x, y + 3)); L.alpha_composite(t, (x, y)); y += 64
    cap_cache[txt] = rgba_to_bgra(L); return cap_cache[txt]

def over(dst, a, alpha=1.0, dy=0, scale=1.0, blur=0.0):
    if scale != 1.0 or dy:
        Mx = cv2.getRotationMatrix2D((W / 2, H / 2), 0, scale); Mx[1, 2] += dy
        a = cv2.warpAffine(a, Mx, (W, H))
    if blur > 0.5: a = cv2.GaussianBlur(a, (0, 0), blur)
    al = a[..., 3:4].astype(np.float32) / 255 * alpha
    dst[:] = (dst.astype(np.float32) * (1 - al) + a[..., :3].astype(np.float32) * al).astype(np.uint8)

# ---------------- câmera (reaproveita a detecção de destaques do vídeo longo)
cap_src = cv2.VideoCapture(os.path.join(PAR, "work", "tut_fast.mov"))
NSRC = int(cap_src.get(cv2.CAP_PROP_FRAME_COUNT))
def vertical_path(n):
    D = json.load(open(os.path.join(PAR, "work", "boxes.json")))
    box = [None] * n
    for r in D["boxes"]:
        if len(r) > 1:
            for k in (r[0], r[0] + 1):
                if k < n: box[k] = r[1:]
    last, gap = None, 0
    for k in range(n):
        if box[k] is not None: last, gap = box[k], 0
        else:
            gap += 1
            if last is not None and gap < 24: box[k] = last
    tw, tx, ty = np.full(n, 1120.0), np.full(n, 830.0), np.full(n, 520.0)
    for k in range(n):
        if box[k] is None: continue
        x, y, w, h = box[k]
        cw = max(w * 1.7, h * 1.7 * PW / PH, 600)
        if cw > 1120: continue
        tw[k] = cw; tx[k] = x + w / 2; ty[k] = y + h / 2
    om = 2 * math.pi / 1.2; dt = 1 / FPS
    w, x, y, vw, vx, vy = 1120.0, 830.0, 520.0, 0, 0, 0
    Wv, Xv, Yv = np.zeros(n), np.zeros(n), np.zeros(n)
    for k in range(n):
        a = om * om * (tw[k] - w) - 2 * om * vw; vw += a * dt; w += vw * dt
        a = om * om * (tx[k] - x) - 2 * om * vx; vx += a * dt; x += vx * dt
        a = om * om * (ty[k] - y) - 2 * om * vy; vy += a * dt; y += vy * dt
        Wv[k], Xv[k], Yv[k] = w, x, y
    return Wv, Xv, Yv
CW, CX, CY = vertical_path(NSRC)
def src_frame(ts):
    cap_src.set(cv2.CAP_PROP_POS_FRAMES, int(round(ts * FPS)))
    ok, fr = cap_src.read(); return fr
def panel_view(fr, k):
    k = min(k, NSRC - 1)
    cw = float(CW[k]); ch = cw * PH / PW
    cx = min(max(CX[k], cw / 2), SW - cw / 2); cy = min(max(CY[k], ch / 2), SH - ch / 2)
    Mx = np.float32([[PW / cw, 0, -(cx - cw / 2) * PW / cw], [0, PH / ch, -(cy - ch / 2) * PH / ch]])
    return cv2.warpAffine(fr, Mx, (PW, PH), flags=cv2.INTER_CUBIC if cw < PW else cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)

def big_card_np(word, dark=True):
    L = layer(); fg = (255, 255, 255, 255) if dark else INK + (255,)
    t = text_img(word, 190, fg); s = min(1, 960 / t.width)
    if s < 1: t = text_img(word, 190 * s, fg)
    L.alpha_composite(t, ((W - t.width) // 2, (H - t.height) // 2 - 60)); return rgba_to_bgra(L)
PROMO_NP = big_card_np(CARD[2], dark=False)

def end_layers():
    A = layer(); B = layer()
    t = text_img("GESTORPRO.", 190, (255, 255, 255, 255)); s = min(1, 960 / t.width)
    if s < 1: t = text_img("GESTORPRO.", 190 * s, (255, 255, 255, 255))
    A.alpha_composite(t, ((W - t.width) // 2, 620))
    sub = text_img("Escritório de agentes de IA", 42, (255, 255, 255, 185), track=-0.01, wght=500)
    A.alpha_composite(sub, ((W - sub.width) // 2, 620 + t.height + 10))
    sub2 = text_img("para marketplaces", 42, (255, 255, 255, 185), track=-0.01, wght=500)
    A.alpha_composite(sub2, ((W - sub2.width) // 2, 620 + t.height + 64))
    # CTA
    kw = pill("GESTOR", 50, YEL + (255,), INK + (255,), padx=30, pady=12, wght=900, track=0.03)
    lab = text_img("Comenta", 50, INK + (255,), track=-0.02, wght=800)
    wv, hv = lab.width + kw.width + 90, kw.height + 26
    cta = Image.new("RGBA", (wv, hv), (0, 0, 0, 0))
    ImageDraw.Draw(cta).rounded_rectangle((0, 0, wv - 1, hv - 1), hv // 2, fill=(255, 255, 255, 255))
    cta.alpha_composite(lab, (40, (hv - lab.height) // 2 + 3)); cta.alpha_composite(kw, (40 + lab.width + 20, 13))
    B.alpha_composite(cta, ((W - wv) // 2, 1040))
    s3 = text_img("que eu te mando o link · 3 dias grátis", 30, (255, 255, 255, 150), track=0.0, wght=600)
    B.alpha_composite(s3, ((W - s3.width) // 2, 1040 + hv + 26))
    s4 = text_img("gestorpro.tiops.com.br", 28, (255, 255, 255, 110), track=0.02, wght=600)
    B.alpha_composite(s4, ((W - s4.width) // 2, 1330))
    return rgba_to_bgra(A), rgba_to_bgra(B)
END_A, END_B = end_layers()

def frame(t):
    out = BG.copy()
    if t < T_S1:                                     # gancho: título entra grande e sobe
        u = t / T_S1
        e = expo(u / 0.35)
        sc = 1.35 - 0.35 * e; bl = 20 * (1 - e)
        mv = eo((u - 0.55) / 0.45)
        over(out, TITLE_NP, alpha=min(1, u / 0.1), scale=sc * (1 + 0.35 * (1 - mv)) / 1.0 if False else sc, blur=bl, dy=int(520 * (1 - mv)))
        return out
    if T_CARD <= t < T_S2:                           # cartão PROMOÇÕES.
        u = (t - T_CARD) / CARD[1]
        out[:] = (out.astype(np.float32) * 0).astype(np.uint8); out[:] = YEL[::-1]
        e = expo(u / 0.25); ko = eo((u - 0.82) / 0.18)
        over(out, PROMO_NP, alpha=min(1, u / 0.08) * (1 - ko), scale=1.25 - 0.25 * e + 0.12 * ko, blur=22 * (1 - e) + 20 * ko)
        return out
    if t >= T_END:                                   # cartão final
        u = t - T_END
        over(out, END_A, alpha=eo(u / 0.3), scale=1.15 - 0.15 * expo(u / 0.35), blur=18 * (1 - expo(u / 0.35)))
        over(out, END_B, alpha=eo((u - 0.35) / 0.3), dy=int(40 * (1 - eo((u - 0.35) / 0.4))))
        return out
    ts, chap = out_to_src(t)
    k = int(round(ts * FPS))
    fr = src_frame(ts)
    pv = panel_view(fr, k)
    seg_start = T_S1 if chap == SEG1[2] else T_S2
    ui = eo((t - seg_start) / 0.45)                  # painel sobe ao entrar no trecho
    dy = int(120 * (1 - ui))
    out[:] = (out.astype(np.float32) * (1 - shadow * ui)).astype(np.uint8)
    y0 = PY + dy
    region = out[y0:y0 + PH, PX:PX + PW].astype(np.float32)
    a = pmask * ui
    out[y0:y0 + PH, PX:PX + PW] = (region * (1 - a) + pv.astype(np.float32) * a).astype(np.uint8)
    over(out, TITLE_NP)
    over(out, CHIPS[chap], alpha=ui, dy=int(20 * (1 - ui)))
    over(out, NOTE, alpha=ui)
    for (a0, a1, txt) in CAPS:
        if a0 <= ts < a1:
            cu = eo((ts - a0) / 0.12)
            over(out, caption_np(txt), alpha=cu, dy=int(14 * (1 - cu)))
            break
    return out

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for t in [float(x) for x in sys.argv[2].split(",")]:
            cv2.imwrite(os.path.join(HERE, f"still_{t:06.2f}.jpg"), frame(t), [cv2.IMWRITE_JPEG_QUALITY, 85])
        print("TOTAL", round(TOTAL, 2)); sys.exit()
    n = int(math.ceil(TOTAL * FPS))
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", os.path.join(HERE, "corte_video.mp4")], stdin=subprocess.PIPE)
    for f in range(n):
        enc.stdin.write(frame(f / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    json.dump({"T_S1": T_S1, "T_CARD": T_CARD, "T_S2": T_S2, "T_END": T_END, "TOTAL": TOTAL,
               "HOOK": HOOK, "SEG1": SEG1[:2], "CARD": CARD[:2], "SEG2": SEG2[:2], "END": END}, open(os.path.join(HERE, "tempos.json"), "w"))
    print("ok", n, round(TOTAL, 2))
