"""Passo 1 da edição de "como gerar vídeo para o Marketplace" (gravação de tela de 22min35s, 10/11/2026).

- Fala acelerada 1,2x (pedido do Itamar: "acelere o vídeo pra ficar mais rápido"); esperas em silêncio 4x,
  com 0,3 s de borda; trechos em silêncio com o vídeo gerado tocando ficam em 1x (é o resultado que interessa).
- Corta 20:12–21:17: tentativa de adicionar um segundo conector no Gemini que não completou e mostra o e-mail dele.
- Desfoca a lista de conversas/projetos e a conta na lateral do ChatGPT e do Gemini (detectados pelo endereço
  na barra do navegador, OCR em trab/url.json) e a URL do bucket S3 no começo.
- Áudio: só muda a velocidade (atempo); sem denoise, EQ ou música. Montado em Python com contagem exata de
  amostras por trecho, para não desalinhar em ~260 emendas.
- Saída: trab/base.mp4 e trab/edl.json (mapa tempo original -> editado, usado por motions, legenda e capítulos).

uso: python3 edita.py"""
import json, os, re, subprocess
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(AQUI, 'trab')
SRC = os.path.join(TRAB, 'original.mp4')
DUR = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC],
                           capture_output=True, text=True).stdout)
FALA, ESPERA, BORDA, SR = 1.2, 4.0, 0.3, 48000
CORTE = (1212.4, 1277.6)

# ---------- silêncios: espera (4x) ou vídeo gerado tocando (1x)
def quadro(t):
    im = np.asarray(Image.open(os.path.join(TRAB, 'f1', '%04d.jpg' % (int(t) + 1))).convert('L').resize((240, 135))).astype(float)
    im[95:, 195:] = 0  # webcam
    return im

def movimento(a, b):
    ts = [t for t in range(int(a) + 1, int(b)) if t + 1 < int(DUR)]
    return float(np.median([np.abs(quadro(t) - quadro(t + 1)).mean() for t in ts])) if ts else 0.0

trechos = []  # (ini, fim, vel)  vel=None -> cortado
for a, b in json.load(open(os.path.join(TRAB, 'silencios.json'))):
    if b - a < 1.5 or (a < CORTE[1] and b > CORTE[0]):
        continue
    if b - a >= 2.5 and movimento(a, b) >= 0.8:
        trechos.append((a, b, 1.0))
    else:
        trechos.append((a + BORDA, b - BORDA, ESPERA))
trechos.append((CORTE[0], CORTE[1], None))
trechos.sort()
edl, t = [], 0.0
for a, b, v in trechos:
    if a > t + 0.02:
        edl.append([t, a, FALA])
    edl.append([max(a, t), b, v]); t = b
if DUR > t + 0.02:
    edl.append([t, DUR, FALA])
out = 0.0
for e in edl:
    e.append(round(out, 4))
    if e[2]: out += (e[1] - e[0]) / e[2]
json.dump({'segmentos': [dict(ini=a, fim=b, vel=v, saida=o) for a, b, v, o in edl], 'duracao': out},
          open(os.path.join(TRAB, 'edl.json'), 'w'), indent=1)
print('trechos', len(edl), 'duração editada %.1f s (original %.1f s)' % (out, DUR), flush=True)

# ---------- janelas de desfoque (tempo do original)
url = {int(k): v.lower() for k, v in json.load(open(os.path.join(TRAB, 'url.json'))).items()}
def janelas(chave):
    seg = sorted(k for k, v in url.items() if chave in v)
    jan = []
    for k in seg:  # o quadro k (1 fps) é o instante k-1 s; margem de 0,9 s para trocas de aba
        a, b = k - 1 - 0.9, k - 1 + 0.9
        if jan and a <= jan[-1][1]:
            jan[-1][1] = b
        else:
            jan.append([a, b])
    return jan
DESF = [((66, 445, 246, 522), janelas('chatgpt')),           # lateral do ChatGPT: fixados, projetos, conta
        ((66, 445, 296, 522), janelas('gemini')),            # lateral do Gemini: notebooks, conversas, conta
        ((165, 137, 760, 30), [[32.0, 52.5]])]               # URL do bucket S3
for (x, y, w, h), j in DESF:
    print('desfoque', (x, y, w, h), len(j), 'janelas', '%.0f s' % sum(b - a for a, b in j))

def grafo(a, b, v):
    """desfoques do trecho [a, b] (tempo relativo ao início do trecho) + velocidade."""
    g, cur = [], '0:v'
    for k, ((x, y, w, h), jan) in enumerate(DESF):
        ws = [(max(wa, a) - a, min(wb, b) - a) for wa, wb in jan if wa < b and wb > a]
        if not ws: continue
        en = '+'.join('between(t,%.3f,%.3f)' % w_ for w_ in ws)
        g.append('[%s]split[b%d][c%d]' % (cur, k, k))
        g.append('[c%d]crop=%d:%d:%d:%d,boxblur=lr=%d:lp=3:cr=%d:cp=3[bl%d]' % (k, w, h, x, y, min(24, h // 2 - 1), min(12, h // 4 - 1), k))
        g.append("[b%d][bl%d]overlay=%d:%d:enable='%s'[o%d]" % (k, k, x, y, en, k))
        cur = 'o%d' % k
    g.append('[%s]setpts=(PTS-STARTPTS)/%g,fps=30,format=yuv420p[v]' % (cur, v))
    return ';'.join(g)

# ---------- áudio: trecho a trecho, com tamanho exato
partes = []
for a, b, v, o in edl:
    if not v: continue
    n = int(round((o + (b - a) / v) * SR)) - int(round(o * SR))
    if v == ESPERA:
        partes.append(np.zeros(n, np.float32)); continue
    af = [] if v == 1.0 else ['-af', 'atempo=%g' % v]
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.4f' % a, '-t', '%.4f' % (b - a), '-i', SRC] + af +
                                     ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
    x = x[:n] if len(x) >= n else np.concatenate([x, np.zeros(n - len(x), np.float32)])
    partes.append(x)
aud = np.concatenate(partes)
import wave
with wave.open(os.path.join(TRAB, 'base_audio.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(aud, -1, 1) * 32767).astype('<i2').tobytes())
print('áudio %.2f s' % (len(aud) / SR), flush=True)

# ---------- vídeo: trecho a trecho, com número exato de quadros (sem deriva nas emendas)
os.makedirs(os.path.join(TRAB, 'seg'), exist_ok=True)
lista = []
for i, (a, b, v, o) in enumerate(edl):
    if not v: continue
    f0, f1 = int(round(o * 30)), int(round((o + (b - a) / v) * 30))
    if f1 <= f0: continue
    arq = os.path.join(TRAB, 'seg', '%03d.ts' % i)
    lista.append("file '%s'" % arq)
    if os.path.exists(arq): continue
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.4f' % a, '-t', '%.4f' % (b - a + 0.5), '-i', SRC,
                    '-filter_complex', grafo(a, b + 0.5, v), '-map', '[v]', '-frames:v', str(f1 - f0),
                    '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', '-g', '60', '-an', '-f', 'mpegts', arq], check=True)
    if i % 10 == 0: print('trecho %d/%d' % (i + 1, len(edl)), flush=True)
open(os.path.join(TRAB, 'lista.txt'), 'w').write('\n'.join(lista) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(TRAB, 'lista.txt'),
                '-i', os.path.join(TRAB, 'base_audio.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-ac', '2', '-movflags', '+faststart',
                os.path.join(TRAB, 'base.mp4')], check=True)
for f in os.listdir(os.path.join(TRAB, 'seg')):
    os.remove(os.path.join(TRAB, 'seg', f))
print('base.mp4 pronto')
