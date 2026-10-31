"""Grava uma janela do macOS (mesmo atrás de outras) como sequência de JPEGs + tempos.
uso: python3 grava_janela.py <window_id> <segundos> <pasta> [fps]
Gera <pasta>/f00000.jpg ... e <pasta>/tempos.txt (segundos desde o início, um por quadro)."""
import os, sys, time
import Quartz
from Foundation import NSURL

wid, dur, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
fps = float(sys.argv[4]) if len(sys.argv) > 4 else 12
os.makedirs(out, exist_ok=True)
opts = {Quartz.kCGImageDestinationLossyCompressionQuality: 0.92}
t0 = time.time(); n = 0; tempos = []
while True:
    agora = time.time() - t0
    if agora > dur or os.path.exists(os.path.join(out, 'PARAR')):
        break
    img = Quartz.CGWindowListCreateImage(Quartz.CGRectNull, Quartz.kCGWindowListOptionIncludingWindow, wid,
                                         Quartz.kCGWindowImageBoundsIgnoreFraming | (0 if os.environ.get('RETINA') else Quartz.kCGWindowImageNominalResolution))
    if img is not None:
        url = NSURL.fileURLWithPath_(os.path.join(out, 'f%05d.jpg' % n))
        d = Quartz.CGImageDestinationCreateWithURL(url, 'public.jpeg', 1, None)
        Quartz.CGImageDestinationAddImage(d, img, opts)
        Quartz.CGImageDestinationFinalize(d)
        tempos.append(agora); n += 1
    alvo = t0 + n / fps
    if alvo > time.time():
        time.sleep(alvo - time.time())
open(os.path.join(out, 'tempos.txt'), 'w').write('\n'.join('%.3f' % t for t in tempos))
print('quadros', n, 'fps real %.1f' % (n / max(tempos[-1], 0.01)))
