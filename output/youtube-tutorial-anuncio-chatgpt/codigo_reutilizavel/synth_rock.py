"""Original driving rock intro (distorted guitars + bass + drums), 150 BPM, E minor. Pure numpy.
usage: synth_rock.py <out.wav> [bars=5]   (bars of 1.6 s; last bar rings out with crash)
"""
import sys
import numpy as np

SR = 44100
BPM = 150
BEAT = 60.0 / BPM            # 0.4 s
STEP = BEAT / 2              # 8th note = 0.2 s
BAR = BEAT * 4               # 1.6 s
rng = np.random.default_rng(7)

def ks(freq, dur, decay=0.997, bright=0.5):
    """Karplus-Strong plucked string."""
    n = int(SR * dur)
    N = max(2, int(SR / freq))
    buf = (rng.random(N) * 2 - 1)
    buf = np.convolve(buf, [0.5, 0.5], mode="same") if bright < 0.5 else buf
    out = np.empty(n + N)
    out[:N] = buf
    pos = N
    prev = buf
    while pos < n:
        nxt = decay * 0.5 * (prev + np.roll(prev, 1))
        out[pos:pos + N] = nxt
        prev = nxt
        pos += N
    return out[:n]

def hp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x); px = 0.0; py = 0.0
    # vectorised one-pole via cumulative trick is awkward; use simple loop on decimated blocks
    for i in range(len(x)):
        py = a * (py + x[i] - px); px = x[i]; y[i] = py
    return y

def dist(x, gain=9.0):
    y = np.tanh(gain * x)
    y = np.tanh(2.2 * y + 0.15 * y * y)          # second stage + a bit of asymmetry
    return y

def env(n, atk=0.002, rel=0.05):
    e = np.ones(n)
    a = int(SR * atk); r = int(SR * rel)
    if a > 0: e[:a] = np.linspace(0, 1, a)
    if r > 0: e[-r:] *= np.linspace(1, 0, r)
    return e

def power_chord(root_hz, dur, muted):
    dec = 0.955 if muted else 0.9975
    parts = [ks(root_hz, dur, dec), 0.9 * ks(root_hz * 1.4983, dur, dec), 0.8 * ks(root_hz * 2, dur, dec)]
    x = sum(parts)
    x = x / (np.max(np.abs(x)) + 1e-9)
    if muted:
        x *= np.exp(-np.arange(len(x)) / (SR * 0.06))
    return x * env(len(x), 0.001, 0.02 if muted else 0.06)

def kick(dur=0.32):
    n = int(SR * dur); t = np.arange(n) / SR
    f = 42 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    click = np.exp(-t * 400) * 0.6
    return (np.sin(ph) * np.exp(-t * 9) + click)

def snare(dur=0.28):
    n = int(SR * dur); t = np.arange(n) / SR
    noise = rng.standard_normal(n) * np.exp(-t * 18)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 26) * 0.7
    return 0.85 * noise + tone

def hat(dur=0.06, open_=False):
    d = 0.35 if open_ else dur
    n = int(SR * d); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = noise - np.roll(noise, 1)             # crude high-pass
    return noise * np.exp(-t * (14 if open_ else 90)) * 0.2

def crash(dur=2.2):
    n = int(SR * dur); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = noise - 0.9 * np.roll(noise, 1)
    return noise * np.exp(-t * 2.6) * 0.3

def bass_note(hz, dur):
    n = int(SR * dur); t = np.arange(n) / SR
    saw = 2 * ((t * hz) % 1) - 1
    x = np.tanh(2.5 * (0.6 * saw + 0.6 * np.sin(2 * np.pi * hz * t)))
    return x * np.exp(-t * 3.0) * env(n, 0.002, 0.03)

def put(track, snd, at, gain=1.0):
    i = int(at * SR)
    if i >= len(track): return
    j = min(len(track), i + len(snd))
    track[i:j] += gain * snd[:j - i]

def render(out, bars=5):
    total = bars * BAR + 1.6
    n = int(total * SR)
    gL = np.zeros(n); gR = np.zeros(n); bass = np.zeros(n); drums = np.zeros(n)
    E2 = 82.41
    semis = lambda s: E2 * 2 ** (s / 12)
    # riff: (bar, step, semitone, muted, length in steps)
    riff = []
    for b, pat in enumerate([
        [(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (3, 0, 1), (0, 0, 1)],
        [(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (5, 0, 1), (3, 0, 1)],
        [(0, 0, 8)] + [None] * 7,
        [(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (7, 0, 1), (5, 0, 1), (3, 0, 1), (0, 0, 1)],
        [(0, 0, 8)] + [None] * 7]):
        if b >= bars: break
        for s, item in enumerate(pat):
            if item is None: continue
            semi, _, length = item
            # muted chugs on 1..4 of the 8ths except accents (semi != 0 or step 0)
            muted = (b in (0, 1, 3)) and not (s in (0, 6, 7) or (b == 3 and s >= 4))
            riff.append((b, s, semi, muted, length))
    for b, s, semi, muted, length in riff:
        t0 = b * BAR + s * STEP
        dur = 0.19 if muted else (STEP * length if length > 1 else 0.36)
        if b == bars - 1: dur = 1.9
        ch = power_chord(semis(semi), dur, muted)
        ch = dist(ch)
        ch = np.convolve(ch, np.ones(7) / 7, mode='same')          # cabinet-style roll-off
        # double-tracked stereo (slight delay + detune feel)
        put(gL, ch, t0, 0.55); put(gR, ch, t0 + 0.011, 0.55)
        put(gL, ch, t0 + 0.017, 0.25); put(gR, ch, t0, 0.25)
        bn = bass_note(semis(semi) / 2, dur if not muted else 0.18)
        put(bass, bn, t0, 0.9)
    # drums (16 steps per bar)
    K = [[1,0,0,0, 0,0,1,0, 1,0,0,0, 0,0,1,0]] * 5
    S = [[0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0]] * 5
    for b in range(bars):
        base = b * BAR
        sx = BAR / 16
        for i in range(16):
            if b == bars - 1 and i > 0: break
            if K[b][i] and b != 2: put(drums, kick(), base + i * sx, 1.0)
            if S[b][i] and b not in (2,): put(drums, snare(), base + i * sx, 0.9)
            if b in (0, 1):
                if i % 2 == 0: put(drums, hat(), base + i * sx, 0.7)
            elif b == 3:
                put(drums, hat(), base + i * sx, 0.6)
        if b == 2:   # build bar: kick pulses + snare roll into the reveal
            for i in range(0, 16, 2): put(drums, kick(), base + i * sx, 0.9)
            for i in range(8, 16): put(drums, snare(), base + i * sx, 0.55 + 0.03 * (i - 8))
        if b == 3:   # fill on the last beat
            for i in range(12, 16): put(drums, snare(), base + i * sx, 0.9)
        if b in (0, 2, 4): put(drums, crash(), base, 0.9)
        if b == bars - 1: put(drums, kick(0.5), base, 1.0)
    # mix
    L = 0.9 * gL + 0.55 * bass + 0.9 * drums
    R = 0.9 * gR + 0.55 * bass + 0.9 * drums
    m = np.max(np.abs(np.stack([L, R])))
    L, R = L / m * 0.85, R / m * 0.85
    st = np.stack([L, R], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    import wave
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print("ok", out, "dur", round(total, 2))

if __name__ == "__main__":
    render(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 5)
