#!/usr/bin/env python3
"""Trilha sintetizada (sem direitos de terceiros) para a animação de 9 s: pulso a 120 BPM,
'whoosh' na varredura, toques nos três checks e impacto no CTA. Saída: audio/trilha.wav"""
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, TOTAL = 48000, 9.0
N = int(TOTAL * SR)
rng = np.random.default_rng(4)
AQUI = os.path.dirname(os.path.abspath(__file__))


def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)


def add(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    x = x[: max(0, len(buf) - i)]
    buf[i:i + len(x)] += g * x


def kick():
    n = int(.4 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(48 + 90 * np.exp(-t * 30)) / SR
    return np.sin(ph) * np.exp(-t * 8)


def hat():
    n = int(.05 * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 8000) * np.exp(-t * 80)


def tom(f, d=.25, dec=10):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * dec)


def whoosh(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    env = np.sin(np.pi * t / d) ** 2
    return lp(hp(rng.standard_normal(n), 800), 6000) * env


def pad(freqs, d):
    n = int(d * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.003 * t) for f in freqs)
    env = np.minimum(1, t / .8) * np.minimum(1, (d - t) / .8)
    return lp(x, 1800) * env / len(freqs)


mix = np.zeros(N)
add(mix, whoosh(1.2), 0.0, .25)
add(mix, pad([220, 261.6, 329.6], 5.3), 0.2, .10)           # Lá menor
add(mix, pad([174.6, 220, 261.6, 349.2], 3.9), 5.2, .12)    # Fá maior no CTA
beat = .5
t = 0.75
while t < TOTAL - .3:
    add(mix, kick(), t, .55)
    add(mix, hat(), t + beat / 2, .12)
    t += beat
for k, f in enumerate([880, 987.8, 1174.7]):                # três checks
    add(mix, tom(f, .3, 12), 2.6 + k * .55 + .2, .22)
add(mix, kick(), 5.3, .9)                                   # entrada do CTA
add(mix, whoosh(.5), 5.0, .2)
add(mix, tom(1318.5, .6, 5), 5.55, .18)
fade = np.ones(N); fn = int(.6 * SR); fade[-fn:] = np.linspace(1, 0, fn)
mix *= fade
mix = mix / np.max(np.abs(mix)) * .85
os.makedirs(os.path.join(AQUI, 'audio'), exist_ok=True)
wavfile.write(os.path.join(AQUI, 'audio', 'trilha.wav'), SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print('ok audio/trilha.wav')
