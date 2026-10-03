"""Trilha eletrônica agitada (house moderno, 126 BPM, Lá menor) criada do zero, sem direitos de terceiros.
Subida de ruído + impacto em cada cartão de capítulo. Saída: work/musica.wav (duração do tutorial)."""
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
from motion import cards, FPS
import cv2

SR = 48000
BPM = 128
B = 60 / BPM
BAR = 4 * B
cap = cv2.VideoCapture("work/tut_fast.mov")
TOTAL = cap.get(cv2.CAP_PROP_FRAME_COUNT) / FPS + 0.2
N = int(TOTAL * SR)
rng = np.random.default_rng(11)
CARDS = [c[0] for c in cards()]
END_OUT = TOTAL - 5.0

def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)
def env_exp(n, k): return np.exp(-np.arange(n) / SR * k)
def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= buf.shape[0] or i < 0: return
    x = x[: buf.shape[0] - i]
    buf[i:i + x.shape[0]] += g * x
def saw(f, n, harm=10, detune=0.0):
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * (1 + detune) * k * t + k) / k for k in range(1, harm + 1))

def kick():
    n = int(0.38 * SR); t = np.arange(n) / SR
    f = 50 + 130 * np.exp(-t * 26)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.2)
    click = filt(rng.standard_normal(n), "high", 3000) * np.exp(-t * 350) * 0.5
    return np.tanh(2.4 * (body + click)) * 1.1
def clap():
    n = int(0.28 * SR); x = filt(rng.standard_normal(n), "band", [900, 3200])
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        i = int(o * SR); e[i:] += np.exp(-np.arange(n - i) / SR * (60 if o < 0.02 else 16))
    return x * e * 0.8
def hat(open_=False):
    n = int((0.16 if open_ else 0.045) * SR)
    return filt(rng.standard_normal(n), "high", 8500) * env_exp(n, 22 if open_ else 90)

# Am - F - C - G
# acordes com 7ª/9ª: Am9, Fmaj7, Cmaj7, G6
PROG = [(110.0, [220.0, 261.63, 329.63, 392.0, 493.88]), (87.31, [174.61, 220.0, 261.63, 329.63]),
        (130.81, [196.0, 261.63, 329.63, 493.88]), (98.0, [196.0, 246.94, 293.66, 329.63])]

drums = np.zeros(N); bass = np.zeros(N); stabs = np.zeros(N); arp = np.zeros(N); pad = np.zeros(N); fx = np.zeros(N)
K, C, HO, HC = kick(), clap(), hat(True), hat(False)

def near_card(t, before=BAR * 0.5):
    return any(c - before <= t < c for c in CARDS)

nbars = int(TOTAL / BAR) + 1
PLK = [12, None, 7, 10, None, 15, None, 12, 7, None, None, 10, 12, None, 3, None]
for bi in range(nbars):
    t0 = bi * BAR
    root, notes = PROG[bi % 4]
    section = (bi // 8) % 4          # 0: base, 1: + arpejo, 2: + stabs cheios, 3: tudo
    outro = t0 >= END_OUT
    for s in range(16):
        ts = t0 + s * B / 4
        if ts >= TOTAL: break
        hole = near_card(ts)
        if s % 4 == 0 and not hole and not outro: add(drums, K, ts, 0.95)
        if s in (4, 12) and not hole and not outro: add(drums, C, ts, 0.55)
        if s % 4 == 2 and not hole: add(drums, HO, ts, 0.20)
        if s % 2 == 1 and not hole and not outro: add(drums, HC, ts, 0.07 + 0.04 * (s % 4 == 3))
        # baixo tech house sincopado (sub saturado, salto de oitava)
        if s in (2, 3, 6, 10, 11, 14) and not hole and not outro:
            n = int(B / 4 * SR * (1.6 if s in (3, 11) else 0.9)); tt = np.arange(n) / SR
            f = root / 2 * (2 if s in (6, 14) else 1)
            x = (np.sin(2 * np.pi * f * tt) + 0.25 * np.tanh(1.3 * saw(f, n, 4))) * np.minimum(1, tt / 0.004) * np.exp(-tt * 7)
            add(bass, x, ts, 0.55)
        # stabs de acorde
        if section >= 1 and s in (3, 10) and not hole and not outro:
            n = int(0.2 * SR)
            x = sum(saw(f, n, 8, d) for f in notes for d in (-0.006, 0.0, 0.006)) * env_exp(n, 14) * 0.8
            add(stabs, x, ts, 0.05 if section == 1 else 0.07)
        # pluck esparso em colcheias (pentatônica), com muito reverb
        if section in (1, 3) and s % 2 == 0 and not hole and not outro and PLK[(bi * 8 + s // 2) % len(PLK)] is not None:
            f = 440.0 * 2 ** (PLK[(bi * 8 + s // 2) % len(PLK)] / 12)
            n = int(0.25 * SR); tt = np.arange(n) / SR
            x = (saw(f, n, 10) + 0.4 * np.sin(2 * np.pi * f * 2 * tt)) * np.exp(-tt * 16)
            add(arp, x, ts, 0.05)
    # pad de fundo
    n = int(BAR * SR) + int(0.5 * SR); tt = np.arange(n) / SR
    e = np.minimum(1, tt / 0.3) * np.exp(-np.maximum(0, tt - BAR) * 5)
    add(pad, sum(saw(f, n, 18, d) for f in notes for d in (-0.011, -0.004, 0.004, 0.011)) * e, t0, 0.012)

# ---- camadas extras: baixo rolante saturado, melodia, prato, virada, shaker
from scipy.signal import fftconvolve
roll = np.zeros(N); lead = np.zeros(N); perc = np.zeros(N)
LEAD = [0, None, 3, None, 5, 3, None, 7, None, 5, 3, None, 0, None, -2, None]  # graus (semitons de A5)
def crash():
    n = int(1.8 * SR); return filt(rng.standard_normal(n), "high", 5000) * env_exp(n, 2.6)
def shaker():
    n = int(0.05 * SR); return filt(rng.standard_normal(n), "band", [5000, 11000]) * np.sin(np.pi * np.arange(n) / n)
CR, SH = crash(), shaker()
RIM = filt(rng.standard_normal(int(0.03 * SR)), "band", [1800, 2600]) * env_exp(int(0.03 * SR), 120) * 2
for bi in range(nbars):
    t0 = bi * BAR; root, notes = PROG[bi % 4]; section = (bi // 8) % 4
    if t0 >= END_OUT: continue
    if bi % 8 == 0 and bi > 0: add(perc, CR, t0, 0.22)
    for s16 in range(16):
        ts = t0 + s16 * B / 4
        if ts >= TOTAL or near_card(ts): continue
        if False:  # baixo rolante desligado (soava trance anos 2000)
            n = int(B / 4 * SR)
            x = np.tanh(2.2 * saw(root, n, 9)) * env_exp(n, 16)
            add(roll, x, ts, 0.16 + 0.05 * (s16 % 4 == 2))
        add(perc, SH, ts, 0.05 + 0.03 * (s16 % 2))
        if s16 in (3, 7, 13) and section != 0: add(perc, RIM, ts, 0.18)
        if section >= 2 and LEAD[s16] is not None and bi % 2 == 0:
            f = 880.0 * 2 ** (LEAD[s16] / 12)
            n = int(B / 2 * SR); tt = np.arange(n) / SR
            x = (saw(f, n, 12) + 0.5 * saw(f * 2, n, 6, 0.004)) * np.exp(-tt * 14)
            add(lead, x, ts, 0.045)
    # virada de caixa no último compasso de cada bloco de 8
    if bi % 8 == 7:
        for s16 in range(8, 16):
            ts = t0 + s16 * B / 4
            if not near_card(ts): add(perc, C, ts, 0.12 + 0.05 * (s16 - 8))
roll = filt(roll, "low", 750)
lead = filt(lead, "low", 2600)
# delay pontuado na melodia
dl = int(0.75 * B * SR); lead2 = lead.copy(); lead2[dl:] += lead[:-dl] * 0.35; lead = lead2
bass = filt(bass, "low", 240)
stabs = filt(stabs, "low", 3200)
pad = filt(filt(pad, "low", 1100), "high", 180)
# filtro do arpejo abrindo e fechando a cada 8 compassos
arp_hi = filt(arp, "low", 3800); arp_lo = filt(arp, "low", 1400)
ph = (np.arange(N) / SR / (8 * BAR)) % 1
mixk = 0.5 - 0.5 * np.cos(2 * np.pi * ph)
arp = arp_lo * (1 - mixk) + arp_hi * mixk

# pump (sidechain do bumbo)
pump = np.ones(N)
for bi in range(int(TOTAL / B) + 1):
    tb = bi * B
    if near_card(tb) or tb >= END_OUT: continue
    i = int(tb * SR); m = min(int(0.22 * SR), N - i)
    if m > 0: pump[i:i + m] = np.minimum(pump[i:i + m], 0.35 + 0.65 * (np.arange(m) / m) ** 0.7)
for x in (bass, stabs, pad, arp, roll, lead): x *= pump

# efeitos nos cartões
def riser(d):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n)
    seg = n // 14
    for k in range(14):
        a, b = k * seg, (k + 1) * seg if k < 13 else n
        c = 500 * 2 ** (k / 3.0)
        out[a:b] = filt(x, "band", [c, min(c * 1.9, 20000)])[a:b]
    return out * (t / d) ** 2
def impact():
    n = int(1.6 * SR); t = np.arange(n) / SR
    f = 36 + 60 * np.exp(-t * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.8) + filt(rng.standard_normal(n), "low", 3000) * np.exp(-t * 10) * 0.45
R, I = riser(BAR * 0.5), impact()
for c in CARDS:
    add(fx, R, c - BAR * 0.5, 0.16)
    add(fx, I, max(0, c), 0.5)

ir_n = int(1.4 * SR); ir_t = np.arange(ir_n) / SR
irL = filt(rng.standard_normal(ir_n), "low", 6000) * np.exp(-ir_t * 3.8)
irR = filt(rng.standard_normal(ir_n), "low", 6000) * np.exp(-ir_t * 3.8)
send = stabs * 0.9 + arp * 0.8 + lead + pad * 0.8 + filt(drums, "band", [900, 4000]) * 0.15
revL = fftconvolve(send, irL)[:N] * 0.09; revR = fftconvolve(send, irR)[:N] * 0.09
core = drums * 1.15 + bass * 1.2 + roll + pad + fx + perc
d1, d2 = int(0.009 * SR), int(0.013 * SR)
Lw = core + stabs * 0.9 + arp * 1.1 + lead + revL
Rw = core + revR
Rw[d1:] += stabs[:-d1] * 0.9
Rw[d2:] += arp[:-d2] * 1.1 + lead[:-d2] * 0.9
Lw = filt(Lw, "high", 28); Rw = filt(Rw, "high", 28)
# compressor de barramento simples + saturação
for ch in (Lw, Rw):
    pass
mono = np.abs(Lw) + np.abs(Rw)
envc = filt(mono, "low", 8)
g = 1 / (1 + np.maximum(0, envc / np.percentile(envc, 70) - 1) * 0.6)
Lw = np.tanh(1.5 * Lw * g / np.max(np.abs(Lw * g))) ; Rw = np.tanh(1.5 * Rw * g / np.max(np.abs(Rw * g)))
st = np.stack([Lw, Rw], 1)
fi, fo = int(0.03 * SR), int(4.5 * SR)
st[:fi] *= np.linspace(0, 1, fi)[:, None]
st[-fo:] *= (np.linspace(1, 0, fo) ** 1.6)[:, None]
st = st / np.max(np.abs(st)) * 0.85
wavfile.write("work/musica.wav", SR, (st * 32767).astype(np.int16))
print("musica", round(TOTAL, 2), "s")
