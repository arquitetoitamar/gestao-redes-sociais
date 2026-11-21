"""Áudio do Reel: voz com respiros inseridos + ambiente de sala (reverb curto e room tone) + trilha sintetizada
(sem direitos de terceiros) com ducking sob a voz + efeitos nas transições. Saída: trab/audio_final.wav (48 kHz estéreo)."""
import json, os, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve
AQUI = os.path.dirname(os.path.abspath(__file__)); T = lambda *p: os.path.join(AQUI, 'trab', *p)
SR = 48000; C = json.load(open(T('cronograma.json'))); DUR = C['duracao']; N = int(DUR * SR)
SFX = os.path.join(AQUI, '../../.agents/skills/media-use/audio/assets/sfx')
rng = np.random.default_rng(7)
lp = lambda x, f: sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)

def ler(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def add(buf, x, t0, g=1.0):
    i = int(t0 * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += g * x

# 1) voz com respiros nos cortes
src = ler(os.path.join(AQUI, 'videos', 'avatar.mp4'))
voz = np.zeros(N); cortes = [0.0] + [c for c, _ in C['pausas']] + [len(src) / SR]; desloc = 0.0
for k in range(len(cortes) - 1):
    a, b = cortes[k], cortes[k + 1]; pedaco = src[int(a * SR):int(b * SR)].copy()
    f = int(0.012 * SR); pedaco[:f] *= np.linspace(0, 1, f); pedaco[-f:] *= np.linspace(1, 0, f)
    add(voz, pedaco, a + desloc); desloc += C['pausas'][k][1] if k < len(C['pausas']) else 0
voz = hp(voz, 75)
# calor leve (+2 dB perto de 200 Hz) e presença suave
voz = voz + 0.25 * bp(voz, 150, 320) + 0.12 * bp(voz, 2500, 5000)
# 2) sala: resposta ao impulso sintética (RT ~0,35 s), mistura discreta
t = np.arange(int(0.45 * SR)) / SR
ir = rng.standard_normal(len(t)) * np.exp(-t / 0.075); ir = lp(ir, 5500); ir[: int(0.012 * SR)] *= 0.3
ir /= np.sqrt(np.sum(ir ** 2))
sala = fftconvolve(voz, ir)[:N]
voz_amb = voz + 0.16 * sala / (np.max(np.abs(sala)) + 1e-9) * np.max(np.abs(voz))
# compressão simples (RMS) para a voz não saltar
env = np.sqrt(np.maximum(lp(voz_amb ** 2, 8), 1e-9)); alvo = 0.12
voz_amb *= np.clip((alvo / (env + 1e-4)) ** 0.35, 0.6, 1.8)
room = lp(rng.standard_normal(N), 2500) * 0.0025

# 3) trilha 112 BPM: kick, chimbal, baixo e pad (Lá menor - Fá - Dó - Sol)
bpm = 112; beat = 60 / bpm; trilha = np.zeros(N)
def kick():
    tt = np.arange(int(.32 * SR)) / SR; f = 50 + 90 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def hat():
    tt = np.arange(int(.05 * SR)) / SR; return hp(rng.standard_normal(len(tt)), 7000) * np.exp(-tt * 70)
def nota(f, d, tipo='pad'):
    tt = np.arange(int(d * SR)) / SR
    if tipo == 'pad':
        x = sum(np.sin(2 * np.pi * f * m * tt + rng.uniform(0, 6)) / (i + 1) for i, m in enumerate([1, 1.003, 2, 0.997]))
        a = np.minimum(1, tt / .25) * np.minimum(1, (d - tt) / .35); return lp(x, 2200) * a
    x = np.sign(np.sin(2 * np.pi * f * tt)) * 0.6 + np.sin(2 * np.pi * f * tt); return lp(x, 300) * np.exp(-tt * 3) 
acordes = [(220, 261.6, 329.6), (174.6, 220, 261.6), (196 * 1.335, 196 * 1.682, 196 * 2), (196, 246.9, 293.7)]
baixo = [110, 87.3, 130.8, 98]
b = 0; tb = 0.0
while tb < DUR:
    compasso = int(b // 8) % 4
    if b % 8 == 0:
        for f in acordes[compasso]: add(trilha, nota(f, 8 * beat), tb, 0.05)
    add(trilha, kick(), tb, 0.55)
    add(trilha, hat(), tb + beat / 2, 0.10)
    if b % 2 == 0: add(trilha, nota(baixo[compasso], beat * 0.9, 'baixo'), tb, 0.16)
    b += 1; tb = b * beat
trilha = lp(trilha, 9000)
# ducking: trilha cai ~11 dB quando há voz
ev = np.sqrt(np.maximum(lp(voz ** 2, 6), 1e-12)); ev /= ev.max(); duck = 1 - 0.72 * np.clip(ev * 6, 0, 1)
duck = lp(duck, 4)
trilha *= duck
# 4) efeitos
def sfx(nome, t0, g):
    x = ler(os.path.join(SFX, nome)); add(efeitos, x, t0, g)
efeitos = np.zeros(N)
for t0 in (6.40, 11.20, 14.90, 17.95, 22.65): sfx('whoosh-short.mp3', t0, 0.30)
pj = [w for w in C['palavras'] if w['w'].startswith('prejuízo')][0]['s']
sfx('pop.mp3', pj - 0.2, 0.35); sfx('sparkle.mp3', 0.45, 0.22)
ta, tb2 = C['transicao_cta']
sfx('riser.mp3', ta - 1.2, 0.18); sfx('glitch-1.mp3', ta, 0.25); sfx('pop.mp3', tb2, 0.35)
mix = voz_amb * 1.0 + room + trilha * 0.55 + efeitos
# fade final e normalização de pico
mix[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
wavfile.write(T('audio_final.wav'), SR, np.stack([mix, mix], 1).astype(np.float32))
print('ok', round(len(mix) / SR, 2), 's')
