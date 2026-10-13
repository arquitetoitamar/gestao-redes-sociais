import glob, os, re, subprocess, sys, json

DIR, OFF, FPS = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
# o token da chave: qualquer palavra com "live_", "key=" ou "/mcp?"
PAD = re.compile(r'(mc_?live|key\s*=|mcp\?|m[ce]_l)', re.I)

achados = {}
for p in sorted(glob.glob(os.path.join(DIR, 'f_*.jpg'))):
    n = int(re.search(r'f_(\d+)', p).group(1))
    t = OFF + (n - 1) / FPS
    tsv = subprocess.run(['tesseract', p, 'stdout', '--psm', '6', 'tsv'],
                         capture_output=True, text=True).stdout
    for linha in tsv.splitlines()[1:]:
        c = linha.split('\t')
        if len(c) < 12:
            continue
        txt = c[11].strip()
        if len(txt) < 12 or not PAD.search(txt):
            continue
        x, y, w, h = int(c[6]), int(c[7]), int(c[8]), int(c[9])
        if w < 120:
            continue
        achados.setdefault(round(t, 1), []).append((x, y, w, h, txt[:28] + '…'))

json.dump(achados, open('chave_por_tempo.json', 'w'), indent=1)
for t in sorted(achados, key=float):
    for b in achados[t]:
        print('%7.1fs  x=%4d y=%4d %4dx%-3d  %s' % (float(t), b[0], b[1], b[2], b[3], b[4]))
