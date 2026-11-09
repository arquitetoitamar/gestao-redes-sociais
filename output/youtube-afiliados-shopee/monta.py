"""Passo 2: motions por cima do trab/base.mp4 e tela final. Saída: trab/final.mp4 + capitulos.txt.
Tempos são dados no vídeo ORIGINAL e convertidos pelo trab/edl.json (esperas aceleradas mudam o relógio).
uso: python3 monta.py <pasta_trab>"""
import json, os, subprocess, sys
from playwright.sync_api import sync_playwright

TRAB = sys.argv[1]
AQUI = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(TRAB, 'png'); os.makedirs(PNG, exist_ok=True)
EDL = json.load(open(os.path.join(TRAB, 'edl.json')))

def ed(t):
    """tempo do original -> tempo editado"""
    for s in EDL['segmentos']:
        if s['ini'] <= t <= s['fim']:
            return s['saida'] + (t - s['ini']) / s['vel']
    return EDL['duracao']

# ---------------- roteiro (tempos do original)
CAP = [  # (início, rótulo, título) — também viram capítulos da descrição
    (0, None, 'Introdução: afiliado Shopee com IA'),
    (40, 'PASSO 1', 'Conecte sua conta Shopee Afiliados'),
    (120, 'PASSO 2', 'Adicione o conector no ChatGPT'),
    (214, 'PASSO 3', 'Encontre os produtos com maior comissão'),
    (318, 'PASSO 4', 'Gere seu link de afiliado'),
    (385, 'PASSO 5', 'Texto pronto para grupo de achadinhos'),
    (443, 'PASSO 6', 'Vídeo do produto com IA'),
    (535, 'BÔNUS', 'Roteiro e vídeo no Google Flow'),
    (834, 'EXTRA', 'Indique e ganhe'),
    (868, 'EXTRA', 'Consulte suas comissões'),
]
PROMPTS = [(229, 'Encontre os produtos com maior comissão'),
           (337, 'Quero vender esse produto. Gere meu link de afiliado'),
           (387, 'Gere uma descrição para um grupo de achadinhos com o link e o vídeo'),
           (447, 'Gere um vídeo do produto com base nas imagens e na descrição'),
           (535, 'Gere o roteiro para criar o vídeo no Flow'),
           (880, 'Consulte minhas comissões')]
CONECTOR = 128          # momento em que ele cola o endereço no ChatGPT
NOME = 24               # "eu sou Itamar..."
CTAS = [250, 520, 700]  # lembretes "link na descrição"

# ---------------- renderiza os cartões (PNG transparente) e as animações
def shot(pg, path):
    pg.screenshot(path=path, omit_background=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    pg.goto('file://' + os.path.join(AQUI, 'motions.html')); pg.evaluate('window.__ready')
    pg.wait_for_timeout(300)
    for i, (t, k, tt) in enumerate(CAP):
        if k:
            pg.evaluate('([k,t]) => show("chap", {k, t})', [k, tt]); shot(pg, f'{PNG}/chap_{i:02d}.png')
    for i, (t, tx) in enumerate(PROMPTS):
        pg.evaluate('p => show("prm", {p})', tx); shot(pg, f'{PNG}/prm_{i:02d}.png')
    for nm in ('con', 'low', 'fast', 'cta'):
        pg.evaluate(f'show("{nm}")'); shot(pg, f'{PNG}/{nm}.png')
    os.makedirs(f'{TRAB}/intro', exist_ok=True); os.makedirs(f'{TRAB}/outro', exist_ok=True)
    pg.evaluate('show("intro")')
    for f in range(180):
        pg.evaluate(f'seekIntro({f / 30})'); shot(pg, f'{TRAB}/intro/f{f:04d}.png')
    pg.evaluate('show("outro")')
    for f in range(240):
        pg.evaluate(f'seekOutro({f / 30})'); pg.screenshot(path=f'{TRAB}/outro/f{f:04d}.jpg', type='jpeg', quality=95)
    b.close()
print('motions renderizados', flush=True)

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', f'{TRAB}/intro/f%04d.png', '-c:v', 'qtrle', '-pix_fmt', 'argb',
                f'{TRAB}/intro.mov'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', f'{TRAB}/outro/f%04d.jpg',
                '-f', 'lavfi', '-t', '8', '-i', 'anullsrc=r=48000:cl=stereo',
                '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                f'{TRAB}/outro.mp4'], check=True)

# ---------------- overlays (cartões com fade/slide) no tempo editado
DUR = EDL['duracao']
items = []   # (arquivo, t0, t1, x, y_expr, desliza)
fim_cap = [c[0] for c in CAP[1:]] + [10 ** 9]
for i, (t, k, tt) in enumerate(CAP):
    if k:
        items.append((f'{PNG}/chap_{i:02d}.png', ed(t), min(ed(fim_cap[i]), DUR) - 0.05, 'baixo'))
for i, (t, tx) in enumerate(PROMPTS):
    items.append((f'{PNG}/prm_{i:02d}.png', ed(t), ed(t) + 6.0, 'cima'))
items.append((f'{PNG}/con.png', ed(CONECTOR), ed(CONECTOR) + 9.0, 'cima'))
items.append((f'{PNG}/low.png', ed(NOME), ed(NOME) + 5.5, 'baixo'))
for t in CTAS:
    items.append((f'{PNG}/cta.png', ed(t), ed(t) + 5.0, 'cima'))
for s in EDL['segmentos']:
    if s['vel'] != 1.0:
        d = (s['fim'] - s['ini']) / s['vel']
        items.append((f'{PNG}/fast.png', s['saida'], s['saida'] + d, 'fixo'))

inputs = ['-i', f'{TRAB}/base.mp4', '-i', f'{TRAB}/intro.mov']
g = ['[1:v]setpts=PTS-STARTPTS[intro]', '[0:v][intro]overlay=0:0:eof_action=pass[v0]']
cur = 'v0'
for k, (arq, t0, t1, modo) in enumerate(items):
    n = k + 2
    d = max(0.5, t1 - t0)
    inputs += ['-loop', '1', '-t', '%.3f' % d, '-i', arq]
    fade = 'fade=in:st=0:d=0.25:alpha=1,fade=out:st=%.3f:d=0.25:alpha=1' % max(0, d - 0.25) if modo != 'fixo' else 'null'
    g.append('[%d:v]format=rgba,%s,setpts=PTS-STARTPTS+%.3f/TB[o%d]' % (n, fade, t0, k))
    if modo == 'cima':
        y = "'if(lt(t,%.3f),-40+40*(t-%.3f)/0.3,0)'" % (t0 + 0.3, t0)
    elif modo == 'baixo':
        y = "'if(lt(t,%.3f),40-40*(t-%.3f)/0.3,0)'" % (t0 + 0.3, t0)
    else:
        y = '0'
    g.append("[%s][o%d]overlay=x=0:y=%s:eof_action=pass:enable='between(t,%.3f,%.3f)'[v%d]" % (cur, k, y, t0, t0 + d, k + 1))
    cur = 'v%d' % (k + 1)
n_out = len(items) + 2
inputs += ['-i', f'{TRAB}/outro.mp4']
g.append('[%s]format=yuv420p,setsar=1[vm];[%d:v]format=yuv420p,setsar=1[vo];[vm][0:a][vo][%d:a]concat=n=2:v=1:a=1[vf][af]' % (cur, n_out, n_out))
open(os.path.join(TRAB, 'grafo.txt'), 'w').write(';\n'.join(g))
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(g), '-map', '[vf]', '-map', '[af]',
                '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{TRAB}/final.mp4'], check=True)
print('motions aplicados', flush=True)

# capítulos para a descrição
def mmss(s): s = int(round(s)); return '%d:%02d' % (s // 60, s % 60)
caps = ['%s %s' % (mmss(ed(t)) if i else '0:00', (k.title() + ': ' if k and k.startswith('PASSO') else '') + tt)
        for i, (t, k, tt) in enumerate(CAP)]
caps.append('%s Links e próximos passos' % mmss(DUR))
open(os.path.join(AQUI, 'capitulos.txt'), 'w').write('\n'.join(caps) + '\n')
print('\n'.join(caps)); print('final.mp4 pronto')
