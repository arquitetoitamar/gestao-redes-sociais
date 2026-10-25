#!/usr/bin/env python3
"""Trilha original pra abertura. Sintetizada aqui — nenhuma amostra de terceiro,
então não existe direito autoral de outra pessoa pra reclamar."""
import numpy as np, wave

SR = 48000
BPM = 96
BAT = 60.0 / BPM          # 0.625 s
COMP = BAT * 4
DUR = COMP * 4            # 4 compassos = 10 s

def t(n):
    return np.arange(int(n * SR)) / SR

def env(n, a, d, s, r, sus=0.7):
    N = int(n * SR)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    ns = max(N - na - nd - nr, 0)
    return np.concatenate([
        np.linspace(0, 1, na, endpoint=False),
        np.linspace(1, sus, nd, endpoint=False),
        np.full(ns, sus),
        np.linspace(sus, 0, N - na - nd - ns)])

def nota(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)

def serra(f, n, det=0.0):
    x = t(n)
    y = np.zeros_like(x)
    for h in range(1, 13):                      # serra por soma de harmônicos
        y += np.sin(2 * np.pi * f * h * x) / h
    if det:
        for h in range(1, 13):
            y += 0.6 * np.sin(2 * np.pi * f * (1 + det) * h * x) / h
    return y / 3.0

def pb(x, fc):                                   # passa-baixa de 1 polo
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    ant = 0.0
    for i in range(len(x)):
        ant = (1 - a) * x[i] + a * ant
        y[i] = ant
    return y

mix = np.zeros(int(DUR * SR))

def soma(sig, ini, g=1.0):
    i = int(ini * SR)
    n = min(len(sig), len(mix) - i)
    if n > 0:
        mix[i:i + n] += g * sig[:n]

# ── Pad: Am - F - C - G, um acorde por compasso ───────────────────────────
ACORDES = [[57, 60, 64], [53, 57, 60], [48, 52, 55, 60], [55, 59, 62]]
for c, ac in enumerate(ACORDES):
    for m in ac:
        s = serra(nota(m), COMP, det=0.006) * env(COMP, 0.35, 0.3, 0, COMP - 0.75, 0.75)
        soma(pb(s, 1700), c * COMP, 0.16)

# ── Baixo: fundamental, duas por compasso ─────────────────────────────────
for c, raiz in enumerate([45, 41, 36, 43]):
    for k in (0, 2):
        f = nota(raiz)
        x = t(BAT * 1.6)
        s = (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x)) * env(BAT * 1.6, 0.01, 0.12, 0, 0.4, 0.55)
        soma(s, c * COMP + k * BAT, 0.30)

# ── Arpejo de pluck: colcheias subindo pelo acorde ────────────────────────
for c, ac in enumerate(ACORDES):
    desenho = [0, 1, 2, 1, 0, 1, 2, 1]
    for i, g in enumerate(desenho):
        m = ac[g % len(ac)] + 12
        d = BAT / 2
        x = t(d)
        s = (np.sin(2 * np.pi * nota(m) * x) * 0.7 +
             np.sin(2 * np.pi * nota(m + 12) * x) * 0.12) * env(d, 0.004, 0.09, 0, d - 0.1, 0.25)
        soma(s, c * COMP + i * d, 0.17)

# ── Bumbo nos tempos, caixa leve no 2 e 4, chimbal em colcheias ───────────
for c in range(4):
    for b in range(4):
        q = c * COMP + b * BAT
        x = t(0.26)
        f = 110 * np.exp(-28 * x) + 46
        soma(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.26, 0.001, 0.05, 0, 0.2, 0.3), q, 0.55)
        if b in (1, 3) and c > 0:
            n = np.random.default_rng(b + c).standard_normal(int(0.16 * SR))
            soma(n * env(0.16, 0.001, 0.04, 0, 0.11, 0.2), q, 0.07)
        for h in (0, 1):
            n = np.random.default_rng(100 + c * 8 + b * 2 + h).standard_normal(int(0.05 * SR))
            soma(n * env(0.05, 0.001, 0.015, 0, 0.03, 0.1), q + h * BAT / 2, 0.035 if h else 0.055)

# ── Subida de ruído entrando no último compasso ───────────────────────────
nr = int(COMP * 1.5 * SR)
rng = np.random.default_rng(7)
sub = rng.standard_normal(nr) * np.linspace(0, 1, nr) ** 2.5
sub = pb(sub, 5000) - pb(sub, 700)
soma(sub, COMP * 1.5, 0.22)

# ── Acabamento: fade, normaliza, estéreo com leve largura ────────────────
fade = int(0.5 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)
mix[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
mix /= np.abs(mix).max() / 0.89

atraso = int(0.011 * SR)
esq = mix.copy()
dir = np.concatenate([np.zeros(atraso), mix[:-atraso]]) * 0.55 + mix * 0.45
est = np.stack([esq, dir / max(np.abs(dir).max(), 1e-9) * 0.89], axis=1)

pcm = (est * 32767).astype('<i2')
with wave.open('trilha.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('trilha.wav', round(DUR, 2), 's', BPM, 'bpm')
