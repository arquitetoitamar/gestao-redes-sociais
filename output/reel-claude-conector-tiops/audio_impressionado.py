"""Trilha original "de impressionado": coral "aaah" angelical + brilhos nas revelações,
base mágica de sininhos (glockenspiel) e batida leve nos passos. Sem música de terceiros.
Saída: audio/trilha_impressionado.wav (já com os cliques de mouse/teclas)."""
import os
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000; TOTAL = 16.3; N = int(TOTAL * SR)
rng = np.random.default_rng(21)
def filt(x, kind, f, order=2): return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)
def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i < 0: return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += g * x
def hz(n):  # nota MIDI
    return 440.0 * 2 ** ((n - 69) / 12)

# ---------- coral "aaah" (síntese de formantes)
def voice(f, dur, att=0.25, rel=0.8, vib=5.2):
    n = int(dur * SR); t = np.arange(n) / SR
    fv = f * (1 + 0.006 * np.sin(2 * np.pi * vib * t + rng.random() * 6))
    ph = 2 * np.pi * np.cumsum(fv) / SR
    src = sum(np.sin(k * ph) / k for k in range(1, 30))          # serra rica em harmônicos
    out = sum(g * filt(src, "band", [fc * 0.85, fc * 1.15]) for fc, g in ((800, 1.0), (1150, 0.6), (2900, 0.25), (3300, 0.15)))
    env = np.minimum(1, t / att) * np.minimum(1, np.maximum(0, (dur - t) / rel))
    return out * env
def choir(notes, dur, att=0.25, rel=0.9):
    return sum(voice(hz(m) * (1 + d), dur, att, rel) for m in notes for d in (-0.004, 0.0, 0.005))

# ---------- sininhos
def bell(f, dur=1.2, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    return g * (np.sin(2 * np.pi * f * t) * np.exp(-t * 4) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 9)
                + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 16))
def sparkle(t0, dur=0.9, n=14, base=84):
    out = np.zeros(int((dur + 1.2) * SR))
    for i in range(n):
        m = base + [0, 2, 4, 7, 9, 12, 14, 16][rng.integers(0, 8)]
        add(out, bell(hz(m), 1.0, 0.25), (i / n) * dur)
    return out

def riser(d):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n)
    seg = n // 12
    for k in range(12):
        a, b = k * seg, (k + 1) * seg if k < 11 else n
        c = 400 * 2 ** (k / 2.6); out[a:b] = filt(x, "band", [c, min(c * 1.8, 20000)])[a:b]
    return out * (t / d) ** 2
def boom():
    n = int(1.4 * SR); t = np.arange(n) / SR
    f = 42 + 60 * np.exp(-t * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3)

choirbus = np.zeros(N); bells = np.zeros(N); beat = np.zeros(N); fx = np.zeros(N)

# gancho (0–2.5): tensão curiosa, sininhos espaçados subindo + riser
for i, m in enumerate([72, 76, 79, 83, 84, 88]):
    add(bells, bell(hz(m), 1.3, 0.35), 0.15 + i * 0.33)
add(fx, riser(1.2), 1.3, 0.25)

# revelação 1 (2.5): "AAAH" em Dó maior com 9ª + brilho + grave
add(choirbus, choir([60, 64, 67, 74, 76], 2.2, att=0.08, rel=1.4), 2.5, 1.0)
add(bells, sparkle(2.5, 0.8, 16, 84), 2.5, 1.0)
add(fx, boom(), 2.5, 0.5)

# passos (3.2–10.3): base mágica 120 BPM — arpejo de sininhos em semicolcheias, bumbo leve, shaker
B = 0.5; t = 3.2
PROG = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67]]   # Cmaj7 Am7 Fmaj7 G
step = 0
while t < 10.25:
    ch = PROG[(step // 16) % 4]
    seq = ch + [ch[0] + 12, ch[2] + 12, ch[1] + 12, ch[3]]
    add(bells, bell(hz(seq[step % 8] + 12), 0.6, 0.18), t)
    if step % 4 == 0:
        n = int(0.3 * SR); tt = np.arange(n) / SR; f = 50 + 90 * np.exp(-tt * 30)
        add(beat, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9), t, 0.5)
    if step % 2 == 1:
        n = int(0.04 * SR); add(beat, filt(rng.standard_normal(n), "high", 7000) * np.exp(-np.arange(n) / SR * 120), t, 0.12)
    if step % 16 == 0:  # pad de coral suave sustentando o acorde
        add(choirbus, choir([m + 12 for m in ch[:3]], 4 * B * 4 * 0.5 + 0.6, att=0.4, rel=0.6), t, 0.25)
    t += B / 4 * 2; step += 1   # colcheias (mais leve)

# revelação 2 (10.3, Claude trabalhando): riser + "AAAAH" maior e mais alto
add(fx, riser(0.9), 9.4, 0.3)
add(choirbus, choir([62, 66, 69, 74, 78, 81], 3.3, att=0.06, rel=1.2), 10.3, 1.25)   # Ré maior (sobe um tom = "uau")
add(bells, sparkle(10.3, 1.0, 20, 86), 10.3, 1.1)
add(fx, boom(), 10.3, 0.6)
# brilhos quando aparecem os resultados
add(bells, sparkle(12.55, 0.5, 8, 91), 12.55, 0.7)

# chamada final (13.8): acorde resolvido + brilho final
add(choirbus, choir([62, 69, 74, 78], 2.5, att=0.1, rel=1.6), 13.8, 0.8)
add(bells, sparkle(13.8, 0.6, 10, 86), 13.8, 0.8)
add(fx, boom(), 13.8, 0.4)

# cliques e teclas (mesmos tempos da animação)
def click():
    n = int(0.025 * SR); tt = np.arange(n) / SR
    return filt(rng.standard_normal(n), "band", [1500, 6000]) * np.exp(-tt * 300) + 0.4 * np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 500)
def key():
    n = int(0.02 * SR); tt = np.arange(n) / SR
    return filt(rng.standard_normal(n), "band", [2000, 8000]) * np.exp(-tt * 380)
for tc in (3.22, 4.02, 4.80, 5.70, 7.60, 8.15, 9.20, 10.02, 11.68):
    add(fx, click(), tc, 0.45)
for (a, b) in ((6.15, 6.85), (10.4, 11.15)):
    tt = a
    while tt < b:
        add(fx, key(), tt, 0.2 + 0.1 * rng.random()); tt += 0.045 + 0.03 * rng.random()

# reverb no coral e nos sininhos
ir_n = int(2.2 * SR); ir_t = np.arange(ir_n) / SR
def rev(x, seed):
    r = np.random.default_rng(seed); ir = filt(r.standard_normal(ir_n), "low", 7000) * np.exp(-ir_t * 2.4)
    return fftconvolve(x, ir)[:N]
choirbus /= np.max(np.abs(choirbus)); bells /= np.max(np.abs(bells))
L = choirbus * 0.55 + bells * 0.45 + beat * 0.6 + fx + rev(choirbus * 0.5 + bells * 0.4, 1) * 0.035
R = choirbus * 0.55 + bells * 0.45 + beat * 0.6 + fx + rev(choirbus * 0.5 + bells * 0.4, 2) * 0.035
st = np.stack([filt(L, "high", 30), filt(R, "high", 30)], 1)
fo = int(1.2 * SR); st[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
st = np.tanh(1.2 * st / np.max(np.abs(st))) * 0.85 / np.tanh(1.2)
os.makedirs("audio", exist_ok=True)
wavfile.write("audio/trilha_impressionado.wav", SR, (st * 32767).astype(np.int16))
print("ok")
