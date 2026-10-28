#!/usr/bin/env python3
"""OCR da gravação para o desfoque à prova de falha.

A janela do navegador fica desfocada por padrão; este script acha, a cada
PASSO quadros, as linhas de texto que são rótulos fixos do GestorPro (todas as
palavras no vocabulário do código do app, sem dígitos) e guarda as caixas que
podem ficar nítidas. Qualquer coisa que o OCR não leia, ou leia como palavra
desconhecida (nome, produto, endereço, valor), continua desfocada.

  python3 ocr.py            roda em paralelo e grava trab/ocr/*.json
"""
import csv, io, json, os, re, subprocess, sys, unicodedata
from concurrent.futures import ProcessPoolExecutor
import numpy as np, cv2

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(AQUI, 'videos', 'bruto.mp4')
OUT = os.path.join(AQUI, 'trab', 'ocr')
PASSO = 6
NQ = 28577
X0, Y0, X1, Y1 = 63, 100, 1652, 968          # janela do navegador (abaixo da barra do macOS)
ESC = 1.5
CW, CH = 2384, 1302                           # recorte escalado 1.5x


def norm(w):
    w = unicodedata.normalize('NFKD', w.lower())
    return ''.join(c for c in w if not unicodedata.combining(c))


_V = json.load(open(os.path.join(AQUI, 'trab', 'vocab_ui.json')))
VOCAB = {norm(w) for w in _V}
ESQ = set()                                     # 'escrit?rio' para 'escritório'
for _w in _V:
    for _i, _c in enumerate(_w.lower()):
        if _c in 'áàâãéêíóôõúüç':
            ESQ.add(norm(_w[:_i]) + '?' + norm(_w[_i + 1:]))
LETRAS = 'abcdefghijklmnopqrstuvwxyz'
DUAS = {'de', 'da', 'do', 'em', 'no', 'na', 'os', 'as', 'ou', 'ao', 'ia', 'se', 'um', 'ja', 'eu', 'ml'}


def conhecida(w):
    if w in VOCAB:
        return True
    for i in range(len(w)):                     # OCR em inglês troca letra acentuada
        if (w[:i] + '?' + w[i + 1:]) in ESQ:
            return True
    return False


def palavra_ok(t, conf):
    """None = só pontuação (ignora); True = rótulo conhecido; False = desconhecida."""
    limpa = ''.join(ch for ch in t if ch.isalnum())
    if not limpa:
        return None
    if any(ch.isdigit() for ch in limpa):
        return False
    w = norm(limpa)
    if len(w) == 1 and w.isalpha():
        return None                            # 'e', 'a', 'o': não identifica ninguém
    if conf < 60:
        return False
    if len(w) == 2:
        return w in DUAS                       # iniciais de cliente (ex.: CC) não passam
    return conhecida(w)


def linhas(ws):
    n = len(ws)
    pai = list(range(n))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            a, b = ws[i], ws[j]
            hv = min(a[3], b[3]) - max(a[1], b[1])
            hm = min(a[3] - a[1], b[3] - b[1])
            if hm <= 0 or hv < 0.5 * hm:
                continue
            gap = max(a[0], b[0]) - min(a[2], b[2])
            if gap <= 1.3 * max(a[3] - a[1], b[3] - b[1]):
                pai[raiz(i)] = raiz(j)
    grupos = {}
    for i in range(n):
        grupos.setdefault(raiz(i), []).append(ws[i])
    return list(grupos.values())


def palavras_ocr(img):
    """Leitura bruta: [x0, y0, x1, y1, texto, conf] em coordenadas do quadro inteiro."""
    png = cv2.imencode('.png', img)[1].tobytes()
    out = subprocess.run(['tesseract', '-', '-', '-l', 'eng', '--psm', '11', 'tsv'], input=png,
                         capture_output=True, env=dict(os.environ, OMP_THREAD_LIMIT='1')).stdout.decode('utf-8', 'ignore')
    res = []
    for r in csv.DictReader(io.StringIO(out), delimiter='\t', quoting=csv.QUOTE_NONE):
        t = (r.get('text') or '').strip()
        if not t:
            continue
        x, y, w, h = (int(r[k]) for k in ('left', 'top', 'width', 'height'))
        res.append([int(X0 + x / ESC), int(Y0 + y / ESC), int(X0 + (x + w) / ESC), int(Y0 + (y + h) / ESC),
                    t, round(float(r['conf']), 1)])
    return res


def caixas_nitidas(palavras):
    """Linhas em que TODAS as palavras são rótulo conhecido do app (sem dígitos)."""
    res = []
    for ln in linhas(palavras):
        estados = [palavra_ok(t, c) for *_, t, c in ln]
        if False in estados or True not in estados:
            continue
        if sum(len(t) for *_, t, c in ln) < 4:
            continue
        res.append([min(w[0] for w in ln) - 2, min(w[1] for w in ln) - 2,
                    max(w[2] for w in ln) + 2, max(w[3] for w in ln) + 2])
    return res


def estado_numero(t, c, ant):
    """'n' = número que pode aparecer (data, contagem até 3 dígitos fora de dinheiro);
    'x' = dinheiro, %, telefone, CEP, CPF, ID, ou leitura duvidosa."""
    nucleo = t.strip('()[]{}.,;:·•-–')
    if c < 80 or '%' in t or 'R$' in t or (ant or '').strip().upper() in ('R$', 'RS', 'R$.', '-R$'):
        return 'x'
    if re.fullmatch(r'\d{1,2}/\d{1,2}(/\d{2,4})?', nucleo):
        return 'n'
    if re.fullmatch(r'\d{1,3}', nucleo):
        return 'n'
    return 'x'


def classifica(ln):
    """Estado de cada palavra da linha (ordenada da esquerda p/ direita)."""
    est = []
    for i, (x0, y0, x1, y1, t, c) in enumerate(ln):
        limpa = ''.join(ch for ch in t if ch.isalnum())
        if any(ch.isdigit() for ch in limpa):
            est.append(estado_numero(t, c, ln[i - 1][4] if i else None))
            continue
        ok = palavra_ok(t, c)
        if ok is True and c >= 72 and len(limpa) >= 2:
            est.append('p')
        elif ok is None and len(limpa) == 1 and limpa.isalpha() and c >= 72:
            est.append('l')
        elif ok is None and not limpa:
            est.append('-')                       # pontuação solta
        else:
            est.append('x')
    return est


def _vizinhos(est, ln, i):
    """Estados das palavras vizinhas (ignora pontuação solta)."""
    viz = []
    for d in (-1, 1):
        j = i + d
        while 0 <= j < len(ln) and est[j] == '-':
            j += d
        if 0 <= j < len(ln):
            viz.append(j)
    return viz


def classifica_seguro(ln):
    """Como classifica(), mas número só fica se não encostar em outro número nem em
    palavra borrada (telefone quebrado em pedaços, número de endereço)."""
    est = classifica(ln)
    for i, (x0, y0, x1, y1, t, c) in enumerate(ln):
        if est[i] == 'n':
            for j in _vizinhos(est, ln, i):
                tj = ln[j][4]
                if est[j] == 'x' or any(ch.isdigit() for ch in tj):
                    est[i] = 'x'
    return est


def caixas_palavras(palavras):
    """Nítidas: palavras de vocabulário genérico (app, fala, nome da loja) e números
    liberados; letra solta só no meio de frase conhecida. A primeira palavra da
    linha ganha espaço à esquerda para o ícone."""
    res = []
    for ln in linhas(palavras):
        ln = sorted(ln, key=lambda w: w[0])
        est = classifica_seguro(ln)
        for i, (x0, y0, x1, y1, t, c) in enumerate(ln):
            if est[i] in ('x', '-'):
                continue
            if est[i] == 'l' and not (0 < i < len(ln) - 1 and est[i - 1] in 'pn' and est[i + 1] in 'pn'):
                continue
            ex = int(1.3 * (y1 - y0)) if (i == 0 and est[i] == 'p') else 0
            res.append([x0 - 2 - ex, y0 - 2, x1 + 2, y1 + 2])
    return res


def caixas_proibidas(palavras):
    """Palavras desconhecidas lidas com alguma confiança (título de anúncio, nome,
    endereço, valor): sempre desfocadas, mesmo dentro de foto liberada."""
    res = []
    for ln in linhas(palavras):
        ln = sorted(ln, key=lambda w: w[0])
        est = classifica_seguro(ln)
        for i, (x0, y0, x1, y1, t, c) in enumerate(ln):
            if est[i] == 'x' and c >= 40:
                res.append([x0 - 4, y0 - 4, x1 + 4, y1 + 4])
    return res


def trecho(args):
    q0, q1 = args
    dest = os.path.join(OUT, '%05d.json' % q0)
    if os.path.exists(dest):
        return dest
    n = (q1 - q0 + PASSO - 1) // PASSO
    cmd = ['ffmpeg', '-v', 'error', '-ss', '%.6f' % (q0 / 30), '-i', SRC, '-vf',
           'select=not(mod(n\\,%d)),crop=%d:%d:%d:%d,format=gray,scale=%d:%d:flags=bicubic'
           % (PASSO, X1 - X0, Y1 - Y0, X0, Y0, CW, CH),
           '-fps_mode', 'passthrough', '-frames:v', str(n), '-f', 'rawvideo', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    res = {}
    for k in range(n):
        buf = p.stdout.read(CW * CH)
        if len(buf) < CW * CH:
            break
        img = np.frombuffer(buf, np.uint8).reshape(CH, CW)
        res[q0 + k * PASSO] = palavras_ocr(img)
    p.wait()
    json.dump(res, open(dest, 'w'))
    return dest


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    TAM = PASSO * 50
    partes = [(q, min(q + TAM, NQ)) for q in range(0, NQ, TAM)]
    with ProcessPoolExecutor(9) as ex:
        for i, d in enumerate(ex.map(trecho, partes)):
            if i % 10 == 0:
                print(i, '/', len(partes), d, flush=True)
    print('fim')
