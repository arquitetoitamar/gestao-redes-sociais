"""Passo 2: motions e legenda por cima do trab/base.mp4, tela final de 8 s. Saída: trab/final.mp4 + capitulos.txt.
Tempos são dados no vídeo ORIGINAL e convertidos pelo trab/edl.json (fala 1,2x, esperas 4x, um trecho cortado).
Legenda: transcrição do whisper.cpp (trab/leg.srt) com correções de nomes, queimada na faixa cinza de baixo.

uso: python3 monta.py [--so-png]"""
import json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(AQUI, 'trab')
PNG = os.path.join(TRAB, 'png'); os.makedirs(PNG, exist_ok=True)
EDL = json.load(open(os.path.join(TRAB, 'edl.json')))
FFULL = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'

def ed(t):
    """tempo do original -> tempo editado (instante cortado vai para o fim do corte)"""
    for s in EDL['segmentos']:
        if s['ini'] <= t <= s['fim']:
            return s['saida'] if not s['vel'] else s['saida'] + (t - s['ini']) / s['vel']
    return EDL['duracao']

def cortado(t):
    return any(not s['vel'] and s['ini'] <= t <= s['fim'] for s in EDL['segmentos'])

# ---------------- roteiro (tempos do original)
CAP = [  # (início, rótulo, título) — também viram capítulos da descrição
    (0, None, 'Introdução: vídeo de produto com IA'),
    (102, 'PASSO 1', 'Google Flow e as imagens de referência'),
    (167, 'PASSO 2', 'Storyboard do produto no ChatGPT'),
    (259, 'CONCEITO', 'O que a IA precisa para gerar o vídeo'),
    (336, 'PASSO 3', 'Prompt do vídeo UGC vertical 9:16'),
    (428, 'PASSO 4', 'Gerando o vídeo no Google Flow'),
    (467, 'PASSO 5', 'Gerando o vídeo no ChatGPT'),
    (662, 'PASSO 6', 'Gerando o vídeo no Gemini'),
    (817, 'PASSO 7', 'Marketplace Connect puxa fotos e ficha do anúncio'),
    (910, 'PASSO 8', 'Storyboard e vídeo direto do anúncio'),
    (1007, 'PROCESSO', 'Do anúncio ao vídeo, e em massa'),
    (1187, 'BÔNUS', 'Conectar o Gemini ao Marketplace Connect'),
    (1277.7, 'RESULTADO', 'Flow x ChatGPT x Gemini'),
]
PROMPTS = [  # (início, texto, ícone, rótulo)
    (177, '/storyboard  (com a foto do tênis anexada)', 'chatgpt', 'Comando no ChatGPT'),
    (374, 'Gere um prompt para o vídeo UGC do produto no formato 9:16', 'chatgpt', 'Prompt usado'),
    (473, 'Gere o vídeo usando o ChatGPT e o storyboard acima', 'chatgpt', 'Prompt usado'),
    (846, 'Busque o anúncio da furadeira na conta de teste: imagens e descrição', 'gemini', 'Prompt usado (Gemini e ChatGPT)'),
    (910, '/storyboard deste produto', 'chatgpt', 'Comando no ChatGPT'),
    (932, 'Gere um vídeo UGC para este produto', 'gemini', 'Prompt usado no Gemini'),
]
REQ = 266          # explicação no diagrama: fotos, descrição, prompt e IA que gera vídeo
CONECTOR = 1201    # "aqui você vai colocar o endereço do Marketplace Connect"
NOME = 7.0
CTAS = [232, 610, 1040]

# ---------------- legenda
CORRECOES = [
    (r'\bchat ?(de )?(IPT|jpt|APT|apt|GPT|gpt)\b', 'ChatGPT'), (r'\bChat GPT\b', 'ChatGPT'), (r'\bgpt\b', 'GPT'),
    (r'\b(Higgs ?[Ff]ield|Rig ?[Ff]ield|Higs ?field|Higsfield)\b', 'Higgsfield'),
    (r'\b(G[Mm]ini|gmini|gemini)\b', 'Gemini'), (r'\bdo Iá\b', 'da IA'), (r'\bo Iá\b', 'a IA'), (r'\bpara Iá\b', 'para a IA'),
    (r'\bIá\b', 'IA'), (r'\bA Yak\b', 'A IA'), (r'\bCloud\b', 'Claude'), (r'mcp\.tops\.com\.br', 'mcp.tiops.com.br'),
    (r'\bTik Tok\b', 'TikTok'), (r'[Mm]arketplace [Cc]onnect', 'Marketplace Connect'), (r'\bcodex\b', 'Codex'),
    (r'\b[Bb]arra [Ss]toryboard\b', '/storyboard'), (r'\b[Bb]arra mcp\b', '/mcp'),
    (r'\bStoryboard GC\b', 'storyboard UGC'), (r'O vídeo e o GC são', 'Os vídeos UGC são'),
    (r'Então o GC não precisa necessariamente ser o GC', 'Então o vídeo não precisa necessariamente ser UGC'),
    (r'\bGC\b', 'UGC'), (r'\bflow\b(?!\.)', 'Flow'), (r'\bStoryboard\b', 'storyboard'),
]
def corrige(t):
    for de, para in CORRECOES:
        t = re.sub(de, para, t)
    return t[:1].upper() + t[1:]

def ts(s):
    h = int(s // 3600); s -= h * 3600; m = int(s // 60); s -= m * 60
    return '%d:%02d:%05.2f' % (h, m, s)

def legenda():
    ev = []
    f = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + float(s[6:].replace(',', '.'))
    for bl in open(os.path.join(TRAB, 'leg.srt')).read().strip().split('\n\n'):
        l = bl.split('\n')
        if len(l) < 3: continue
        a, b = (f(x) for x in l[1].split(' --> '))
        if cortado((a + b) / 2): continue
        txt = corrige(' '.join(l[2:]).strip())
        ea, eb = ed(a), min(ed(b), EDL['duracao'])
        if txt and eb - ea > 0.15:
            ev.append('Dialogue: 0,%s,%s,Leg,,0,0,0,,%s' % (ts(ea), ts(eb), txt))
    open(os.path.join(TRAB, 'leg.ass'), 'w').write(
        '[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\n'
        'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, '
        'ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
        'Style: Leg,Arial,46,&H00FFFFFF,&H00FFFFFF,&H00261410,&H00261410,1,0,0,0,100,100,0,0,3,10,0,2,80,330,34,1\n\n'
        '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n' + '\n'.join(ev) + '\n')
    print('legenda', len(ev), 'falas', flush=True)

legenda()

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
    for i, (t, tx, ic, lb) in enumerate(PROMPTS):
        pg.evaluate('([p,i,l]) => show("prm", {p, i, l})', [tx, ic, lb]); pg.wait_for_timeout(80); shot(pg, f'{PNG}/prm_{i:02d}.png')
    for nm in ('req', 'con', 'low', 'fast', 'cta'):
        pg.evaluate(f'show("{nm}")'); pg.wait_for_timeout(50); shot(pg, f'{PNG}/{nm}.png')
    if '--so-png' in sys.argv:
        b.close(); sys.exit()
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
items = []   # (arquivo, t0, t1, modo)
fim_cap = [c[0] for c in CAP[1:]] + [10 ** 9]
for i, (t, k, tt) in enumerate(CAP):
    if k:
        items.append((f'{PNG}/chap_{i:02d}.png', ed(t), min(ed(fim_cap[i]), DUR) - 0.05, 'cima'))
for i, (t, *_r) in enumerate(PROMPTS):
    items.append((f'{PNG}/prm_{i:02d}.png', ed(t), ed(t) + 6.0, 'cima'))
items.append((f'{PNG}/req.png', ed(REQ), ed(REQ) + 9.0, 'cima'))
items.append((f'{PNG}/con.png', ed(CONECTOR), ed(CONECTOR) + 8.5, 'cima'))
items.append((f'{PNG}/low.png', ed(NOME), ed(NOME) + 6.0, 'cima'))
for t in CTAS:
    items.append((f'{PNG}/cta.png', ed(t), ed(t) + 5.0, 'cima'))
FAST = [(s['saida'], s['saida'] + (s['fim'] - s['ini']) / s['vel']) for s in EDL['segmentos']
        if s['vel'] and s['vel'] > 2 and (s['fim'] - s['ini']) / s['vel'] >= 0.6]

inputs = ['-i', f'{TRAB}/base.mp4', '-i', f'{TRAB}/intro.mov']
g = ['[1:v]setpts=PTS-STARTPTS[intro]', '[0:v][intro]overlay=0:0:eof_action=pass[v0]']
cur = 'v0'
for k, (arq, t0, t1, modo) in enumerate(items):
    n = k + 2
    d = max(0.5, t1 - t0)
    inputs += ['-loop', '1', '-t', '%.3f' % d, '-i', arq]
    fade = 'fade=in:st=0:d=0.25:alpha=1,fade=out:st=%.3f:d=0.25:alpha=1' % max(0, d - 0.25) if modo != 'fixo' else 'null'
    g.append('[%d:v]format=rgba,%s,setpts=PTS-STARTPTS+%.3f/TB[o%d]' % (n, fade, t0, k))
    y = "'if(lt(t,%.3f),-30+30*(t-%.3f)/0.3,0)'" % (t0 + 0.3, t0) if modo == 'cima' else '0'
    g.append("[%s][o%d]overlay=x=0:y=%s:eof_action=pass:enable='between(t,%.3f,%.3f)'[v%d]" % (cur, k, y, t0, t0 + d, k + 1))
    cur = 'v%d' % (k + 1)
inputs += ['-loop', '1', '-t', '%.3f' % DUR, '-i', f'{PNG}/fast.png']
en = '+'.join('between(t,%.3f,%.3f)' % w for w in FAST)
g.append("[%d:v]format=rgba[fz];[%s][fz]overlay=0:0:enable='%s'[vz]" % (len(items) + 2, cur, en)); cur = 'vz'
g.append('[%s]subtitles=%s:fontsdir=/System/Library/Fonts/Supplemental[vl]' % (cur, os.path.join(TRAB, 'leg.ass')))
n_out = len(items) + 3
inputs += ['-i', f'{TRAB}/outro.mp4']
g.append('[vl]format=yuv420p,setsar=1[vm];[%d:v]format=yuv420p,setsar=1[vo];[vm][0:a][vo][%d:a]concat=n=2:v=1:a=1[vf][af]' % (n_out, n_out))
open(os.path.join(TRAB, 'grafo.txt'), 'w').write(';\n'.join(g))
subprocess.run([FFULL, '-v', 'error', '-stats', '-y'] + inputs + ['-/filter_complex', os.path.join(TRAB, 'grafo.txt'), '-map', '[vf]', '-map', '[af]',
                '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{TRAB}/final.mp4'], check=True)
print('motions aplicados', flush=True)

# capítulos para a descrição
def mmss(s): s = int(round(s)); return '%d:%02d' % (s // 60, s % 60)
caps = ['%s %s' % (mmss(ed(t)) if i else '0:00', (k.title() + ': ' if k and k.startswith('PASSO') else '') + tt)
        for i, (t, k, tt) in enumerate(CAP)]
# sem capítulo para a tela final: ela tem 8 s, e capítulo com menos de 10 s esconde todos
open(os.path.join(AQUI, 'capitulos.txt'), 'w').write('\n'.join(caps) + '\n')
print('\n'.join(caps)); print('final.mp4 pronto')
