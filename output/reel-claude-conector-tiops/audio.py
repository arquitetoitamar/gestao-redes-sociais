"""Trilha original: pizzicato de suspense (cordas dedilhadas, Karplus-Strong), 150 BPM, Ré menor,
+ cliques de mouse e teclas nos momentos da animação. Sem música de terceiros.
Gera audio/trilha.wav (música + efeitos) e audio/efeitos.wav (só efeitos, para usar com áudio do Instagram)."""
import os
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000; TOTAL = 16.3; N = int(TOTAL * SR)
rng = np.random.default_rng(3)
os.makedirs("audio", exist_ok=True)

def filt(x, kind, f): return sosfilt(butter(2, f, kind, fs=SR, output="sos"), x)
def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += g * x

def pizz(f, dur=0.32, bright=0.5):
    n = int(dur * SR); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p) * 0.9
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * (0.993 + 0.004 * bright)
    env = np.exp(-np.arange(n) / SR * 9)
    return filt(out * env, "low", 1800 + 2500 * bright)

def note(name):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    o = int(name[-1]); k = names[name[:-1]]
    return 440.0 * 2 ** ((k - 9) / 12 + (o - 4))

E8 = 60 / 150 / 2   # colcheia
music = np.zeros(N)
# baixo dedilhado andando (furtivo), frase de 2 compassos
BASS = ["D2", None, "F2", None, "G#2", "A2", None, "F2", "D2", None, "A#1", None, "A1", None, "C#2", None]
HIGH = [None, "D4", None, "F4", None, None, "A4", None, None, "G#4", None, "A4", None, "F4", "E4", None]
t, k = 0.0, 0
while t < TOTAL - 2.2:
    b, h = BASS[k % 16], HIGH[k % 16]
    sec = t >= 2.5                                     # entra completo depois do gancho
    if b: add(music, pizz(note(b), 0.4, 0.3), t, 0.55)
    if h and sec: add(music, pizz(note(h), 0.28, 0.7), t, 0.32)
    if sec and k % 2 == 1: add(music, filt(rng.standard_normal(int(0.03 * SR)), "high", 7000) * np.exp(-np.arange(int(0.03 * SR)) / SR * 140), t, 0.06)
    t += E8; k += 1
# acorde final (dedilhado) na chamada
for i, nn in enumerate(["D3", "F3", "A3", "D4"]):
    add(music, pizz(note(nn), 1.4, 0.5), TOTAL - 2.3 + i * 0.05, 0.45)

# impacto grave nos cortes principais
def boom():
    n = int(0.9 * SR); tt = np.arange(n) / SR
    f = 40 + 50 * np.exp(-tt * 12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.5)
for tb in (2.5, 10.3, 13.8): add(music, boom(), tb, 0.5)

# efeitos: clique de mouse e teclas
fx = np.zeros(N)
def click():
    n = int(0.025 * SR); tt = np.arange(n) / SR
    return filt(rng.standard_normal(n), "band", [1500, 6000]) * np.exp(-tt * 300) + 0.4 * np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 500)
def key():
    n = int(0.02 * SR); tt = np.arange(n) / SR
    return filt(rng.standard_normal(n), "band", [2000, 8000]) * np.exp(-tt * 380)
for tc in (3.22, 4.02, 4.80, 5.70, 7.60, 8.15, 9.20, 10.02, 11.68):
    add(fx, click(), tc, 0.5)
for (a, b) in ((6.15, 6.85), (10.4, 11.15)):
    tt = a
    while tt < b:
        add(fx, key(), tt, 0.22 + 0.1 * rng.random()); tt += 0.045 + 0.03 * rng.random()

def save(x, path):
    x = x / max(1e-9, np.max(np.abs(x))) * 0.85
    st = np.stack([x, x], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
save(music * 0.8 + fx, "audio/trilha.wav")
save(fx, "audio/efeitos.wav")
print("ok")
