"""Trilha do Reel MadeiraMadeira (18,4 s): tech house animada, criada do zero, sem direitos de terceiros.
Substitui a trilha "impressionado" (coral + sininhos), que o Itamar achou chata em 09/11/2026.

~121 BPM (batida de 0,495 s, grade começando em 0,025 s para os drops caírem nos cortes), Lá menor:
  0-2,0 s    groove com filtro abrindo (gancho)            2,0-2,5 s  caixa acelerando, sem bumbo
  2,5 s      DROP 1 no logo (impacto, crash, supersaw, 808)
  4,6-11,9 s groove cheio nos passos (stabs, baixo rolando, palmas)
  11,4-12,4  riser + caixa acelerando                      12,4 s     DROP 2 (Claude com os resultados)
  15,9 s     chamada final; batida final em 17,8 s e cauda
Cliques de mouse e teclas nos mesmos tempos da animação. Saída: audio/trilha_house.wav (48 kHz, estéreo)."""
import os
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000; DUR = 18.4; N = int(DUR * SR)
B = 0.495; G0 = 0.025                     # duração da batida e início da grade
D1, D2, CTA, END = 2.5, 12.4, 15.9, 17.8
OFF = 2.1                                 # deslocamento da animação em relação ao reel original
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)

def filt(x, kind, f, order=2): return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)
def tt(d): return np.arange(int(d * SR)) / SR
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def add(x, t0, g=1.0, pan=0.0, bl=None, br=None):
    bl = L if bl is None else bl; br = R if br is None else br
    i = int(round(t0 * SR))
    if i >= N: return
    if i < 0: x = x[-i:]; i = 0
    x = x[: N - i]
    bl[i:i + len(x)] += g * np.sqrt((1 - pan) / 2) * 1.414 * x
    br[i:i + len(x)] += g * np.sqrt((1 + pan) / 2) * 1.414 * x
def add_st(xl, xr, t0, g, bl, br):
    i = int(round(t0 * SR)); n = min(len(xl), N - i)
    bl[i:i + n] += g * xl[:n]; br[i:i + n] += g * xr[:n]

# ---------------- instrumentos
def kick():
    t = tt(0.42); f = 46 + 120 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    return np.tanh(1.6 * (body + filt(rng.standard_normal(len(t)), "highpass", 2500) * np.exp(-t * 400) * 0.35))
def clap():
    t = tt(0.32); env = np.zeros(len(t))
    for k, o in enumerate((0.0, 0.011, 0.022)):
        i = int(o * SR); env[i:] += np.exp(-(t[i:] - o) * (95 if k < 2 else 16))
    return filt(rng.standard_normal(len(t)), "bandpass", (900, 4200)) * env * 0.8
def hat(open_=False):
    t = tt(0.22 if open_ else 0.06)
    return filt(rng.standard_normal(len(t)), "highpass", 7500) * np.exp(-t * (14 if open_ else 70)) * 0.5
def shaker():
    t = tt(0.05); return filt(rng.standard_normal(len(t)), "bandpass", (5000, 11000)) * np.sin(np.pi * t / t[-1]) * 0.22
def saw(f, d, dt=0.0):
    t = tt(d); return 2 * ((f * (1 + dt) * t + rng.random()) % 1.0) - 1
def supersaw(fs, d, voices=7, spread=0.012):
    l = np.zeros(int(d * SR)); r = np.zeros(int(d * SR))
    for f in fs:
        for v in range(voices):
            s = saw(f, d, spread * (v / (voices - 1) - 0.5)); p = (v / (voices - 1)) * 2 - 1
            l += s * (1 - p) * 0.5; r += s * (1 + p) * 0.5
    k = 1.0 / (len(fs) * voices * 0.5); return l * k, r * k
def bass_note(f, d):
    t = tt(d); x = filt(0.7 * np.sin(2 * np.pi * f * t) + 0.35 * saw(f, d), "lowpass", 900)
    return np.tanh(2.2 * x * np.minimum(1, t / 0.004) * np.exp(-t * 7))
def sub808(f, d):
    t = tt(d); fr = f * (1 + 0.6 * np.exp(-t * 40))
    return np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(fr) / SR)) * np.minimum(1, t / 0.003) * np.exp(-t * 1.6)
def whoosh(d=0.4):
    t = tt(d); n = rng.standard_normal(len(t)); a = t / d
    return (filt(n, "bandpass", (500, 1800)) * (1 - a) + filt(n, "bandpass", (1800, 7000)) * a) * np.sin(np.pi * a) ** 2 * 0.5
def crash(d=1.8): t = tt(d); return filt(rng.standard_normal(len(t)), "highpass", 3800) * np.exp(-t * 2.6) * 0.55
def impact():
    t = tt(1.6); f = 32 + 55 * np.exp(-t * 4)
    return np.tanh(1.5 * (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
                          + filt(rng.standard_normal(len(t)), "lowpass", 300) * np.exp(-t * 18) * 0.6))
def riser(d):
    t = tt(d); f = 220 * 2 ** (t / d * 2.3)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * 0.25
    return x + filt(rng.standard_normal(len(t)), "bandpass", (1500, 6000)) * (t / d) ** 2.2 * 0.45

# ---------------- arranjo
PROG = [(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]  # Am F C G
def secao(t):
    if t < 2.0: return "intro"
    if t < D1: return "build"
    if t < 4.6: return "drop"
    if t < 11.9: return "groove"
    if t < D2: return "build"
    if t < CTA - 0.04: return "drop"
    if t < END: return "groove"
    return "fim"

beats = [G0 + n * B for n in range(int((END - G0) / B) + 1)]
K, C = kick(), clap()
side = np.ones(N)
padL, padR, bas = np.zeros(N), np.zeros(N), np.zeros(N)
for n, bt in enumerate(beats):
    sc = secao(bt)
    root, chord = PROG[(n // 4) % 4]
    fs = [note(m) for m in chord]
    if sc in ("intro", "groove", "drop"):
        i = int(bt * SR); t = np.arange(min(int(B * SR), N - i)) / SR
        side[i:i + len(t)] = 1 - 0.78 * np.exp(-t * 11)
        add(K, bt, 1.1 if sc == "drop" else 0.95)
        add(hat(), bt + B / 2, 0.6 if sc == "intro" else 0.72, pan=0.25)
        for k in range(4): add(shaker(), bt + k * B / 4, 0.5 if k % 2 else 0.25, pan=-0.35)
        if sc != "intro" and n % 2 == 1: add(C, bt, 0.65, pan=-0.05)
        if sc != "intro" and n % 4 == 3: add(hat(True), bt + B / 2, 0.4, pan=0.3)
        # baixo rolando no contratempo
        for off, m in ((0.5, 0), (0.75, 12 if (n // 4) % 2 else 0)):
            x = bass_note(note(root + m), 0.12); add(x, bt + off * B, 0.6, bl=bas, br=np.zeros(N))
        if sc in ("intro", "groove"):   # stabs no contratempo
            for off in ((0.5, 0.75) if sc == "groove" else (0.5,)):
                l, r = supersaw(fs, 0.22, voices=5, spread=0.008); env = np.exp(-tt(0.22) * 16)
                add_st(l * env * 0.55, r * env * 0.55, bt + off * B, 1.0, padL, padR)
        if sc == "drop" and n % 4 == 0:   # acorde largo + 808 a cada compasso
            l, r = supersaw(fs + [f * 2 for f in fs[:2]], 4 * B, voices=9, spread=0.018)
            add_st(l * 0.6, r * 0.6, bt, 1.0, padL, padR)
            for s in (0.0, 1.5 * B, 3 * B): add(sub808(note(root - 12), 0.7), bt + s, 0.55)
    elif sc == "build":   # caixa acelerando
        add(C, bt, 0.35); add(C, bt + B / 2, 0.42)
        if bt + B >= D1 - 0.01 or bt + B >= D2 - 0.01:
            for k in range(4): add(C, bt + k * B / 4, 0.5 + 0.05 * k)

# drops que não começam no início de compasso: força o acorde no próprio drop
for dt in (D1, D2):
    root, chord = PROG[0]; fs = [note(m) for m in chord]
    l, r = supersaw(fs + [f * 2 for f in fs[:2]], 4 * B, voices=9, spread=0.018)
    add_st(l * 0.5, r * 0.5, dt, 1.0, padL, padR)

ramp = np.clip(np.arange(N) / SR / 2.0, 0, 1) ** 1.5      # filtro abrindo no gancho
for buf in (padL, padR):
    buf[:] = filt(buf, "lowpass", 650) * (1 - ramp) + buf * ramp
padL = filt(filt(padL, "highpass", 180), "lowpass", 7000) * side
padR = filt(filt(padR, "highpass", 180), "lowpass", 7000) * side
L += padL * 0.55; R += padR * 0.55
add(bas * side, 0, 0.75)

# risers e impactos
add(riser(1.0), D1 - 1.0, 0.6); add(riser(1.0), D2 - 1.0, 0.75)
for dt in (D1, D2):
    add(impact(), dt, 1.0); add(crash(), dt, 0.8, pan=-0.15)
add(impact(), CTA, 0.7); add(crash(1.2), CTA, 0.5, pan=0.15)
add(impact(), END, 0.9); add(crash(1.4), END, 0.6)
l, r = supersaw([note(m) for m in (45, 57, 64, 69)], 0.6, voices=9, spread=0.02); env = np.exp(-tt(0.6) * 5)
add_st(l * env * 0.5, r * env * 0.5, END, 1.0, L, R)

# whoosh nos cortes de cena dos passos
for k, tc in enumerate((4.6, 5.6, 6.3, 8.1, 9.1, 10.1, 11.6)):
    add(whoosh(), tc - 0.25, 0.35, pan=-0.6 if k % 2 else 0.6)

# cliques de mouse e teclas (mesmos tempos da animação)
fx = np.zeros(N)
def click():
    n = int(0.025 * SR); t = np.arange(n) / SR
    return filt(rng.standard_normal(n), "bandpass", [1500, 6000]) * np.exp(-t * 300) + 0.4 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 500)
def key():
    n = int(0.02 * SR); t = np.arange(n) / SR
    return filt(rng.standard_normal(n), "bandpass", [2000, 8000]) * np.exp(-t * 380)
for tc in (3.22, 4.02, 4.80, 5.70, 7.60, 8.15, 9.20, 10.02, 11.68):
    add(click(), tc + OFF, 0.5, bl=fx, br=np.zeros(N))
for a, b in ((6.15, 6.85), (10.4, 11.15)):
    t0 = a + OFF
    while t0 < b + OFF:
        add(key(), t0, 0.22 + 0.1 * rng.random(), bl=fx, br=np.zeros(N)); t0 += 0.045 + 0.03 * rng.random()
fx /= 1.414

# master
L = filt(L, "highpass", 28); R = filt(R, "highpass", 28)
m = max(np.abs(L).max(), np.abs(R).max()); L /= m; R /= m
L += fx * 0.55; R += fx * 0.55
fade = np.ones(N); i0 = int((END + 0.15) * SR); fade[i0:] = np.linspace(1, 0, N - i0) ** 1.5
L *= fade; R *= fade
m = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(1.3 * L / m) / np.tanh(1.3) * 10 ** (-1.5 / 20); R = np.tanh(1.3 * R / m) / np.tanh(1.3) * 10 ** (-1.5 / 20)
os.makedirs("audio", exist_ok=True)
wavfile.write("audio/trilha_house.wav", SR, (np.stack([L, R], 1) * 32767).astype(np.int16))
print("audio/trilha_house.wav %.1f s" % (N / SR))
