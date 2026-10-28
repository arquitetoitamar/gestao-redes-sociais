"""Abertura nova do canal (evolução da intro_youtube.mp4): 1920x1080, 30 fps, 12,5 s.

0-8 s   8 cenas reais da Imersão IA para Marketplaces (24/10/2026), 1 s cada (2 batidas a 120 BPM),
        cada uma com um insight em tipografia pesada + selo fixo "IMERSÃO IA PARA MARKETPLACES".
        Uma das cenas é um tríptico de fotos verticais.
8 s     drop: cartela ITAMAR / IA PARA NEGÓCIOS / ESCRITÓRIO DE AGENTES / NO MERCADO LIVRE / TIOPS.
Trilha: trilha.py (criada do zero).
uso: python3 abertura.py still f1 f2 ... | render <saida.mp4>
"""
import math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageOps
from engine import (W, H, FPS, NAVY, GOLD, CYAN, WHITE, F, clamp01, ease_out, ease_io, ease_back,
                     pillar, grade, TRANS, text_sprite, paste, vignette, shake)

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(AQUI)
VID = os.path.join(OUT, "..", "imersao-cronograma", "videos")
FOTO = os.path.join(OUT, "..", "linkedin-imersao", "fotos")
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"

SHOT = 30           # 1 s = 2 batidas a 120 BPM
CUT = 3             # meia-largura da transição
NSHOT = 8
SLAM = SHOT * NSHOT  # 240 = drop
NF = SLAM + 135      # 12,5 s
YEL = (255, 226, 54)

# (tipo, fonte, início, zoom, (cx0, cy0, cx1, cy1), insight)
CENAS = [
    ("foto", "2-IMG_9697.jpg", 0, (1.00, 1.12), (0.50, 0.42, 0.50, 0.46), "IMERSÃO IA"),
    ("foto", "1-IMG_9763.jpg", 0, (1.06, 1.16), (0.45, 0.52, 0.55, 0.52), "A PERGUNTA MUDOU"),
    ("video", "IMG_9718.MOV", 30.3, (1.02, 1.10), (0.5, 0.56, 0.5, 0.56), "POR ONDE COMEÇAR?"),
    ("video", "IMG_9717.MOV", 17.0, (1.00, 1.08), (0.5, 0.40, 0.5, 0.42), "IA NA OPERAÇÃO"),
    ("tri", [("foto", "3-IMG_9677.jpg", 0), ("video", "IMG_9719.MOV", 56.0), ("video", "IMG_9718.MOV", 34.0)],
     0, None, None, "EMPRESÁRIOS DE VERDADE"),
    ("pilar", "5-IMG_9695.jpg", 0, (1.00, 1.05), None, "AGENTES TRABALHANDO"),
    ("video", "IMG_9717.MOV", 159.6, (1.00, 1.08), (0.5, 0.55, 0.5, 0.55), "RESULTADO REAL"),
    ("video", "IMG_9633.MOV", 12.8, (1.00, 1.05), (0.5, 0.34, 0.5, 0.35), "NO MERCADO LIVRE"),
]
TRS = ["zoom", "whip", "glitch", "flash", "whip_l", "glitch", "zoom"]


# ------------------------------------------------------------------ fontes
def foto(nome):
    im = ImageOps.exif_transpose(Image.open(os.path.join(FOTO, nome))).convert("RGB")
    return np.asarray(im)


def quadros(nome, ini, n):
    """n quadros RGB 1080x1920 (vertical, já girado) a partir de `ini` s"""
    p = subprocess.run([FF, "-v", "error", "-ss", "%.3f" % ini, "-i", os.path.join(VID, nome),
                        "-vf", "fps=%d,scale=1080:1920" % FPS, "-frames:v", str(n),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    a = np.frombuffer(p.stdout, np.uint8)
    k = a.size // (1080 * 1920 * 3)
    fr = [a[i * 1080 * 1920 * 3:(i + 1) * 1080 * 1920 * 3].reshape(1920, 1080, 3) for i in range(k)]
    while len(fr) < n:
        fr.append(fr[-1])
    return fr


def cobre(img, w, h, zoom=1.0, cx=0.5, cy=0.5):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * zoom
    nw, nh = int(iw * s + 1), int(ih * s + 1)
    r = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA)
    x0 = int(min(max(cx * nw - w / 2, 0), nw - w)); y0 = int(min(max(cy * nh - h / 2, 0), nh - h))
    return r[y0:y0 + h, x0:x0 + w]


def nitidez(img):
    b = cv2.GaussianBlur(img, (0, 0), 1.2)
    return cv2.addWeighted(img, 1.45, b, -0.45, 0)


class Cena:
    def __init__(self, c):
        tipo = c[0]; n = SHOT + 2 * CUT
        self.frames = []
        if tipo == "tri":
            self.frames = triptico(c[1], n)
            return
        _, src, ini, zoom, pan, _ = c
        if tipo == "pilar":
            im = foto(src)
            for i in range(n):
                z = zoom[0] + (zoom[1] - zoom[0]) * ease_io(i / (n - 1))
                self.frames.append(grade(nitidez(pillar(im, z)), contrast=1.1, sat=1.12))
            return
        base = [foto(src)] * n if tipo == "foto" else quadros(src, ini, n)
        for i, f in enumerate(base):
            t = i / (n - 1)
            z = zoom[0] + (zoom[1] - zoom[0]) * ease_io(t)
            cx = pan[0] + (pan[2] - pan[0]) * t; cy = pan[1] + (pan[3] - pan[1]) * t
            self.frames.append(grade(nitidez(cobre(f, W, H, z, cx, cy)), contrast=1.1, sat=1.12))


def triptico(fontes, n):
    """3 painéis verticais lado a lado entrando em cascata sobre fundo navy"""
    pw, gap = 600, 20
    x0s = [(W - 3 * pw - 2 * gap) // 2 + k * (pw + gap) for k in range(3)]
    srcs = []
    for tipo, nome, ini in fontes:
        srcs.append([foto(nome)] * n if tipo == "foto" else quadros(nome, ini, n))
    bg = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]
    for c, (a, b) in enumerate(zip((4, 14, 28), (10, 46, 78))):
        bg[:, :, c] = a + (b - a) * (1 - yy)
    bg = bg.astype(np.uint8)
    out = []
    for i in range(n):
        fr = bg.copy()
        for k in range(3):
            e = ease_out((i - 2 * k) / 9.0)
            z = 1.0 + 0.06 * i / (n - 1)
            p = grade(nitidez(cobre(srcs[k][i], pw, H - 120, z, 0.5, 0.5)), contrast=1.1, sat=1.12)
            y = int(60 + (1 - e) * 700)
            if e <= 0:
                continue
            ys, ye = max(y, 0), min(y + p.shape[0], H)
            fr[ys:ye, x0s[k]:x0s[k] + pw] = p[ys - y:ye - y]
        out.append(fr)
    return out


# ------------------------------------------------------------------ textos
def insight_sprite(txt):
    tam = 170
    while True:
        sp = text_sprite(txt, tam, fill=WHITE, stroke=14, stroke_fill=(4, 24, 42))
        if sp.width <= 1720 or tam <= 90:
            return sp
        tam -= 6


def selo():
    txt = "IMERSÃO IA PARA MARKETPLACES  ·  SÃO PAULO  ·  24/10"
    f = F(34)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = tmp.textbbox((0, 0), txt, font=f)
    w, h = bb[2] - bb[0] + 92, bb[3] - bb[1] + 34
    sp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=(4, 24, 42, 200))
    d.ellipse((24, h // 2 - 9, 42, h // 2 + 9), fill=YEL + (255,))
    d.text((60 - bb[0], 17 - bb[1]), txt, font=f, fill=WHITE + (255,))
    return sp


def barra_insight(fr, c, largura):
    """traço amarelo que corre sob o insight"""
    e = ease_out((c - 2) / 8.0)
    if e <= 0:
        return
    w = int(largura * 0.55 * e)
    x0 = W // 2 - w // 2
    cv2.rectangle(fr, (x0, 968), (x0 + w, 980), YEL, -1)


# ------------------------------------------------------------------ montagem
def montage_frame(f, S, SP):
    j = f // SHOT; c = f % SHOT
    nxt = (f + CUT) // SHOT
    if nxt != j and nxt < len(S):
        cutf = nxt * SHOT
        k = (f - (cutf - CUT) + 0.5) / (2 * CUT)
        a = S[j].frames[(f - j * SHOT) + CUT]
        b = S[nxt].frames[(f - nxt * SHOT) + CUT]
        fr = TRANS[TRS[j]](a, b, k)
        jj = nxt if k > 0.5 else j
    else:
        fr = S[j].frames[c + CUT].copy(); jj = j
    fr = np.ascontiguousarray(fr)
    cc = f - jj * SHOT
    sp = SP["ins"][jj]
    if -CUT <= cc < SHOT - 1:
        k = ease_back(max(cc, 0) / 5.0, 2.4)
        pump = 1.0 + (0.05 * math.exp(-(cc - 15) / 3.0) if cc >= 15 else 0)
        al = clamp01((cc + 1) / 2.0) * (1 if cc < SHOT - 4 else clamp01((SHOT - 1 - cc) / 3.0))
        paste(fr, sp, W / 2, 875, alpha=al, scale=max(0.3, min(k, 1.25)) * pump)
        barra_insight(fr, cc, sp.width)
    # selo fixo no canto (entra no começo)
    e = ease_out(f / 12.0)
    paste(fr, SP["selo"], 60 + SP["selo"].width / 2 - (1 - e) * 900, 70, alpha=e)
    if c < 3:
        fr = cv2.addWeighted(fr, 1.0, np.full_like(fr, 255), 0.10 * (1 - c / 3.0), 0)
    return vignette(shake(fr, 5 if c == 0 else 0), 0.5)


def bg_title(ultimo):
    base = cv2.GaussianBlur(ultimo, (0, 0), 24)
    base = (base * 0.22).astype(np.uint8)
    grad = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]
    for c, (a, b) in enumerate(zip((4, 14, 28), (10, 46, 78))):
        grad[:, :, c] = a + (b - a) * (1 - yy)
    return np.clip(base * 0.55 + grad * 0.85, 0, 255).astype(np.uint8)


def streaks(t):
    Lr = np.zeros((H, W, 3), np.uint8)
    for i in range(9):
        x = int(((i * 260 + t * 420) % (W + 700)) - 350)
        cv2.line(Lr, (x, 0), (x - 380, H), (GOLD[0] // 4, GOLD[1] // 4, GOLD[2] // 4), 26 if i % 3 == 0 else 8)
    return cv2.GaussianBlur(Lr, (0, 0), 6)


def grade_tech(fr, t):
    """grade de pontos sutil que desliza (toque tech da cartela nova)"""
    ov = fr.copy()
    off = int(t * 40) % 60
    for x in range(-60 + off, W, 60):
        for y in range(30, H, 60):
            cv2.circle(ov, (x, y), 2, (60, 110, 150), -1)
    return cv2.addWeighted(fr, 0.75, ov, 0.25, 0)


def ring(fr, cx, cy, r, alpha):
    ov = fr.copy()
    cv2.circle(ov, (int(cx), int(cy)), int(r), (255, 255, 255), 10, cv2.LINE_AA)
    cv2.circle(ov, (int(cx), int(cy)), int(r * 0.86), tuple(CYAN), 5, cv2.LINE_AA)
    return cv2.addWeighted(fr, 1 - alpha, ov, alpha, 0)


def title_frame(f, bgimg, TS):
    T = f - SLAM
    fr = bgimg.copy()
    fr = np.clip(fr.astype(np.int16) + streaks(f / 30.0).astype(np.int16), 0, 255).astype(np.uint8)
    fr = grade_tech(fr, f / 30.0)
    k = ease_out(T / 8.0)
    sc = 1 + 1.3 * (1 - k)
    amp = max(0, 22 * (1 - T / 14.0))
    paste(fr, TS["name"], W / 2 + np.random.uniform(-amp, amp), 330 + np.random.uniform(-amp, amp),
          alpha=clamp01(T / 2.0), scale=sc * (1.0 + 0.012 * math.sin(f / 5.0)))
    if T < 16:
        fr = ring(fr, W / 2, 380, 60 + T * 95, 0.9 * (1 - T / 16.0))
    t2 = T - 15
    if t2 >= 0:
        e = ease_out(t2 / 10.0)
        paste(fr, TS["role"], W / 2 - (1 - e) * 900, 530, alpha=clamp01(t2 / 4.0))
    for line, t0, y in ((TS["tag1"], 30, 700), (TS["tag2"], 45, 805), (TS["brand"], 60, 950)):
        tt = T - t0
        if tt >= 0:
            kk = ease_back(tt / 6.0, 2.2)
            paste(fr, line, W / 2, y, alpha=clamp01(tt / 3.0), scale=max(0.3, min(kk, 1.2)))
    if T >= 120:
        tt = T - 120
        pulse = max(0, 1 - tt / 8.0)
        fr = cv2.addWeighted(fr, 1 - 0.7 * pulse, np.full_like(fr, 255), 0.7 * pulse, 0)
        fr = ring(fr, W / 2, 380, 60 + tt * 120, 0.8 * (1 - tt / 15.0))
    fr = shake(fr, 6 if 120 <= T < 126 else (10 if 0 <= T < 5 else 0))
    if f >= NF - 6:
        m = (f - (NF - 6) + 1) / 6.0
        fr = cv2.addWeighted(fr, 1 - m, np.full_like(fr, 255), m, 0)
    if 0 <= T < 3:
        m = 1 - T / 3.0
        fr = cv2.addWeighted(fr, 1 - 0.9 * m, np.full_like(fr, 255), 0.9 * m, 0)
    return vignette(fr, 0.45)


def sprites():
    role = text_sprite("IA PARA NEGÓCIOS", 108, fill=NAVY, stroke=0, shadow=False, pad=34)
    chip = Image.new("RGBA", (role.width + 60, role.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(chip).rounded_rectangle((0, 0, chip.width - 1, chip.height - 1), 26, fill=GOLD + (255,))
    chip.alpha_composite(role, (30, 10))
    return {"name": text_sprite("ITAMAR", 330, fill=WHITE, stroke=16, stroke_fill=(4, 24, 42)),
            "role": chip,
            "tag1": text_sprite("ESCRITÓRIO DE AGENTES", 96, fill=WHITE, stroke=9),
            "tag2": text_sprite("NO MERCADO LIVRE", 96, fill=YEL, stroke=9),
            "brand": text_sprite("T I O P S", 46, fill=GOLD, stroke=5, shadow=False)}


def frames(S, SP, TS):
    bgimg = bg_title(S[-1].frames[SHOT + CUT - 1])
    np.random.seed(3)
    for f in range(NF):
        yield montage_frame(f, S, SP) if f < SLAM else title_frame(f, bgimg, TS)


if __name__ == "__main__":
    os.chdir(AQUI)
    S = [Cena(c) for c in CENAS]
    SP = {"ins": [insight_sprite(c[-1]) for c in CENAS], "selo": selo()}
    TS = sprites()
    if sys.argv[1] == "still":
        want = set(int(x) for x in sys.argv[2:])
        for f, fr in enumerate(frames(S, SP, TS)):
            if f in want:
                cv2.imwrite("survey/still_%03d.jpg" % f, cv2.cvtColor(fr, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
            if f >= max(want):
                break
        sys.exit(0)
    out = sys.argv[2]
    enc = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                            "-r", str(FPS), "-i", "-", "-i", "trilha.wav",
                            "-af", "afade=t=in:st=0:d=0.03,afade=t=out:st=%.2f:d=0.35,aresample=48000" % (NF / FPS - 0.35),
                            "-t", "%.3f" % (NF / FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in frames(S, SP, TS):
        enc.stdin.write(np.ascontiguousarray(fr).tobytes())
    enc.stdin.close(); enc.wait()
    print("ok", out, enc.returncode)
