#!/usr/bin/env python3
"""Renderiza build/index.html quadro a quadro e monta o MP4 com a trilha.
  python3 render.py            -> animacao_connect_2min.mp4
  python3 render.py --stills 1,3,5,8   -> stills/ para revisão
Usa 2 processos (memória: render com muitos processos já encheu o disco pela swap)."""
import math, os, subprocess, sys
from multiprocessing import Process
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
PAGINA = os.environ.get('PAGINA', 'index')
URL = 'file://' + os.path.join(AQUI, 'build', PAGINA + '.html')
FPS, TOTAL = 30, 9.0
FR = os.path.join(AQUI, 'quadros-' + os.environ.get('PAGINA', 'index'))


def abre(p):
    b = p.chromium.launch(args=['--force-color-profile=srgb'])
    pg = b.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
    pg.goto(URL)
    pg.wait_for_function('window.__ready === true', timeout=30000)
    return b, pg


def trabalha(idx):
    with sync_playwright() as p:
        b, pg = abre(p)
        for i in idx:
            pg.evaluate(f'window.__seek({i / FPS})')
            pg.screenshot(path=f'{FR}/f{i:05d}.jpg', type='jpeg', quality=93)
        b.close()


if __name__ == '__main__':
    if '--stills' in sys.argv:
        os.makedirs(os.path.join(AQUI, 'stills'), exist_ok=True)
        with sync_playwright() as p:
            b, pg = abre(p)
            for t in [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]:
                pg.evaluate(f'window.__seek({t})')
                pg.screenshot(path=os.path.join(AQUI, 'stills', f'{PAGINA}_{t:05.2f}.jpg'), type='jpeg', quality=85)
            b.close()
        sys.exit()
    os.makedirs(FR, exist_ok=True)
    n = int(math.ceil(TOTAL * FPS))
    ps = [Process(target=trabalha, args=(list(range(n))[k::2],)) for k in range(2)]
    [q.start() for q in ps]; [q.join() for q in ps]
    saida = os.path.join(AQUI, 'animacao_connect_2min.mp4' if PAGINA == 'index' else f'animacao_connect_{PAGINA}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{FR}/f%05d.jpg',
                    '-i', os.path.join(AQUI, 'audio', 'trilha.wav'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', '18', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                    '-movflags', '+faststart', saida], check=True)
    print('ok', saida, n, 'quadros')
