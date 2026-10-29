"""Trilha da abertura (12,5 s), criada do zero, sem direitos de terceiros.

Tech house / future bass a 120 BPM (1 batida = 15 quadros a 30 fps), Lá menor:
  0-4 s   groove com filtro abrindo (kick, hats, baixo rolando, acordes)
  4-8 s   groove cheio + palmas; riser e caixa acelerando no compasso 4; kick some na última batida
  8 s     DROP na cartela: impacto (sub + crash), supersaw largo com sidechain, 808
  12 s    batida final e cauda
Whoosh em cada corte de cena (1, 2, ... 7 s). Saída: trilha.wav (48 kHz, estéreo).
"""
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
BPM = 120
B = 60 / BPM            # 0,5 s
DUR = 12.6
N = int(DUR * SR)
DROP = 8.0
END = 12.0
rng = np.random.default_rng(7)

L = np.zeros(N); R = np.zeros(N)


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)


def add(x, t0, g=1.0, pan=0.0):
    """mono x at t0 (s), pan -1..1"""
    i = int(round(t0 * SR))
    if i >= N:
        return
    if i < 0:
        x = x[-i:]; i = 0
    x = x[: N - i]
    gl, gr = g * np.sqrt((1 - pan) / 2) * 1.414, g * np.sqrt((1 + pan) / 2) * 1.414
    L[i:i + len(x)] += gl * x
    R[i:i + len(x)] += gr * x


def add_st(xl, xr, t0, g=1.0):
    i = int(round(t0 * SR))
    n = min(len(xl), N - i)
    L[i:i + n] += g * xl[:n]
    R[i:i + n] += g * xr[:n]


def tt(d):
    return np.arange(int(d * SR)) / SR


def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------ instrumentos
def kick():
    t = tt(0.42)
    f = 46 + 120 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = filt(rng.standard_normal(len(t)), "highpass", 2500) * np.exp(-t * 400) * 0.35
    return np.tanh(1.6 * (body + click))


def clap():
    t = tt(0.32)
    n = rng.standard_normal(len(t))
    env = np.zeros(len(t))
    for k, o in enumerate((0.0, 0.011, 0.022)):
        i = int(o * SR)
        env[i:] += np.exp(-(t[i:] - o) * (95 if k < 2 else 16))
    return filt(n, "bandpass", (900, 4200)) * env * 0.8


def hat(open_=False):
    t = tt(0.22 if open_ else 0.06)
    return filt(rng.standard_normal(len(t)), "highpass", 7500) * np.exp(-t * (14 if open_ else 70)) * 0.5


def shaker():
    t = tt(0.05)
    return filt(rng.standard_normal(len(t)), "bandpass", (5000, 11000)) * np.sin(np.pi * t / t[-1]) * 0.22


def saw(f, d, detune=0.0):
    t = tt(d)
    ph = (f * (1 + detune) * t + rng.random()) % 1.0
    return 2 * ph - 1


def supersaw(fs, d, voices=7, spread=0.012):
    """acorde largo: retorna (l, r)"""
    l = np.zeros(int(d * SR)); r = np.zeros(int(d * SR))
    for f in fs:
        for v in range(voices):
            dt = spread * (v / (voices - 1) - 0.5)
            s = saw(f, d, dt)
            p = (v / (voices - 1)) * 2 - 1
            l += s * (1 - p) * 0.5
            r += s * (1 + p) * 0.5
    k = 1.0 / (len(fs) * voices * 0.5)
    return l * k, r * k


def bass_note(f, d):
    t = tt(d)
    x = 0.7 * np.sin(2 * np.pi * f * t) + 0.35 * saw(f, d)
    x = filt(x, "lowpass", 900)
    env = np.minimum(1, t / 0.004) * np.exp(-t * 7)
    return np.tanh(2.2 * x * env)


def sub808(f, d):
    t = tt(d)
    fr = f * (1 + 0.6 * np.exp(-t * 40))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.tanh(1.8 * np.sin(ph)) * np.minimum(1, t / 0.003) * np.exp(-t * 1.6)


def whoosh(d=0.42):
    t = tt(d)
    n = rng.standard_normal(len(t))
    lo = filt(n, "bandpass", (500, 1800)); hi = filt(n, "bandpass", (1800, 7000))
    a = t / d
    x = lo * (1 - a) + hi * a
    env = np.sin(np.pi * a) ** 2
    return x * env * 0.5


def crash(d=1.8):
    t = tt(d)
    return filt(rng.standard_normal(len(t)), "highpass", 3800) * np.exp(-t * 2.6) * 0.55


def impact():
    t = tt(1.6)
    f = 32 + 55 * np.exp(-t * 4)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    thud = filt(rng.standard_normal(len(t)), "lowpass", 300) * np.exp(-t * 18) * 0.6
    return np.tanh(1.5 * (boom + thud))


# ------------------------------------------------------------ arranjo
CH = [  # (raiz do baixo, notas do acorde) por compasso de 2 s
    (45, [57, 60, 64, 69]),   # Am
    (41, [53, 57, 60, 65]),   # F
    (48, [55, 60, 64, 67]),   # C
    (43, [55, 59, 62, 67]),   # G
    (45, [57, 60, 64, 69, 72]),  # Am (drop)
    (41, [53, 57, 60, 65, 69]),  # F  (drop)
]

beats = np.arange(0, END, B)
K = kick(); C = clap()

# sidechain (bombeia em todo kick)
side = np.ones(N)
for bt in beats:
    if 7.5 <= bt < DROP:
        continue
    i = int(bt * SR); t = np.arange(min(int(B * SR), N - i)) / SR
    side[i:i + len(t)] = 1 - 0.78 * np.exp(-t * 11)

# bus de acordes e baixo (para filtrar e aplicar sidechain)
padL = np.zeros(N); padR = np.zeros(N); bas = np.zeros(N)
for bar, (root, chord) in enumerate(CH):
    t0 = bar * 2.0
    if t0 >= END:
        break
    fs = [note(m) for m in chord]
    if t0 < DROP:
        # stabs no contratempo (pluck)
        for s in np.arange(t0, t0 + 2.0, B):
            for off in (0.25, 0.375) if bar >= 2 else (0.25,):
                l, r = supersaw(fs, 0.22, voices=5, spread=0.008)
                env = np.exp(-tt(0.22) * 16)
                i = int((s + off) * SR); n = min(len(env), N - i)
                padL[i:i + n] += l[:n] * env[:n] * 0.55; padR[i:i + n] += r[:n] * env[:n] * 0.55
    else:
        l, r = supersaw(fs + [f * 2 for f in fs[:2]], 2.0, voices=9, spread=0.018)
        env = np.minimum(1, tt(2.0) / 0.01)
        i = int(t0 * SR); n = min(len(env), N - i)
        padL[i:i + n] += l[:n] * env[:n] * 0.6; padR[i:i + n] += r[:n] * env[:n] * 0.6
    # baixo rolando no contratempo (tech house)
    for s in np.arange(t0, t0 + 2.0, B):
        if 7.5 <= s < DROP:
            continue
        for off, m in ((0.25, 0), (0.375, 12 if bar % 2 else 0)):
            x = bass_note(note(root + m), 0.12)
            i = int((s + off) * SR); n = min(len(x), N - i)
            bas[i:i + n] += x[:n] * 0.6

# filtro abrindo nos 4 primeiros segundos (mistura entre versão abafada e cheia)
ramp = np.clip(np.arange(N) / SR / 4.0, 0, 1) ** 1.5
for buf in (padL, padR):
    lp = filt(buf, "lowpass", 650)
    buf[:] = lp * (1 - ramp) + buf * ramp
padL = filt(filt(padL, "highpass", 180), "lowpass", 7000); padR = filt(filt(padR, "highpass", 180), "lowpass", 7000)
padL *= side; padR *= side; bas *= side
L += padL * 0.55; R += padR * 0.55
add(bas, 0, 0.75)

# bateria
for bt in beats:
    if 7.5 <= bt < DROP:
        continue
    add(K, bt, 1.15 if bt >= DROP else 0.95)
    add(hat(), bt + 0.25, 0.55 if bt < 2 else 0.7, pan=0.25)
    if bt >= 2.0:
        if int(round(bt / B)) % 2 == 1:
            add(C, bt, 0.65, pan=-0.05)
        if int(round(bt / B)) % 4 == 3:
            add(hat(True), bt + 0.25, 0.4, pan=0.3)
    for k in range(4):
        add(shaker(), bt + k * B / 4, 0.5 if k % 2 else 0.25, pan=-0.35)

# 808 nas batidas fortes do drop
for bar, (root, _) in enumerate(CH[4:], start=4):
    for s in (0.0, 0.75, 1.5):
        add(sub808(note(root - 12), 0.7), bar * 2.0 + s, 0.55)

# compasso 4 (6-8 s): riser + caixa acelerando
t = tt(2.0)
f = 220 * 2 ** (t / 2.0 * 2.3)
riser = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / 2.0) ** 2 * 0.25
nz = rng.standard_normal(len(t))
riser += (filt(nz, "bandpass", (1500, 6000)) * (t / 2.0) ** 2.2) * 0.45
add(riser, 6.0, 0.8)
for k in range(8):
    add(C, 6.0 + k * 0.25, 0.25 + 0.04 * k)
for k in range(8):
    add(C, 7.0 + k * 0.125, 0.45 + 0.04 * k)
rc = crash(1.0)[::-1] * np.linspace(0, 1, int(1.0 * SR)) ** 2
add(rc, DROP - 1.0, 0.7, pan=0.1)

# drop e final
add(impact(), DROP, 1.0); add(crash(), DROP, 0.8, pan=-0.15)
add(impact(), END, 1.0); add(crash(1.4), END, 0.7, pan=0.15)
l, r = supersaw([note(m) for m in (45, 57, 64, 69)], 0.6, voices=9, spread=0.02)
env = np.exp(-tt(0.6) * 5)
add_st(l * env * 0.5, r * env * 0.5, END)

# whoosh nos cortes de cena (1..7 s), alternando o lado
for k in range(1, 8):
    add(whoosh(), k * 1.0 - 0.3, 0.45, pan=-0.6 if k % 2 else 0.6)

# master: corta graves inúteis, satura de leve, cauda e normaliza
L = filt(L, "highpass", 28); R = filt(R, "highpass", 28)
fade = np.ones(N); i0 = int((END + 0.15) * SR)
fade[i0:] = np.linspace(1, 0, N - i0) ** 1.5
L *= fade; R *= fade
m = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(1.3 * L / m) / np.tanh(1.3); R = np.tanh(1.3 * R / m) / np.tanh(1.3)
pk = 10 ** (-1.5 / 20)
L *= pk; R *= pk
wavfile.write("trilha.wav", SR, (np.stack([L, R], 1) * 32767).astype(np.int16))
print("trilha.wav %.1f s" % (N / SR))
