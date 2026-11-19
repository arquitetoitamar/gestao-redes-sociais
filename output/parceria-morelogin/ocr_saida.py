"""OCR no vídeo JÁ EDITADO (texto maior, zoom aplicado) e devolve as caixas para o tempo/coordenada do BRUTO.

Necessário porque na gravação original o texto claro da janela escura do Claude sai pequeno demais para o OCR.
uso: python3 ocr_saida.py [video] [fps] [saida.json] [janelas.json]  -> trab/ocr_saida_hits.json
janelas.json (opcional): [[ini, fim], ...] em segundos do vídeo editado; só esses trechos são lidos.
"""
import csv, glob, io, json, os, re, shutil, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import monta as M

VIDEO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'morelogin_final.mp4')
FPS = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
PASTA = os.path.join(AQUI, 'trab', 'ocr_saida')
ESC = 1.25
SENS = re.compile(r'isantos|keiprod|kei\s?prod|\bKEI\b|achadinhos|ads\s?team|\b1\d\d\.1\d\d\.\d{1,3}\.\d{1,3}\b|'
                  r'[\w.]+@[\w-]+\.\w+|gmail|\+?\d[\d\s().-]{9,}\d', re.I)


def um(arq):
    to = round((int(os.path.basename(arq)[2:8]) - 1) / FPS, 3)
    out = subprocess.run(['tesseract', arq, '-', '--psm', '11', 'tsv'], capture_output=True, text=True).stdout
    linhas = {}
    for r in csv.DictReader(io.StringIO(out), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r.get('level') != '5' or not (r.get('text') or '').strip():
            continue
        x, y, w, h = (int(r[k]) for k in ('left', 'top', 'width', 'height'))
        linhas.setdefault((r['block_num'], r['par_num'], r['line_num']), []).append(
            (x / ESC, y / ESC, (x + w) / ESC, (y + h) / ESC, r['text']))
    hits = []
    for ws in linhas.values():
        txt, pos = '', []
        for w in ws:
            if txt:
                txt += ' '
            pos.append((len(txt), len(txt) + len(w[4])))
            txt += w[4]
        for m in SENS.finditer(txt):
            g = m.group()
            if 'morelogin.com' in txt.lower() or re.search(r'20\d\d-\d\d-\d\d|\d\d-\d\d-20\d\d', g):
                continue
            if re.fullmatch(r'[\d\s().+-]+', g) and len(re.sub(r'\D', '', g)) < 10:
                continue
            for w, (a, b) in zip(ws, pos):
                if a < m.end() and b > m.start():
                    hits.append({'to': to, 'palavra': g, 'caixa_saida': [round(v) for v in w[:4]]})
    return hits


def para_bruto(hits):
    e = json.load(open(M.T('edl.json')))
    ch = M.plano_zoom(e)
    saida = []
    for h in hits:
        f = h['to'] * M.FPS
        ts = None
        for s in e:
            if s['oa'] <= f < s['oa'] + s['fb'] - s['fa']:
                ts = (s['fa'] + f - s['oa']) / M.FPS
                break
        if ts is None:
            continue
        x0, y0, x1, y1 = M.rect_em(ch, h['to'])
        kx, ky = (x1 - x0) / M.W, (y1 - y0) / M.H
        cx = h['caixa_saida']
        # a câmera e os motions não são tela: ignora o que cair em cima deles
        if cx[0] > M.CAM_POS[0] - 20 and cx[1] > M.CAM_POS[1] - 20:
            continue
        saida.append({'t': round(ts, 3), 'palavra': h['palavra'],
                      'caixa': [round(x0 + cx[0] * kx), round(y0 + cx[1] * ky), round(x0 + cx[2] * kx), round(y0 + cx[3] * ky)]})
    return saida


if __name__ == '__main__':
    SAIDA = sys.argv[3] if len(sys.argv) > 3 else 'ocr_saida_hits.json'
    JANELAS = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
    shutil.rmtree(PASTA, ignore_errors=True)
    os.makedirs(PASTA)
    if JANELAS:
        # extrai cada janela com a numeração global (quadro = round(t*FPS)+1) para o tempo continuar certo
        for a, b in JANELAS:
            tmp = os.path.join(PASTA, 'tmp')
            os.makedirs(tmp, exist_ok=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', VIDEO, '-vf',
                            f'fps={FPS},scale={int(1920 * ESC)}:{int(1080 * ESC)}:flags=lanczos', '-q:v', '3',
                            os.path.join(tmp, 'x_%06d.jpg')], check=True)
            for k, f in enumerate(sorted(glob.glob(os.path.join(tmp, 'x_*.jpg')))):
                os.rename(f, os.path.join(PASTA, 's_%06d.jpg' % (round(a * FPS) + k + 1)))
            shutil.rmtree(tmp)
    else:
        subprocess.run(['ffmpeg', '-v', 'error', '-i', VIDEO, '-vf', f'fps={FPS},scale={int(1920 * ESC)}:{int(1080 * ESC)}:flags=lanczos',
                        '-q:v', '3', os.path.join(PASTA, 's_%06d.jpg')], check=True)
    arqs = sorted(glob.glob(os.path.join(PASTA, 's_*.jpg')))
    todos = []
    with ProcessPoolExecutor(4) as ex:
        for i, h in enumerate(ex.map(um, arqs, chunksize=8)):
            todos.extend(h)
            if i % 500 == 0:
                print(i, len(todos), flush=True)
    br = para_bruto(todos)
    json.dump(br, open(M.T(SAIDA), 'w'), ensure_ascii=False)
    print('quadros', len(arqs), '| hits', len(todos), '| no bruto', len(br))
