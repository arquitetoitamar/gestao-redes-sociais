"""Acha o Gmail pessoal nos quadros do OCR e grava as caixas a desfocar por quadro (30 fps, 1080x1920).

uso: python3 mascara.py <pasta_dos_quadros_com_tsv>
Os quadros vêm em duas janelas: a_NNNN.jpg começa em 38 s, b_NNNN.jpg em 72 s.
Saída: caixas.json  {"<quadro global>": [[x0, y0, x1, y1], ...]}
"""
import csv, glob, json, os, re, sys
from collections import defaultdict

PASTA = sys.argv[1]
FPS = 30
JANELAS = {'a': 38.0, 'b': 72.0}
GMAIL = re.compile(r'gm[ae]?[il1]|gmet|gma[il]|ads@|\.ads|santos|@gm|lsantos|isantos', re.I)
VENDA = re.compile(r'venda@|pre\.venda|pre\.vend', re.I)
EMAIL = re.compile(r'@|\.com', re.I)


def linhas(tsv):
    """Agrupa as palavras do tsv por linha do tesseract: {(bloco, par, linha): [palavras]}."""
    out = defaultdict(list)
    for r in csv.DictReader(open(tsv, encoding='utf-8', errors='replace'), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r.get('level') != '5' or not (r.get('text') or '').strip():
            continue
        x, y, w, h = (int(r[k]) for k in ('left', 'top', 'width', 'height'))
        out[(r['block_num'], r['par_num'], r['line_num'])].append((x, y, x + w, y + h, r['text']))
    return out


def caixa(ws):
    return [min(w[0] for w in ws), min(w[1] for w in ws), max(w[2] for w in ws), max(w[3] for w in ws)]


bruto = {}
for tsv in sorted(glob.glob(os.path.join(PASTA, '*.tsv'))):
    nome = os.path.basename(tsv).split('.')[0]          # a_0123
    jan, k = nome.split('_')
    n = round(JANELAS[jan] * FPS) + int(k)
    ls = linhas(tsv)
    caixas = []
    # 1) a própria linha do gmail
    for ws in ls.values():
        if any(GMAIL.search(w[4]) for w in ws):
            caixas.append(caixa(ws))
    # 2) âncora: a linha logo abaixo do último membro (teste.atendimento.pre.venda@...)
    emails = sorted((caixa(ws) for ws in ls.values() if any(EMAIL.search(w[4]) for w in ws)), key=lambda b: b[1])
    vendas = [caixa(ws) for ws in ls.values() if any(VENDA.search(w[4]) for w in ws)]
    if vendas:
        v = max(vendas, key=lambda b: b[1])
        passos = [b2[1] - b1[1] for b1, b2 in zip(emails, emails[1:]) if 15 < b2[1] - b1[1] < 90]
        passo = sorted(passos)[len(passos) // 2] if passos else 32
        caixas.append([v[0] - 10, v[3] + int(0.15 * passo), v[2] + 40, v[1] + int(2.0 * passo)])
    if caixas:
        bruto[n] = caixas


def junta(cs):
    return [min(c[0] for c in cs), min(c[1] for c in cs), max(c[2] for c in cs), max(c[3] for c in cs)]


# cada quadro com detecção vira uma caixa por região; preenche buracos de até 1 s por interpolação
# e segura a caixa 6 quadros antes e depois (o OCR falha em quadro tremido)
ns = sorted(bruto)
final = defaultdict(list)
for n in ns:
    for c in bruto[n]:
        for d in range(-6, 7):
            final[n + d].append(c)
for a, b in zip(ns, ns[1:]):
    if 1 < b - a <= FPS:
        ca, cb = junta(bruto[a]), junta(bruto[b])
        for n in range(a + 1, b):
            t = (n - a) / (b - a)
            final[n].append([round(ca[i] + (cb[i] - ca[i]) * t) for i in range(4)])

PAD = 18
saida = {str(n): [[max(0, c[0] - PAD), max(0, c[1] - PAD), min(1080, c[2] + PAD), min(1920, c[3] + PAD)] for c in cs]
         for n, cs in sorted(final.items())}
json.dump(saida, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caixas.json'), 'w'))
print('quadros com detecção:', len(bruto), '| quadros com máscara:', len(saida))
seg = []
for n in sorted(int(k) for k in saida):
    if seg and n == seg[-1][1] + 1:
        seg[-1][1] = n
    else:
        seg.append([n, n])
print('trechos (s):', [(round(a / FPS, 2), round(b / FPS, 2)) for a, b in seg])
