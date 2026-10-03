"""YouTube intro 1920x1080, 8 s @30fps, 150 BPM rock. usage: build_intro.py still <frames...> | render <out.mp4>"""
import json, os, subprocess, sys
import numpy as np, cv2
from engine import *

SCR = os.path.dirname(os.path.abspath(__file__))
D = "/Users/itamar/Downloads/"
DANILO = D + "WhatsApp Video 2026-09-25 at 14.57.29.mp4"
CFG = {
    "name": "ITAMAR",
    "role": "IA PARA NEGÓCIOS",
    "tag1": "RESULTADO REAL COM IA",
    "tag2": "NO MARKETPLACE",
    "brand": "TIOPS",
}
if os.path.exists(os.path.join(SCR, "intro_config.json")):
    CFG.update(json.load(open(os.path.join(SCR, "intro_config.json"))))

BEAT = 12          # frames per beat @150 BPM
NF = 240           # 8.0 s
CUT = 3            # transition half-width (frames)
SLAM = 96          # bar 3 downbeat
KEYS = ["MERCADO LIVRE", "EVENTOS", "ESTRADA", "IA", "CLIENTES", "DADOS", "VENDEDORES", "RESULTADO REAL"]
TRS = ["zoom", "whip", "glitch", "flash", "whip_l", "spin", "zoom"]   # 7 cuts between 8 shots
n = BEAT + 2 * CUT

def build_shots():
    S = []
    S.append(Shot("photo", "med/IMG_3716_2560.jpg", n, zoom=(1.0, 1.14), pan=(0.4, 0.5, 0.55, 0.5)))
    S.append(Shot("video", D + "IMG_3717.MOV", n, start=5.0, zoom=(1.02, 1.12)))
    S.append(Shot("video", D + "IMG_3643.MOV", n, start=9.0, zoom=(1.0, 1.10)))
    S.append(Shot("photo", "med/IMG_3726_2560.jpg", n, zoom=(1.0, 1.16), pan=(0.35, 0.5, 0.6, 0.5)))
    S.append(Shot("video", D + "F5E29DCB-25C3-486E-B2E0-1E48E363F137.MP4", n, start=6.0, portrait=True, zoom=(1.0, 1.08)))
    S.append(Shot("photo", "med/IMG_3644_2560.jpg", n, zoom=(1.0, 1.15), pan=(0.5, 0.45, 0.45, 0.6)))
    S.append(Shot("video", D + "IMG_3723.MOV", n, start=3.0, portrait=True, zoom=(1.0, 1.08)))
    S.append(Shot("video", DANILO, n, start=27.0, portrait=True, zoom=(1.0, 1.06)))
    return S

def key_overlay(fr, j, c):
    """huge keyword slam on each beat"""
    if c > 10: return
    sp = _key_sprites[j]
    k = ease_back(c / 4.0, 2.4)
    paste(fr, sp, W / 2, 860, alpha=clamp01(c / 2.0) * (1 if c < 9 else clamp01((11 - c) / 2)), scale=max(0.3, min(k, 1.25)) * 1.0)

def bg_title(shots_last):
    base = cv2.GaussianBlur(shots_last, (0, 0), 24)
    base = (base * 0.22).astype(np.uint8)
    grad = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]
    for c, (a, b) in enumerate(zip((4, 14, 28), (10, 46, 78))):
        grad[:, :, c] = a + (b - a) * (1 - yy)
    return np.clip(base * 0.55 + grad * 0.85, 0, 255).astype(np.uint8)

def streaks(t):
    L = np.zeros((H, W, 3), np.uint8)
    for i in range(9):
        x = int(((i * 260 + t * 420) % (W + 700)) - 350)
        cv2.line(L, (x, 0), (x - 380, H), (GOLD[0] // 4, GOLD[1] // 4, GOLD[2] // 4), 26 if i % 3 == 0 else 8)
    return cv2.GaussianBlur(L, (0, 0), 6)

def ring(fr, cx, cy, r, alpha):
    ov = fr.copy()
    cv2.circle(ov, (int(cx), int(cy)), int(r), (255, 255, 255), 10, cv2.LINE_AA)
    cv2.circle(ov, (int(cx), int(cy)), int(r * 0.86), tuple(CYAN), 5, cv2.LINE_AA)
    return cv2.addWeighted(fr, 1 - alpha, ov, alpha, 0)

def title_frame(f, bgimg, S):
    T = f - SLAM
    fr = bgimg.copy()
    fr = np.clip(fr.astype(np.int16) + streaks(f / 30.0).astype(np.int16), 0, 255).astype(np.uint8)
    # NAME slam
    k = ease_out(T / 8.0)
    sc = 1 + 1.3 * (1 - k)
    amp = max(0, 22 * (1 - T / 14.0)) if T >= 0 else 0
    if T >= 0:
        paste(fr, S["name"], W / 2 + np.random.uniform(-amp, amp), 350 + np.random.uniform(-amp, amp), alpha=clamp01(T / 2.0), scale=sc * (1.0 + 0.012 * math.sin(f / 5.0)))
        if T < 16: fr = ring(fr, W / 2, 400, 60 + T * 95, 0.9 * (1 - T / 16.0))
    # ROLE chip slides in
    t2 = T - 14
    if t2 >= 0:
        e = ease_out(t2 / 10.0)
        paste(fr, S["role"], W / 2 - (1 - e) * 900, 545, alpha=clamp01(t2 / 4.0))
    # tagline lines on beats (48 = bar 4, +12, +24)
    for line, t0, y in ((S["tag1"], 48, 715), (S["tag2"], 60, 815), (S["brand"], 72, 950)):
        tt = T - t0
        if tt >= 0:
            kk = ease_back(tt / 6.0, 2.2)
            paste(fr, line, W / 2, y, alpha=clamp01(tt / 3.0), scale=max(0.3, min(kk, 1.2)))
    # light sweep + final crash pulse at bar 5 (T=96)
    if T >= 96:
        tt = T - 96
        pulse = max(0, 1 - tt / 10.0)
        fr = cv2.addWeighted(fr, 1 - 0.75 * pulse, np.full_like(fr, 255), 0.75 * pulse, 0)
        if tt < 22: fr = ring(fr, W / 2, 400, 60 + tt * 110, 0.8 * (1 - tt / 22.0))
    fr = shake(fr, 6 if (T >= 96 and T < 104) else (10 if 0 <= T < 5 else 0))
    # out flash
    if f >= NF - 6:
        m = (f - (NF - 6) + 1) / 6.0
        fr = cv2.addWeighted(fr, 1 - m, np.full_like(fr, 255), m, 0)
    if 0 <= T < 3:
        m = 1 - T / 3.0
        fr = cv2.addWeighted(fr, 1 - 0.9 * m, np.full_like(fr, 255), 0.9 * m, 0)
    return vignette(fr, 0.45)

def montage_frame(f, S):
    j = f // BEAT; c = f % BEAT
    # transition window around the cut into shot j+1
    nxt = (f + CUT) // BEAT
    if nxt != j and nxt < len(S):
        cutf = nxt * BEAT
        k = (f - (cutf - CUT) + 0.5) / (2 * CUT)
        a = S[j].frames[(f - j * BEAT) + CUT]
        b = S[nxt].frames[(f - nxt * BEAT) + CUT]
        name = TRS[j]
        fr = TRANS[name](a, b, k)
        jj = nxt if k > 0.5 else j
    else:
        fr = S[j].frames[c + CUT].copy(); jj = j
    fr = np.ascontiguousarray(fr)
    cc = f - jj * BEAT
    if 0 <= cc <= 10: key_overlay(fr, jj, cc)
    # beat pulse
    if c < 3: fr = cv2.addWeighted(fr, 1.0, np.full_like(fr, 255), 0.10 * (1 - c / 3.0), 0)
    return vignette(shake(fr, 5 if c == 0 else 0), 0.5)

_key_sprites = []
def make_sprites():
    for k in KEYS:
        _key_sprites.append(text_sprite(k, 150 if len(k) < 9 else 120, fill=WHITE, stroke=14, stroke_fill=(4, 24, 42)))
    role = text_sprite(CFG["role"], 112, fill=NAVY, stroke=0, shadow=False, pad=34)
    chip = Image.new("RGBA", (role.width + 60, role.height + 20), (0, 0, 0, 0))
    ImageDraw.Draw(chip).rounded_rectangle((0, 0, chip.width - 1, chip.height - 1), 26, fill=GOLD + (255,))
    chip.alpha_composite(role, (30, 10))
    tag1 = text_sprite(CFG["tag1"], 92, fill=WHITE, stroke=9)
    tag2 = text_sprite(CFG["tag2"], 92, fill=CYAN, stroke=9)
    brand = text_sprite(" ".join(CFG["brand"]), 46, fill=GOLD, stroke=5, shadow=False)
    name = text_sprite(CFG["name"], 340, fill=WHITE, stroke=16, stroke_fill=(4, 24, 42))
    return {"name": name, "role": chip, "tag1": tag1, "tag2": tag2, "brand": brand}

def frames(S, TS):
    bgimg = bg_title(S[-1].frames[BEAT + CUT - 1])
    for f in range(NF):
        yield montage_frame(f, S) if f < SLAM else title_frame(f, bgimg, TS)

if __name__ == "__main__":
    os.chdir(SCR)
    S = build_shots(); TS = make_sprites()
    if sys.argv[1] == "still":
        want = [int(x) for x in sys.argv[2:]]
        g = list(frames(S, TS))
        for f in want:
            cv2.imwrite(f"intro_still_{f}.png", cv2.cvtColor(g[f], cv2.COLOR_RGB2BGR))
        sys.exit(0)
    out = sys.argv[2]
    audio = os.path.join(SCR, "rock_mix.wav")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", audio, "-af", "afade=t=in:st=0:d=0.05,afade=t=out:st=7.4:d=0.6,loudnorm=I=-14:TP=-1.2:LRA=9,aresample=44100",
                            "-t", "8.0", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in frames(S, TS):
        enc.stdin.write(np.ascontiguousarray(fr).tobytes())
    enc.stdin.close(); enc.wait()
    print("done", out, enc.returncode)
