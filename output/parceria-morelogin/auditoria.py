"""Relê o vídeo final e procura dado de conta que tenha escapado do desfoque.

uso: python3 auditoria.py [video] [fps]  -> trab/auditoria.json e lista no terminal
"""
import csv, glob, io, json, os, re, shutil, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
VIDEO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'morelogin_final.mp4')
FPS = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
PASTA = os.path.join(AQUI, 'trab', 'aud')
SENS = re.compile(r'isantos|keiprod|kei\s?prod|\bKEI\b|achadinhos|ads\s?team|\b177\.172|\+?55\s?11\s?9?\d{4}|'
                  r'[\w.]+@[\w-]+\.(com|br)|gmail', re.I)


def um(arq):
    t = round((int(os.path.basename(arq)[2:8]) - 1) / FPS, 2)
    out = subprocess.run(['tesseract', arq, '-', '--psm', '11', 'tsv'], capture_output=True, text=True).stdout
    achados = []
    for r in csv.DictReader(io.StringIO(out), delimiter='\t', quoting=csv.QUOTE_NONE):
        tx = (r.get('text') or '').strip()
        if r.get('level') == '5' and tx and SENS.search(tx):
            achados.append({'t': t, 'texto': tx, 'x': int(r['left']) / 1.25, 'y': int(r['top']) / 1.25})
    return achados


if __name__ == '__main__':
    shutil.rmtree(PASTA, ignore_errors=True)
    os.makedirs(PASTA)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', VIDEO, '-vf', f'fps={FPS},scale=2400:1350:flags=lanczos', '-q:v', '3',
                    os.path.join(PASTA, 's_%06d.jpg')], check=True)
    arqs = sorted(glob.glob(os.path.join(PASTA, 's_*.jpg')))
    todos = []
    with ProcessPoolExecutor(4) as ex:
        for h in ex.map(um, arqs, chunksize=8):
            todos.extend(h)
    json.dump(todos, open(os.path.join(AQUI, 'trab', 'auditoria.json'), 'w'), ensure_ascii=False, indent=0)
    print('quadros', len(arqs), '| suspeitos', len(todos))
    for a in todos:
        print('%d:%05.2f  %-30s  (%d,%d)' % (a['t'] // 60, a['t'] % 60, a['texto'], a['x'], a['y']))
