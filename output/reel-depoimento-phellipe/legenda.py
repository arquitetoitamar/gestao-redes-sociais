#!/usr/bin/env python3
"""Gera trab/legenda.ass a partir de trab/palavras.json (whisper com tempo por palavra).

Cada palavra entra quando é falada (as seguintes da página ficam invisíveis
mas ocupando lugar, para a linha não pular), a palavra da vez fica amarela
com um pop de escala. Páginas de até 3 palavras / 16 letras.
Mais: título fixo no topo e identificação do Phellipe nos primeiros segundos.
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(AQUI, 'trab')
FONTE = 'Avenir Next Condensed Heavy'

# Correções do que o whisper ouviu torto (texto em maiúsculas, sem pontuação final).
CORRIGE = {'ASSISTE': 'ASSISTI'}
# Correção pontual por instante (o whisper ouviu "Está" no "Vai" logo depois da emenda).
CORRIGE_EM = [(57.5, 58.3, 'ESTÁ', 'VAI')]

TITULO = ['ELE ACHOU MEU VÍDEO', 'COM 24 VISUALIZAÇÕES']
NOME, CARGO = 'PHELLIPE', 'fabricante e seller'

AMARELO, BRANCO, PRETO = '&H005EE4FF&', '&H00FFFFFF&', '&H00000000&'


def ts(s):
    s = max(0, s)
    h, r = divmod(s, 3600)
    m, r = divmod(r, 60)
    return '%d:%02d:%05.2f' % (h, m, r)


def palavras():
    d = json.load(open(os.path.join(TRAB, 'palavras.json')))
    out = []
    for s in d['transcription']:
        bruto = s['text'].strip()
        if not bruto:
            continue
        txt = re.sub(r'[.,;:!…]+$', '', bruto).upper()
        txt = CORRIGE.get(txt, txt)
        a = s['offsets']['from'] / 1000
        for x, y, de, para in CORRIGE_EM:
            if x <= a <= y and txt == de:
                txt = para
        out.append({'t': txt, 'a': s['offsets']['from'] / 1000, 'b': s['offsets']['to'] / 1000,
                    'fim_frase': bool(re.search(r'[.?!…]$', bruto))})
    return out


def paginas(ws):
    pags, cur = [], []
    for i, w in enumerate(ws):
        if cur:
            gap = w['a'] - cur[-1]['b']
            letras = sum(len(x['t']) + 1 for x in cur) + len(w['t'])
            if len(cur) >= 3 or letras > 16 or gap > 0.35 or cur[-1]['fim_frase']:
                pags.append(cur)
                cur = []
        cur.append(w)
    if cur:
        pags.append(cur)
    return pags


def main():
    ws = palavras()
    pags = paginas(ws)
    linhas = []
    for k, p in enumerate(pags):
        prox = pags[k + 1][0]['a'] if k + 1 < len(pags) else p[-1]['b'] + 0.6
        fim_pag = min(p[-1]['b'] + 0.35, prox)
        for i, w in enumerate(p):
            ini = w['a']
            fim = p[i + 1]['a'] if i + 1 < len(p) else fim_pag
            if fim - ini < 0.02:
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
            linhas.append('Dialogue: 1,%s,%s,Leg,,0,0,0,,{\\an5\\pos(540,1270)}%s'
                          % (ts(ini), ts(fim), ' '.join(partes)))

    dur = ws[-1]['b'] + 0.4
    titulo = '\\N'.join(TITULO)
    linhas.append('Dialogue: 2,%s,%s,Titulo,,0,0,0,,{\\an8\\pos(540,230)\\fscx60\\fscy60'
                  '\\t(0,180,\\fscx106\\fscy106)\\t(180,280,\\fscx100\\fscy100)}%s'
                  % (ts(0), ts(dur), titulo))
    linhas.append('Dialogue: 2,%s,%s,Nome,,0,0,0,,{\\an1\\move(-500,1580,70,1580,0,260)'
                  '\\fad(0,250)}%s{\\fs58\\c%s\\b0}\\N%s'
                  % (ts(0.5), ts(5.2), NOME, BRANCO, CARGO))

    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,{FONTE},120,{BRANCO},{BRANCO},{PRETO},&H80000000&,1,0,0,0,100,100,1,0,1,7,3,5,60,60,0,1
Style: Titulo,{FONTE},78,{PRETO},{PRETO},{AMARELO},&H00000000&,1,0,0,0,100,100,1,0,3,16,0,8,60,60,0,1
Style: Nome,{FONTE},86,{AMARELO},{AMARELO},{PRETO},&H80000000&,1,0,0,0,100,100,1,0,1,5,2,1,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(os.path.join(TRAB, 'legenda.ass'), 'w').write(cab + '\n'.join(linhas) + '\n')

    # Legenda comum (SRT) para o YouTube/acessibilidade, uma página por bloco.
    srt = []
    for n, p in enumerate(pags, 1):
        a, b = p[0]['a'], p[-1]['b'] + 0.2
        f = lambda s: '%02d:%02d:%02d,%03d' % (s // 3600, s % 3600 // 60, s % 60, round(s % 1 * 1000) % 1000)
        srt.append('%d\n%s --> %s\n%s\n' % (n, f(a), f(b), ' '.join(x['t'] for x in p)))
    open(os.path.join(AQUI, 'depoimento-phellipe.srt'), 'w').write('\n'.join(srt))
    print(len(pags), 'páginas,', len(linhas), 'linhas')


if __name__ == '__main__':
    main()
