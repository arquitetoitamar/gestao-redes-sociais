"""OCR dos quadros (1 por segundo, recorte da tela escalado 1,5x) para achar dado sensível.

uso: python3 ocr_scan.py trab/ocr3 3  -> trab/ocr3_hits.json  (pasta, quadros por segundo)
Cada hit: {"t": segundo, "texto": linha, "caixa": [x0,y0,x1,y1] em coordenadas do bruto 1920x1080}
"""
import csv, glob, io, json, os, re, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

PASTA = sys.argv[1]
OX, OY, ESC = 62, 74, 1.5          # recorte crop=1590:894:62:74, escala 1,5
FPS = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
SENS = re.compile(r'isantos|keiprod|kei\s?prod|\bKEI\b|achadinhos|\b1\d\d\.1\d\d\.\d{1,3}\.\d{1,3}\b|[\w.]+@[\w-]+\.\w+|'
                  r'gmail|hotmail|ads\s?team|\+?\d[\d\s().-]{9,}\d|cpf|cnpj')


def um(arq):
    t = round((int(os.path.basename(arq)[2:7]) - 1) / FPS, 3)
    out = subprocess.run(['tesseract', arq, '-', '--psm', '11', 'tsv'], capture_output=True, text=True).stdout
    linhas = {}
    for r in csv.DictReader(io.StringIO(out), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r.get('level') != '5' or not (r.get('text') or '').strip():
            continue
        x, y, w, h = (int(r[k]) for k in ('left', 'top', 'width', 'height'))
        linhas.setdefault((r['block_num'], r['par_num'], r['line_num']), []).append((x, y, x + w, y + h, r['text']))
    hits = []
    for ws in linhas.values():
        txt, pos = '', []
        for w in ws:                       # posição de cada palavra dentro da linha
            if txt:
                txt += ' '
            pos.append((len(txt), len(txt) + len(w[4])))
            txt += w[4]
        for m in SENS.finditer(txt):
            if re.fullmatch(r'[\d\s().+-]+', m.group()) and len(re.sub(r'\D', '', m.group())) < 10:
                continue
            for w, (a, b) in zip(ws, pos):
                if a < m.end() and b > m.start():
                    hits.append({'t': t, 'texto': txt, 'palavra': m.group(),
                                 'caixa': [round(OX + w[0] / ESC), round(OY + w[1] / ESC),
                                           round(OX + w[2] / ESC), round(OY + w[3] / ESC)]})
    return hits


if __name__ == '__main__':
    arqs = sorted(glob.glob(os.path.join(PASTA, 's_*.jpg')))
    todos = []
    with ProcessPoolExecutor(4) as ex:
        for i, h in enumerate(ex.map(um, arqs, chunksize=8)):
            todos.extend(h)
            if i % 200 == 0:
                print(i, len(todos), flush=True)
    json.dump(todos, open(os.path.join(os.path.dirname(PASTA.rstrip('/')), os.path.basename(PASTA.rstrip('/')) + '_hits.json'), 'w'), ensure_ascii=False)
    print('quadros', len(arqs), 'hits', len(todos))
