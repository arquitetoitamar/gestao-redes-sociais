#!/usr/bin/env python3
"""Cortes do fim de semana (31/10 e 01/11) a partir dos brutos da Imersão.

Mesmo motor do depoimento do Phellipe (output/reel-depoimento-phellipe):
trechos colados com fade de 30-40 ms no áudio (áudio original, sem tratamento),
zoom nos planos abertos, whisper por palavra no corte pronto e legenda ASS
com a palavra da vez em amarelo, título fixo no topo e cartela no fim.

  python3 editor.py fds-phellipe     # sábado: palestra do Phellipe
  python3 editor.py fds-gravacao     # domingo: Itamar, gravação no YouTube
"""
import json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
WHISPER = os.path.expanduser('~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin')
V = lambda n: os.path.join(AQUI, 'videos', n)

CORTES = {
    'fds-phellipe': {
        # (arquivo, início, fim) — sem o "40% do faturamento" nem o nome da loja
        'trechos': [
            ('IMG_9719.MOV', 3.70, 6.15),    # sou comercial, vendedor a vida inteira
            ('IMG_9718.MOV', 11.05, 16.40),  # comecei a implantar IA na empresa
            ('IMG_9718.MOV', 18.40, 24.70),  # GPT 2022, nossa, aqui tá um caminho
            ('IMG_9719.MOV', 14.30, 21.25),  # todo mundo é funcionário, quanto mais técnico pior
            ('IMG_9719.MOV', 22.35, 30.80),  # era desenhista; o primeiro caminho foi o desenho
        ],
        # planos abertos: (arquivo, de, até, zoom, centro x, centro y)
        'abertos': [
            ('IMG_9718.MOV', 9.0, 13.5, 1.6, 0.55, 0.47),
            ('IMG_9718.MOV', 16.6, 18.6, 1.6, 0.47, 0.55),
            ('IMG_9719.MOV', 14.0, 29.5, 1.45, 0.47, 0.50),
        ],
        'titulo': ['UMA FÁBRICA DE 26 ANOS', 'COLOCOU A IA PRA TRABALHAR'],
        'nome': ('PHELLIPE', 'fabricante, na Imersão IA'),
        'cartela': ['A PALESTRA INTEIRA ESTÁ', 'NA GRAVAÇÃO DA IMERSÃO'],
        'corrige': {'IAR': 'IA'},
    },
    'fds-gravacao': {
        'trechos': [('IMG_9633.MOV', 0.30, 17.95)],
        'abertos': [],
        'titulo': ['3 HORAS DE IMERSÃO', 'DE GRAÇA NO YOUTUBE'],
        'nome': None,
        'cartela': ['BUSCA NO YOUTUBE:', 'IMERSÃO IA PARA MARKETPLACES'],
        'corrige': {'YAPA': 'IA PARA'},
    },
}

FONTE = 'Avenir Next Condensed Heavy'
AMARELO, BRANCO, PRETO = '&H005EE4FF&', '&H00FFFFFF&', '&H00000000&'


def pedacos(c):
    """Divide cada trecho onde começa/termina um plano aberto."""
    out = []
    for arq, a, b in c['trechos']:
        cortes = sorted({t for f, x, y, *_ in c['abertos'] if f == arq for t in (x, y)})
        pts = [a] + [t for t in cortes if a < t < b] + [b]
        for x, y in zip(pts, pts[1:]):
            z = next((ab for ab in c['abertos'] if ab[0] == arq and ab[1] <= x and y <= ab[2]), None)
            out.append((arq, x, y, z))
    return out


def base(nome, c, saida):
    arqs = sorted({t[0] for t in c['trechos']})
    idx = {a: i for i, a in enumerate(arqs)}
    f, vs, as_ = [], [], []
    for i, (arq, a, b, z) in enumerate(pedacos(c)):
        zf = ''
        if z:
            _, _, _, zoom, cx, cy = z
            w, h = round(1080 / zoom / 2) * 2, round(1920 / zoom / 2) * 2
            zf = ',crop=%d:%d:%d:%d,scale=1080:1920:flags=lanczos' % (
                w, h, round(1080 * cx - w / 2), round(1920 * cy - h / 2))
        f.append('[%d:v]trim=%s:%s,setpts=PTS-STARTPTS,fps=30%s,setsar=1[v%d]' % (idx[arq], a, b, zf, i))
        vs.append('[v%d]' % i)
    for i, (arq, a, b) in enumerate(c['trechos']):
        f.append('[%d:a]atrim=%s:%s,asetpts=PTS-STARTPTS,afade=t=in:d=0.03,'
                 'afade=t=out:st=%.3f:d=0.04[a%d]' % (idx[arq], a, b, b - a - 0.04, i))
        as_.append('[a%d]' % i)
    f.append(''.join(vs) + 'concat=n=%d:v=1:a=0[v]' % len(vs))
    f.append(''.join(as_) + 'concat=n=%d:v=0:a=1[a]' % len(as_))
    cmd = [FF, '-v', 'error', '-y']
    for a in arqs:
        cmd += ['-i', V(a)]
    cmd += ['-filter_complex', ';'.join(f), '-map', '[v]', '-map', '[a]', '-c:v', 'libx264',
            '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', saida]
    subprocess.run(cmd, check=True)


def palavras(base_mp4, trab, c):
    wav = os.path.join(trab, 'base.wav')
    subprocess.run([FF, '-v', 'error', '-y', '-i', base_mp4, '-ar', '16000', '-ac', '1', wav], check=True)
    subprocess.run(['whisper-cli', '-m', WHISPER, '-l', 'pt', '-f', wav, '-ml', '1', '-sow', '-oj',
                    '-of', os.path.join(trab, 'palavras'), '-np'], check=True, capture_output=True)
    d = json.load(open(os.path.join(trab, 'palavras.json')))
    ws = []
    for s in d['transcription']:
        bruto = s['text'].strip()
        if not bruto:
            continue
        t = re.sub(r'[.,;:!…]+$', '', bruto).upper()
        t = c['corrige'].get(t, t)
        ws.append({'t': t, 'a': s['offsets']['from'] / 1000, 'b': s['offsets']['to'] / 1000,
                   'fim': bool(re.search(r'[.?!…]$', bruto))})
    return ws


def ts(s):
    s = max(0, s)
    return '%d:%02d:%05.2f' % (s // 3600, s % 3600 // 60, s % 60)


def legenda(ws, c, dur, ass):
    pags, cur = [], []
    for w in ws:
        if cur and (len(cur) >= 3 or sum(len(x['t']) + 1 for x in cur) + len(w['t']) > 16
                    or w['a'] - cur[-1]['b'] > 0.35 or cur[-1]['fim']):
            pags.append(cur)
            cur = []
        cur.append(w)
    if cur:
        pags.append(cur)
    L = []
    for k, p in enumerate(pags):
        prox = pags[k + 1][0]['a'] if k + 1 < len(pags) else dur
        fim_pag = min(p[-1]['b'] + 0.35, prox)
        for i, w in enumerate(p):
            fim = p[i + 1]['a'] if i + 1 < len(p) else fim_pag
            if fim - w['a'] < 0.02:
                continue
            partes = []
            for j, x in enumerate(p):
                if j < i:
                    partes.append(x['t'])
                elif j == i:
                    partes.append('{\\c%s\\fscx72\\fscy72\\t(0,90,\\fscx112\\fscy112)'
                                  '\\t(90,170,\\fscx100\\fscy100)}%s{\\r}' % (AMARELO, x['t']))
                else:
                    partes.append('{\\alpha&HFF&}%s' % x['t'])
            L.append('Dialogue: 1,%s,%s,Leg,,0,0,0,,{\\an5\\pos(540,1270)}%s' % (ts(w['a']), ts(fim), ' '.join(partes)))
    L.append('Dialogue: 2,%s,%s,Titulo,,0,0,0,,{\\an8\\pos(540,230)\\fscx60\\fscy60'
             '\\t(0,180,\\fscx106\\fscy106)\\t(180,280,\\fscx100\\fscy100)}%s' % (ts(0), ts(dur), '\\N'.join(c['titulo'])))
    if c['nome']:
        L.append('Dialogue: 2,%s,%s,Nome,,0,0,0,,{\\an1\\move(-500,1580,70,1580,0,260)\\fad(0,250)}'
                 '%s{\\fs58\\c%s\\b0}\\N%s' % (ts(0.5), ts(5.2), c['nome'][0], BRANCO, c['nome'][1]))
    L.append('Dialogue: 2,%s,%s,Cartela,,0,0,0,,{\\an2\\pos(540,1640)\\fad(200,0)\\fscx80\\fscy80'
             '\\t(0,200,\\fscx100\\fscy100)}%s' % (ts(dur - 3.6), ts(dur), '\\N'.join(c['cartela'])))
    cab = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,{F},120,{B},{B},{P},&H80000000&,1,0,0,0,100,100,1,0,1,7,3,5,60,60,0,1
Style: Titulo,{F},74,{P},{P},{A},&H00000000&,1,0,0,0,100,100,1,0,3,16,0,8,60,60,0,1
Style: Nome,{F},86,{A},{A},{P},&H80000000&,1,0,0,0,100,100,1,0,1,5,2,1,60,60,0,1
Style: Cartela,{F},66,{B},{B},{P},&H00000000&,1,0,0,0,100,100,1,0,3,18,0,2,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".replace('{F}', FONTE).replace('{B}', BRANCO).replace('{P}', PRETO).replace('{A}', AMARELO)
    open(ass, 'w').write(cab + '\n'.join(L) + '\n')
    return len(pags)


def main(nome):
    c = CORTES[nome]
    trab = os.path.join(AQUI, 'trab', nome)
    os.makedirs(trab, exist_ok=True)
    b = os.path.join(trab, 'base.mp4')
    base(nome, c, b)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'csv=p=0', b], capture_output=True, text=True).stdout)
    ws = palavras(b, trab, c)
    print(' '.join(w['t'] for w in ws))
    n = legenda(ws, c, dur, os.path.join(trab, 'legenda.ass'))
    out = V(nome + '.mp4')
    subprocess.run([FF, '-v', 'error', '-y', '-i', b, '-vf', 'ass=' + os.path.join(trab, 'legenda.ass'),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
                    '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
    print('%s: %.1f s, %d páginas de legenda -> %s' % (nome, dur, n, out))


if __name__ == '__main__':
    main(sys.argv[1])
