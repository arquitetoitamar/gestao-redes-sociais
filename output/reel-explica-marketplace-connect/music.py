"""Trilha sintetizada (sem direitos de terceiros): pulso eletrônico leve em Lá menor,
120 BPM, com subida de ruído e impacto em cada tela de palavra. Saída: audio/musica.wav"""
import json
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
TL = json.load(open("build/timeline.json"))
TOTAL = TL["total"] + 0.3
N = int(TOTAL * SR)
BEAT = 0.5
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR
S = {s["id"]: s for s in TL["scenes"]}
GROOVE_IN = S["s1"]["start"]
END = S["s7"]["start"]
HITS = [s["start"] for s in TL["scenes"] if s["kind"] == "inter"]

def lp(x, f, order=2): return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += g * x

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.sin(ph * 2) * np.exp(-t * 30)

def hat():
    n = int(0.06 * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * 70)

def saw(f, n, harm=8):
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, harm + 1))

def impact():
    n = int(1.4 * SR); t = np.arange(n) / SR
    f = 38 + 50 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    noise = lp(rng.standard_normal(n), 2500) * np.exp(-t * 9) * 0.5
    return boom + noise

def riser(d=0.55):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n)
    seg = n // 12
    for k in range(12):  # banda subindo em degraus curtos
        a, b = k * seg, (k + 1) * seg if k < 11 else n
        c = 600 * (2 ** (k / 3.2))
        out[a:b] = bp(x, c, min(c * 1.8, 20000))[a:b]
    return out * (t / d) ** 2.2

mix_drums = np.zeros(N); mix_bass = np.zeros(N); mix_pad = np.zeros(N); mix_fx = np.zeros(N)

# bateria: 4 no chão a partir da cena 1, pausa de meio tempo antes de cada impacto
K, H = kick(), hat()
b = 0
while b * BEAT < END + 2 * BEAT:
    tb = b * BEAT
    if tb >= GROOVE_IN - 0.01 and not any(h - 0.5 < tb < h for h in HITS):
        add(mix_drums, K, tb, 0.9 if tb < END else 0.6)
        add(mix_drums, H, tb + BEAT / 2, 0.22)
        if b % 2: add(mix_drums, H, tb + BEAT * 0.75, 0.1)
    elif tb < GROOVE_IN and b % 2 == 0:
        add(mix_drums, lp(K, 300), tb, 0.35)  # pulso abafado no gancho
    b += 1

# progressão Am - F - C - G, dois tempos por acorde... um compasso (4 tempos) por acorde
CH = [(110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 220.0, 261.63]),
      (130.81, [196.0, 261.63, 329.63]), (98.0, [196.0, 246.94, 293.66])]
bar = 4 * BEAT
nb = int(TOTAL / bar) + 1
for i in range(nb):
    t0 = i * bar
    root, notes = CH[i % 4]
    # pad: serra suave, ataque lento
    n = int(bar * SR) + int(0.6 * SR)
    tt = np.arange(n) / SR
    env = np.minimum(1, tt / 0.35) * np.exp(-np.maximum(0, tt - bar) * 6)
    pad = sum(saw(f * d, n, 6) for f in notes for d in (0.997, 1.003)) * env
    add(mix_pad, pad, t0, 0.06)
    # baixo em colcheias com "bombeio"
    if t0 >= GROOVE_IN - 0.01:
        for k in range(8):
            ts = t0 + k * BEAT / 2
            if any(h - 0.5 < ts < h for h in HITS) or ts >= END + BEAT: continue
            m = int(BEAT / 2 * SR); tm = np.arange(m) / SR
            note = saw(root / 2 if k % 2 == 0 else root, m, 5) * np.minimum(1, tm / 0.03) * np.exp(-tm * 5)
            add(mix_bass, note, ts, 0.35)

mix_bass = lp(mix_bass, 420)
mix_pad = lp(mix_pad, 1800)
# "bombeio" do pad junto do bumbo
duck = np.ones(N)
for b in range(int(TOTAL / BEAT) + 1):
    tb = b * BEAT
    if tb < GROOVE_IN: continue
    i = int(tb * SR); m = min(int(0.3 * SR), N - i)
    if m > 0: duck[i:i + m] = np.minimum(duck[i:i + m], 0.45 + 0.55 * (np.arange(m) / m))
mix_pad *= duck

# efeitos: subida antes e impacto em cada tela de palavra, na virada do gancho e no final
R, I = riser(), impact()
for h in HITS + [END]:
    add(mix_fx, R, h - 0.55, 0.18)
    add(mix_fx, I, h, 0.55)
add(mix_fx, I, S["s0"]["cues"]["operasse"] - 0.1, 0.45)
add(mix_fx, R, S["s0"]["cues"]["operasse"] - 0.65, 0.12)

mix = mix_drums + mix_bass + mix_pad + mix_fx
# fade final
fo = int(2.5 * SR)
mix[-fo:] *= np.linspace(1, 0, fo) ** 1.5
fi = int(0.05 * SR)
mix[:fi] *= np.linspace(0, 1, fi)
mix = mix / np.max(np.abs(mix)) * 0.8
st = np.stack([mix, np.roll(mix, int(0.012 * SR)) * 0.96 + mix * 0.04], axis=1)  # leve abertura estéreo
wavfile.write("audio/musica.wav", SR, (st * 32767).astype(np.int16))
print("musica ok", round(TOTAL, 2), "s")
