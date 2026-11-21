"""Composição final 1080x1920 30 fps: avatar (com quadro parado nos respiros) ou b-roll + animação por cima + áudio.
Saída: videos/reel_bf.mp4"""
import glob, json, os, subprocess
import cv2, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); T = lambda *p: os.path.join(AQUI, 'trab', *p)
W, H, FPS = 1080, 1920, 30
C = json.load(open(T('cronograma.json'))); N = int(round(C['duracao'] * FPS))
BR = {n: sorted(glob.glob(T('br', n, 'f_*.jpg'))) for n in ('hero', 'prompts', 'calendario', 'margem')}

def src_de(t):
    acc = 0.0
    for c, d in C['pausas']:
        ini = c + acc
        if t < ini: break
        if t < ini + d: return c
        acc += d
    return t - acc

def zoom(q, z, cy=0.42):
    if z <= 1.0001: return q
    h, w = q.shape[:2]; nw, nh = int(w / z), int(h / z)
    x0 = (w - nw) // 2; y0 = int((h - nh) * cy)
    return cv2.resize(q[y0:y0 + nh, x0:x0 + nw], (w, h), interpolation=cv2.INTER_LINEAR)

dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', os.path.join(AQUI, 'videos', 'avatar.mp4'), '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
av_i, av_q = -1, None
def avatar(s):
    global av_i, av_q
    alvo = min(int(s * 25), 754)
    while av_i < alvo:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        av_q = np.frombuffer(b, np.uint8).reshape(H, W, 3); av_i += 1
    return av_q

saida = os.path.join(AQUI, 'videos', 'reel_bf_mudo.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', saida], stdin=subprocess.PIPE)
cta = C['cta'][0]
for n in range(N):
    t = n / FPS
    cena = next((c for c in C['cenas'] if c[1] <= t < c[2]), C['cenas'][-1])
    q = avatar(src_de(t))  # sempre avança o decodificador
    if cena[0].startswith('broll:'):
        fs = BR[cena[0].split(':')[1]]; a, b = cena[1], cena[2]
        q = cv2.imread(fs[min(len(fs) - 1, int((t - a) / (b - a) * len(fs)))])
    else:
        z = 1.0 + 0.06 * min(1, t / 6.4) if t < 6.45 else (1.08 if t >= cta else 1.03)
        q = zoom(q, z)
    m = cv2.imread(T('mot', 'm_%05d.png' % n), cv2.IMREAD_UNCHANGED)
    if m.shape[2] == 3: m = np.dstack([m, np.full(m.shape[:2], 255, np.uint8)])
    a = m[..., 3:4].astype(np.float32) / 255
    q = (m[..., :3] * a + q.astype(np.float32) * (1 - a)).astype(np.uint8)
    enc.stdin.write(q.tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
final = os.path.join(AQUI, 'videos', 'reel_bf.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', saida, '-i', T('audio_final.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
print('ok', final)
