"""Reel GestorPro para campanha de topo de funil.
Junta o bastidor do coworking (abertura humana) com o GestorPro em operação.
Evita por regra: faixa de tokens processados e a lista com números de reclamação.
"""
import os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

GP = "/Users/itamar/Downloads/WhatsApp Video 2026-10-09 at 17.16.51.mp4"
CW = "/Users/itamar/Downloads/WhatsApp Video 2026-10-08 at 16.03.28.mp4"
OUT = "/Users/itamar/git/gestao-redes-sociais/output/reel-gestorpro-funil"
FONTP = "/Users/itamar/git/gestao-redes-sociais/output/reel-explica-marketplace-connect/assets/Inter.ttf"
W, H, FPS = 1080, 1920, 30
ACCENT = (37, 196, 234)
os.makedirs(OUT, exist_ok=True)

# (fonte, inicio, duracao, crop_top_frac, l1, l2, destaque)
# crop_top_frac corta o topo do quadro: usado para excluir a faixa de "tokens processados"
CENAS = [
    (CW, 2.0, 3.2, 0.00, "VOCÊ AINDA OPERA", "SUA LOJA NA MÃO?", "NA MÃO?"),
    (GP, 58.0, 4.4, 0.00, "ISSO É A SUA", "OPERAÇÃO INTEIRA", "INTEIRA"),
    (GP, 17.2, 4.2, 0.17, "9 AGENTES DE IA", "TRABALHANDO NELA", "9 AGENTES"),
    (GP, 50.5, 4.2, 0.00, "CADA UM COM", "UMA FUNÇÃO", "UMA FUNÇÃO"),
    (GP, 22.5, 4.6, 0.09, "2.232 AÇÕES", "VOCÊ NÃO FEZ NENHUMA", "NENHUMA"),
    (GP, 30.0, 4.0, 0.09, "E NADA MUDA", "SEM VOCÊ APROVAR", "SEM VOCÊ"),
]
CTA = 4.2

def font(sz, w=900):
    f = ImageFont.truetype(FONTP, int(sz))
    try:
        axes = f.get_variation_axes()
        vals = []
        for a in axes:
            nm = a.get("name", b"")
            nm = nm.decode() if isinstance(nm, bytes) else str(nm)
            vals.append(w if "eight" in nm.lower() else a["default"])
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f

def text_layer(l1, l2, destaque, maxw=990):
    img = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def fit(t, base=94):
        f = font(base)
        while d.textlength(t, font=f) > maxw and base > 46:
            base -= 3; f = font(base)
        return f
    y = 0
    for txt, hl in ((l1, False), (l2, True)):
        f = fit(txt)
        tw = d.textlength(txt, font=f)
        x = (W - tw) / 2
        if hl and destaque:
            cx = x
            for w_ in txt.split():
                ww = d.textlength(w_ + " ", font=f)
                col = ACCENT + (255,) if w_ in destaque.split() else (255, 255, 255, 255)
                for ox in (-3, 0, 3):
                    for oy in (-3, 0, 3):
                        d.text((cx + ox, y + oy), w_, font=f, fill=(6, 8, 14, 255))
                d.text((cx, y), w_, font=f, fill=col)
                cx += ww
        else:
            for ox in (-3, 0, 3):
                for oy in (-3, 0, 3):
                    d.text((x + ox, y + oy), txt, font=f, fill=(6, 8, 14, 255))
            d.text((x, y), txt, font=f, fill=(255, 255, 255, 255))
        y += int(f.size * 1.14)
    return np.array(img)

def cta_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f1 = font(118, 900)
    t = "GESTORPRO"
    tw = d.textlength(t, font=f1)
    d.text(((W - tw) / 2, 690), t, font=f1, fill=(255, 255, 255, 255))
    f2 = font(46, 600)
    s = "escritório de agentes de IA para a sua loja"
    sw = d.textlength(s, font=f2)
    d.text(((W - sw) / 2, 840), s, font=f2, fill=(220, 232, 255, 230))
    f3 = font(52, 900)
    b = "3 DIAS GRÁTIS"
    bw = d.textlength(b, font=f3)
    d.rounded_rectangle(((W - bw) / 2 - 44, 960, (W + bw) / 2 + 44, 1062), 51, fill=ACCENT + (255,))
    d.text(((W - bw) / 2, 977), b, font=f3, fill=(8, 12, 22, 255))
    f4 = font(40, 700)
    u = "gestorpro.tiops.com.br"
    uw = d.textlength(u, font=f4)
    d.text(((W - uw) / 2, 1110), u, font=f4, fill=(255, 255, 255, 190))
    return np.array(img)
CTA_L = cta_layer()

def over(base, layer, y0, alpha=1.0):
    h = layer.shape[0]
    if y0 + h > H: h = H - y0; layer = layer[:h]
    if h <= 0: return
    a = layer[:, :, 3:4].astype(np.float32) / 255.0 * alpha
    roi = base[y0:y0 + h].astype(np.float32)
    base[y0:y0 + h] = (roi * (1 - a) + layer[:, :, :3][:, :, ::-1].astype(np.float32) * a).astype(np.uint8)

eo = lambda x: 0 if x <= 0 else (1 if x >= 1 else 1 - (1 - x) ** 3)

def main():
    tmp = os.path.join(OUT, "_t.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    VH, VY = 780, 470
    rng = np.random.default_rng(3)
    grain = [rng.normal(0, 3.0, (H, W, 1)).astype(np.float32) for _ in range(10)]
    gi = 0
    for src, ini, dur, ctop, l1, l2, hl in CENAS:
        lay = text_layer(l1, l2, hl)
        cap = cv2.VideoCapture(src)
        cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
        n = int(dur * FPS)
        for i in range(n):
            ok, fr = cap.read()
            if not ok: break
            if ctop > 0:
                fr = fr[int(fr.shape[0] * ctop):, :]
            t = i / FPS
            bg = cv2.resize(fr, (W, int(W * fr.shape[0] / fr.shape[1])), interpolation=cv2.INTER_LINEAR)
            if bg.shape[0] < H:
                k = H / bg.shape[0]
                bg = cv2.resize(bg, (int(W * k), H), interpolation=cv2.INTER_LINEAR)
            x0 = max(0, (bg.shape[1] - W) // 2); y0 = max(0, (bg.shape[0] - H) // 2)
            out = (bg[y0:y0 + H, x0:x0 + W].astype(np.float32) * 0.3).astype(np.uint8)
            out = cv2.GaussianBlur(out, (0, 0), 26)
            z = 1.3 + 0.06 * (t / dur)
            nw = int(W * z); nh = int(nw * fr.shape[0] / fr.shape[1])
            v = cv2.resize(fr, (nw, nh), interpolation=cv2.INTER_CUBIC)
            cx = (nw - W) // 2; cy = max(0, (nh - VH) // 2)
            v = v[cy:cy + VH, cx:cx + W]
            if v.shape[0] < VH:
                v = cv2.copyMakeBorder(v, 0, VH - v.shape[0], 0, 0, cv2.BORDER_REPLICATE)
            out[VY:VY + VH] = cv2.convertScaleAbs(v, alpha=1.07, beta=-5)
            u = eo(t / 0.24)
            fade = 1.0 if t < dur - 0.2 else max(0.0, (dur - t) / 0.2)
            over(out, lay, int(140 + 24 * (1 - u)), alpha=u * fade)
            out = np.clip(out.astype(np.float32) + grain[gi % 10], 0, 255).astype(np.uint8); gi += 1
            enc.stdin.write(out.tobytes())
        cap.release()
    # CTA
    for i in range(int(CTA * FPS)):
        t = i / FPS
        out = np.zeros((H, W, 3), np.uint8); out[:, :] = (16, 11, 8)
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - 900) / H) ** 2)
        g = np.clip(1 - r * 1.8, 0, 1)[..., None]
        out = np.clip(out + g * np.array([78, 44, 16]), 0, 255).astype(np.uint8)
        over(out, CTA_L, 0, alpha=eo(t / 0.3))
        out = np.clip(out.astype(np.float32) + grain[gi % 10], 0, 255).astype(np.uint8); gi += 1
        enc.stdin.write(out.tobytes())
    enc.stdin.close(); enc.wait()
    final = os.path.join(OUT, "reel_gestorpro_funil_SEM_AUDIO.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-an", "-c:v", "libx264",
                    "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", final], check=True)
    os.remove(tmp)
    total = sum(c[2] for c in CENAS) + CTA
    print("ok", round(total, 1), "s")

if __name__ == "__main__":
    main()
