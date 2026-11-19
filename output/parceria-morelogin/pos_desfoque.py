"""Último passe: OCR em cada quadro do vídeo JÁ editado, nas janelas indicadas, e desfoque no próprio quadro.

Detecta e desfoca no mesmo quadro (±2 quadros), então não depende de prever para onde o texto rolou.
uso: python3 pos_desfoque.py <entrada.mp4> <saida.mp4> <janelas: ini-fim,ini-fim (s, tempo do arquivo)>
"""
import csv, glob, io, os, re, shutil, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import monta as M

ENT, SAI = sys.argv[1], sys.argv[2]
JAN = [tuple(float(v) for v in j.split('-')) for j in sys.argv[3].split(',')]
FPS, W, H = 30, 1920, 1080
ESC = float(os.environ.get("ESC", "1.25"))
PASTA = M.T('pos_ocr')
SENS = re.compile(r'isantos|keiprod|kei\s?prod|\bKEI\b|achadinhos|ads\s?team|\b1\d\d\.1\d\d\.\d{1,3}\.\d{1,3}\b|'
                  r'[\w.]+@[\w-]+\.(com|br)|\+?55\s?\d{2}\s?9?\d{3,4}|\+?\d[\d\s().-]{9,}\d', re.I)


def ocr(arq):
    n = int(os.path.basename(arq)[2:9])
    out = subprocess.run(['tesseract', arq, '-', '--psm', '11', 'tsv'], capture_output=True, text=True).stdout
    linhas = {}
    for r in csv.DictReader(io.StringIO(out), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r.get('level') != '5' or not (r.get('text') or '').strip():
            continue
        x, y, w, h = (int(r[k]) for k in ('left', 'top', 'width', 'height'))
        linhas.setdefault((r['block_num'], r['par_num'], r['line_num']), []).append(
            (x / ESC, y / ESC, (x + w) / ESC, (y + h) / ESC, r['text']))
    caixas = []
    for ws in linhas.values():
        txt, pos = '', []
        for w in ws:
            if txt:
                txt += ' '
            pos.append((len(txt), len(txt) + len(w[4])))
            txt += w[4]
        if 'morelogin.com' in txt.lower():
            continue
        for m in SENS.finditer(txt):
            g = m.group()
            if re.search(r'20\d\d-\d\d-\d\d|\d\d-\d\d-20\d\d', g):
                continue
            if re.fullmatch(r'[\d\s().+-]+', g) and len(re.sub(r'\D', '', g)) < 10 and not g.lstrip().startswith('+55'):
                continue
            for w, (a, b) in zip(ws, pos):
                if a < m.end() and b > m.start():
                    caixas.append([int(w[0]) - 6, int(w[1]) - 4, int(w[2]) + 6, int(w[3]) + 4])
    return n, caixas


def main():
    shutil.rmtree(PASTA, ignore_errors=True)
    os.makedirs(PASTA)
    for a, b in JAN:
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', ENT, '-vf',
                        f'scale={int(W * ESC)}:{int(H * ESC)}:flags=lanczos', '-q:v', '3',
                        os.path.join(PASTA, 'tmp_%07d.jpg')], check=True)
        for k, f in enumerate(sorted(glob.glob(os.path.join(PASTA, 'tmp_*.jpg')))):
            os.rename(f, os.path.join(PASTA, 'q_%07d.jpg' % (round(a * FPS) + k)))
    arqs = sorted(glob.glob(os.path.join(PASTA, 'q_*.jpg')))
    por_quadro = {}
    with ProcessPoolExecutor(4) as ex:
        for n, cx in ex.map(ocr, arqs, chunksize=8):
            if cx:
                por_quadro[n] = cx
    print('quadros lidos', len(arqs), '| com dado', len(por_quadro), flush=True)
    shutil.rmtree(PASTA, ignore_errors=True)
    # aplica: cada quadro recebe as caixas dele e dos 2 vizinhos de cada lado
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', ENT, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-g', '60', SAI],
                           stdin=subprocess.PIPE)
    n, tam = 0, W * H * 3
    while True:
        b = dec.stdout.read(tam)
        if len(b) < tam:
            break
        viz = int(os.environ.get('VIZ', '2'))
        cx = [c for k in range(n - viz, n + viz + 1) for c in por_quadro.get(k, [])]
        if cx:
            q = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
            b = M.desfoca(q, [[max(0, c[0]), max(0, c[1]), min(W, c[2]), min(H, c[3])] for c in cx]).tobytes()
        enc.stdin.write(b)
        n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print('quadros', n, '->', SAI)


if __name__ == '__main__':
    main()
