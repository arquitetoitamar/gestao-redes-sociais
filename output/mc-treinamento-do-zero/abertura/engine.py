"""Shared motion engine (1920x1080 @30): shot loading, Ken Burns, transitions, text sprites."""
import os, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
NAVY = (6, 43, 70); GOLD = (213, 170, 117); CYAN = (102, 199, 216); WHITE = (252, 252, 252)
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
def _idx(w):
    for i in range(16):
        try:
            if w in " ".join(ImageFont.truetype(AVENIR, 20, index=i).getname()).lower(): return i
        except Exception:
            break
    return 0
_HEAVY = _idx("heavy")
def F(s): return ImageFont.truetype(AVENIR, int(s), index=_HEAVY)

def clamp01(x): return min(max(x, 0.0), 1.0)
def ease_out(x): x = clamp01(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp01(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def ease_back(x, k=1.9): x = clamp01(x); return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2

# ------------------------------------------------------------------ frame helpers
def cover(img, w=W, h=H, zoom=1.0, cx=0.5, cy=0.5):
    """cover-fit img (H,W,3) into w x h with extra zoom, centre (cx,cy) in 0..1"""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * zoom
    nw, nh = int(iw * s + 1), int(ih * s + 1)
    r = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR if s > 1 else cv2.INTER_AREA)
    x0 = int(min(max(cx * nw - w / 2, 0), nw - w)); y0 = int(min(max(cy * nh - h / 2, 0), nh - h))
    return r[y0:y0 + h, x0:x0 + w]

def pillar(img, zoom=1.0):
    """portrait/any source: blurred cover background + centred fit foreground with shadow"""
    bg = cover(img, zoom=1.15)
    bg = cv2.GaussianBlur(bg, (0, 0), 28)
    bg = (bg * 0.5).astype(np.uint8)
    ih, iw = img.shape[:2]
    s = (H * 0.94 * zoom) / ih
    fg = cv2.resize(img, (int(iw * s), int(ih * s)), interpolation=cv2.INTER_AREA)
    fh, fw = fg.shape[:2]
    x0 = (W - fw) // 2; y0 = (H - fh) // 2
    out = bg.copy()
    sh = np.zeros_like(out); sh[max(y0 + 14, 0):min(y0 + fh + 14, H), max(x0 + 14, 0):min(x0 + fw + 14, W)] = 255
    sh = cv2.GaussianBlur(sh, (0, 0), 22)
    out = (out * (1 - 0.55 * sh / 255.0)).astype(np.uint8)
    ys, ye = max(y0, 0), min(y0 + fh, H); xs, xe = max(x0, 0), min(x0 + fw, W)
    out[ys:ye, xs:xe] = fg[ys - y0:ye - y0, xs - x0:xe - x0]
    return out

def grade(img, contrast=1.08, sat=1.15, dark=1.0):
    x = img.astype(np.float32)
    x = (x - 128) * contrast + 128
    g = x.mean(axis=2, keepdims=True)
    x = g + (x - g) * sat
    return np.clip(x * dark, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ sources
def video_frames(path, start, n, portrait=False, fps=FPS):
    """decode n frames starting at `start` (s). Returns list of RGB frames sized for cover/pillar use."""
    if portrait:
        vf = f"fps={fps},scale=1080:1920:force_original_aspect_ratio=decrease"
        w, h = None, None
    else:
        vf = f"fps={fps},scale=2304:1296:force_original_aspect_ratio=increase,crop=2304:1296"
        w, h = 2304, 1296
    if portrait:
        # probe true size after auto-rotate
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path, "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True).stdout
        im = cv2.imdecode(np.frombuffer(r, np.uint8), cv2.IMREAD_COLOR)
        h, w = im.shape[:2]
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path, "-vf", vf, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True)
    a = np.frombuffer(p.stdout, np.uint8)
    fs = a.size // (w * h * 3)
    fr = [a[i * w * h * 3:(i + 1) * w * h * 3].reshape(h, w, 3) for i in range(fs)]
    while len(fr) < n and fr: fr.append(fr[-1])
    return fr

class Shot:
    """a sequence of n frames at 1920x1080 with a Ken Burns move"""
    def __init__(self, kind, path, n, start=0.0, portrait=False, zoom=(1.0, 1.10), pan=(0.5, 0.5, 0.5, 0.5), dark=1.0):
        self.n = n; self.frames = []
        if kind == "photo":
            im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
            src = [im] * n
        else:
            src = video_frames(path, start, n, portrait)
        for i, f in enumerate(src[:n]):
            t = i / max(n - 1, 1)
            z = zoom[0] + (zoom[1] - zoom[0]) * ease_io(t)
            cx = pan[0] + (pan[2] - pan[0]) * t; cy = pan[1] + (pan[3] - pan[1]) * t
            fr = pillar(f, z) if portrait else cover(f, zoom=z, cx=cx, cy=cy)
            self.frames.append(grade(fr, dark=dark))
        while len(self.frames) < n: self.frames.append(self.frames[-1])

# ------------------------------------------------------------------ transitions (A tail frames, B head frames, k in 0..1)
def tr_flash(a, b, k):
    m = 1 - abs(2 * k - 1)                       # 0 -> 1 -> 0
    base = a if k < 0.5 else b
    w = np.full_like(base, 255)
    return cv2.addWeighted(base, 1 - m * 0.85, w, m * 0.85, 0)

def tr_zoom(a, b, k):
    if k < 0.5:
        s = 1 + 0.9 * ease_in(k * 2); src = a
    else:
        s = 1.7 - 0.7 * ease_out((k - 0.5) * 2); src = b
    z = zoom_blur(src, s, 8 if 0.25 < k < 0.75 else 3)
    m = 1 - abs(2 * k - 1)
    return cv2.addWeighted(z, 1 - 0.35 * m, np.full_like(z, 255), 0.35 * m, 0)

def ease_in(x): x = clamp01(x); return x ** 3

def zoom_blur(img, s, taps):
    acc = np.zeros_like(img, np.float32)
    for i in range(taps):
        ss = 1 + (s - 1) * (i + 1) / taps
        acc += cover(img, zoom=ss)
    return (acc / taps).astype(np.uint8)

def tr_whip(a, b, k, direction=1):
    e = ease_io(k)
    off = int(e * W)
    canvas = np.concatenate([a, b], axis=1) if direction == 1 else np.concatenate([b, a], axis=1)
    x0 = off if direction == 1 else W - off
    view = canvas[:, x0:x0 + W]
    amt = int(3 + 110 * math.sin(math.pi * k))
    if amt > 1:
        kern = np.zeros((1, amt * 2 + 1), np.float32); kern[0, :] = 1.0 / kern.size
        view = cv2.filter2D(view, -1, kern)
    return view

def tr_glitch(a, b, k, seed=0):
    rng = np.random.default_rng(seed + int(k * 100))
    base = a if k < 0.5 else b
    out = base.copy()
    amp = int(6 + 40 * math.sin(math.pi * k))
    out[:, :, 0] = np.roll(base[:, :, 0], amp, axis=1)
    out[:, :, 2] = np.roll(base[:, :, 2], -amp, axis=1)
    for _ in range(9):
        y = int(rng.integers(0, H - 60)); h = int(rng.integers(12, 90)); dx = int(rng.integers(-220, 220))
        out[y:y + h] = np.roll(out[y:y + h], dx, axis=1)
    scan = (np.arange(H) % 4 < 2)[:, None, None]
    out = np.where(scan, (out * 0.85).astype(np.uint8), out)
    return out

def tr_spin(a, b, k):
    ang = 25 * ease_io(k) * (1 if k < 0.5 else 1)
    base = a if k < 0.5 else b
    ang = (18 * math.sin(math.pi * k))
    s = 1 + 0.25 * math.sin(math.pi * k)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, s)
    r = cv2.warpAffine(base, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return cv2.GaussianBlur(r, (0, 0), 1 + 10 * math.sin(math.pi * k))

TRANS = {"flash": tr_flash, "zoom": tr_zoom, "glitch": tr_glitch, "spin": tr_spin,
         "whip": lambda a, b, k: tr_whip(a, b, k, 1), "whip_l": lambda a, b, k: tr_whip(a, b, k, -1)}

# ------------------------------------------------------------------ text sprites
def text_sprite(txt, size, fill=WHITE, stroke=10, stroke_fill=NAVY, shadow=True, pad=30):
    f = F(size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = tmp.textbbox((0, 0), txt, font=f, stroke_width=stroke)
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    sp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    if shadow:
        d.text((pad - bb[0] + 8, pad - bb[1] + 10), txt, font=f, fill=(0, 0, 0, 140), stroke_width=stroke, stroke_fill=(0, 0, 0, 140))
    d.text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill + (255,))
    return sp

def paste(dst, sp, x, y, alpha=1.0, scale=1.0, rot=0.0):
    """alpha-composite RGBA PIL sprite onto numpy RGB frame `dst` (in place), centre at (x,y)"""
    if scale != 1.0:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.LANCZOS)
    if rot:
        sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        r, g, b, a = sp.split(); sp = Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * alpha))))
    x0, y0 = int(x - sp.width / 2), int(y - sp.height / 2)
    xs, ys = max(x0, 0), max(y0, 0); xe, ye = min(x0 + sp.width, W), min(y0 + sp.height, H)
    if xe <= xs or ye <= ys: return
    reg = Image.fromarray(dst[ys:ye, xs:xe]).convert("RGBA")
    crop = sp.crop((xs - x0, ys - y0, xe - x0, ye - y0))
    dst[ys:ye, xs:xe] = np.asarray(Image.alpha_composite(reg, crop).convert("RGB"))

def vignette(img, strength=0.55):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    m = 1 - strength * np.clip(d - 0.35, 0, 1)
    return (img * m[:, :, None]).astype(np.uint8)

def shake(img, amp):
    if amp < 0.5: return img
    dx, dy = int(np.random.uniform(-amp, amp)), int(np.random.uniform(-amp, amp))
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
