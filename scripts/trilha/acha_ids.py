import glob, os, re, subprocess, sys, json

DIR = sys.argv[1]
OFF = int(sys.argv[2])          # segundo do clipe correspondente a f_001
ALVO = re.compile(r'\d{7,}')    # qualquer corrida de 7+ dígitos

achados = {}
for p in sorted(glob.glob(os.path.join(DIR, 'f_*.jpg'))):
    n = int(re.search(r'f_(\d+)', p).group(1))
    t = OFF + n - 1
    tsv = subprocess.run(['tesseract', p, 'stdout', '--psm', '6', 'tsv'],
                         capture_output=True, text=True).stdout
    caixas = []
    for linha in tsv.splitlines()[1:]:
        c = linha.split('\t')
        if len(c) < 12:
            continue
        txt = c[11].strip()
        if not ALVO.search(txt):
            continue
        if len(re.sub(r'\D', '', txt)) < 7:
            continue
        x, y, w, h = (int(c[6]), int(c[7]), int(c[8]), int(c[9]))
        if w < 40 or h < 8 or h > 60:
            continue
        caixas.append((x, y, w, h, txt))
    if caixas:
        achados[t] = caixas

json.dump(achados, open('ids_por_segundo.json', 'w'), indent=1)
for t in sorted(achados):
    print(t, [(b[0], b[1], b[2], b[3], b[4]) for b in achados[t]])
