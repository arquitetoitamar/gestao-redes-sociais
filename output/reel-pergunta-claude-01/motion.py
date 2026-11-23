"""Renderiza motion.html quadro a quadro (PNG com transparência) -> trab/mot/m_00000.png
uso: python3 motion.py todos [processos]   |   python3 motion.py teste t1,t2,...  (-> trab/teste_m_<t>.png)"""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
AQUI = os.path.dirname(os.path.abspath(__file__)); FPS = 30
HTML = open(os.path.join(AQUI, 'motion.html'), encoding='utf-8').read().replace(
    '__CRONO__', open(os.path.join(AQUI, 'trab', 'cronograma.json'), encoding='utf-8').read())

def faixa(args):
    tempos, nomes = args
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(HTML, wait_until='networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(400)
        for t, n in zip(tempos, nomes):
            pg.evaluate('t=>window.seek(t)', t); pg.screenshot(path=n, type="jpeg", quality=92)
        b.close()
    return len(tempos)

if __name__ == '__main__':
    if sys.argv[1] == 'teste':
        ts = [float(x) for x in sys.argv[2].split(',')]
        faixa((ts, [os.path.join(AQUI, 'trab', 'teste_m_%s.jpg' % t) for t in ts]))
    else:
        dur = json.load(open(os.path.join(AQUI, 'trab', 'cronograma.json')))['duracao']
        n = int(round(dur * FPS)); k = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        os.makedirs(os.path.join(AQUI, 'trab', 'mot'), exist_ok=True)
        idx = list(range(n)); partes = [idx[i::k] for i in range(k)]
        jobs = [([i / FPS for i in pt], [os.path.join(AQUI, 'trab', 'mot', 'm_%05d.jpg' % i) for i in pt]) for pt in partes]
        with ProcessPoolExecutor(k) as ex:
            print('quadros', sum(ex.map(faixa, jobs)))
