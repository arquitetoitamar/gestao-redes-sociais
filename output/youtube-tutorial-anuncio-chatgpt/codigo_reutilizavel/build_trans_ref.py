"""Transition reference reel (1920x1080): each transition shown slowly with its name. usage: build_trans_ref.py render <out.mp4> | still <frames...>"""
import os, subprocess, sys
import numpy as np, cv2
from engine import *
import build_intro as bi

SCR = os.path.dirname(os.path.abspath(__file__))
D = "/Users/itamar/Downloads/"
L, R = 36, 6
n = L + 2 * R
SPECS = [
    ("photo", "med/IMG_3716_2560.jpg", dict(zoom=(1.0, 1.10))),
    ("video", D + "IMG_3717.MOV", dict(start=5.0, zoom=(1.02, 1.10))),
    ("video", D + "IMG_3643.MOV", dict(start=9.0, zoom=(1.0, 1.08))),
    ("photo", "med/IMG_3726_2560.jpg", dict(zoom=(1.0, 1.12), pan=(0.35, 0.5, 0.6, 0.5))),
    ("video", D + "F5E29DCB-25C3-486E-B2E0-1E48E363F137.MP4", dict(start=6.0, portrait=True, zoom=(1.0, 1.06))),
    ("photo", "med/IMG_3644_2560.jpg", dict(zoom=(1.0, 1.12), pan=(0.5, 0.45, 0.45, 0.6))),
    ("video", bi.DANILO, dict(start=27.0, portrait=True, zoom=(1.0, 1.05))),
]
NAMES = [("zoom", "1 · ZOOM PUNCH", "zoom rápido com flash: energia e impacto"),
         ("whip", "2 · WHIP PAN", "deslize com motion blur: troca de assunto"),
         ("glitch", "3 · GLITCH RGB", "falha digital: tecnologia e IA"),
         ("flash", "4 · FLASH CUT", "estouro de luz branca: batida forte"),
         ("spin", "5 · GIRO", "rotação com blur: dinamismo"),
         ("whip_l", "6 · WHIP INVERSO", "deslize para o outro lado: variação")]

def load(j):
    kind, path, kw = SPECS[j]
    return Shot(kind, path, n, **kw)

def label(fr, tt, name, sub):
    # tt = frames relative to the cut; visible from -24 to +30
    if tt < -24 or tt > 30: return
    a = clamp01((tt + 24) / 6.0) * clamp01((30 - tt) / 6.0)
    paste(fr, _chips[name], 470, 110, alpha=a)
    paste(fr, _subs[name], 470, 178, alpha=a)

_chips, _subs = {}, {}
def prep():
    for tr, name, sub in NAMES:
        c = text_sprite(name, 66, fill=WHITE, stroke=0, shadow=False, pad=20)
        chip = Image.new("RGBA", (c.width + 30, c.height + 6), (0, 0, 0, 0))
        ImageDraw.Draw(chip).rounded_rectangle((0, 0, chip.width - 1, chip.height - 1), 20, fill=NAVY + (240,), outline=GOLD + (255,), width=4)
        chip.alpha_composite(c, (15, 3))
        _chips[name] = chip
        _subs[name] = text_sprite(sub, 38, fill=WHITE, stroke=6, shadow=False, pad=10)

def frames():
    prep()
    prev = None
    cur = load(0); nxt = load(1)
    for j in range(7):
        for c in range(L):
            if j >= 1 and c < R:                       # second half of the transition that started in the previous shot
                k = (c + R + 0.5) / (2 * R)
                fr = TRANS[NAMES[j - 1][0]](prev.frames[c + L + R], cur.frames[c + R], k)
            elif j < 6 and c >= L - R:                 # first half
                k = (c - (L - R) + 0.5) / (2 * R)
                fr = TRANS[NAMES[j][0]](cur.frames[c + R], nxt.frames[c - L + R], k)
            else:
                fr = cur.frames[c + R]
            yield np.ascontiguousarray(fr).copy(), j, c
        prev, cur = cur, nxt
        nxt = load(j + 2) if j + 2 < 7 else None

if __name__ == "__main__":
    os.chdir(SCR)
    prep()
    out = sys.argv[2]
    total = 7 * L
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-stream_loop", "1", "-i", os.path.join(SCR, "rock_mix.wav"),
                            "-af", f"afade=t=in:st=0:d=0.05,afade=t=out:st={total / FPS - 0.8:.2f}:d=0.8,volume=0.9,loudnorm=I=-15:TP=-1.2:LRA=9,aresample=44100",
                            "-t", f"{total / FPS:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    want = set(int(x) for x in sys.argv[3:]) if sys.argv[1] == "still" else None
    idx = 0
    for fr, j, c in frames():
        # label overlay relative to the next cut of this shot (cut at c == L)
        if j < 6: label(fr, c - L, NAMES[j][1], NAMES[j][2])
        if j > 0: label(fr, c, NAMES[j - 1][1], NAMES[j - 1][2])
        if want is not None:
            if idx in want: cv2.imwrite(f"tr_still_{idx}.png", cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
        else:
            enc.stdin.write(np.ascontiguousarray(fr).tobytes())
        idx += 1
    enc.stdin.close(); enc.wait()
    print("done", out, enc.returncode, "frames", idx)
