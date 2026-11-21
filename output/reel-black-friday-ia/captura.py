"""B-roll com rolagem real: viewport 432x768 css, dsf 2.5 -> quadros 1080x1920 em trab/br/<seg>/f_00000.jpg.
Cada segmento: (nome, seletor da seção, deslocamento inicial css, distância css, quadros a 30 fps)."""
import os, math
from playwright.sync_api import sync_playwright
URL = 'https://marketplaces.tiops.com.br/black-friday-2026.html'
AQUI = os.path.dirname(os.path.abspath(__file__))
SEGS = [('hero', None, 0, 760, 150), ('prompts', '#prompts', -20, 900, 115),
        ('calendario', '#calendario', -20, 700, 95), ('margem', '#margem', -20, 1050, 145)]
ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * x)
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True)
    pg = b.new_page(viewport={'width': 432, 'height': 768}, device_scale_factor=2.5, is_mobile=True, has_touch=True)
    pg.goto(URL, wait_until='networkidle'); pg.wait_for_timeout(1500)
    pg.add_style_tag(content='html{scroll-behavior:auto!important}')
    for nome, sel, off, dist, n in SEGS:
        pasta = os.path.join(AQUI, 'trab', 'br', nome); os.makedirs(pasta, exist_ok=True)
        y0 = (pg.evaluate("s=>Math.round(document.querySelector(s).getBoundingClientRect().top+scrollY)", sel) if sel else 0) + off
        for i in range(n):
            pg.evaluate('y=>window.scrollTo(0,y)', y0 + dist * ease(i / (n - 1)))
            pg.wait_for_timeout(15)
            pg.screenshot(path=os.path.join(pasta, 'f_%05d.jpg' % i), type='jpeg', quality=90)
        print(nome, n, flush=True)
    b.close()
