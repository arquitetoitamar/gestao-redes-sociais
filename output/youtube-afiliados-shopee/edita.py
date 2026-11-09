"""Passo 1 da edição do vídeo "Afiliado Shopee no ChatGPT" (gravação de tela de 15 min).

- Acelera 4x as esperas em silêncio (> 3 s), mantendo 0,4 s normais em cada ponta; o áudio original
  fica intacto nos trechos falados (regra: sem denoise, EQ ou música na voz do Itamar).
- Desfoca o que não pode ir a público: nomes e IDs de lojas no painel do Marketplace Connect e na lista
  de integrações, e a lista de projetos/conversas na lateral do ChatGPT.
- Gera trab/base.mp4 e trab/edl.json (mapa tempo original -> tempo editado, usado pelos motions e capítulos).

uso: python3 edita.py <video_original> <pasta_trab>"""
import json, os, subprocess, sys

SRC, TRAB = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(TRAB, 'seg'), exist_ok=True)
DUR = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC],
                           capture_output=True, text=True).stdout)
FAST, BORDA = 4.0, 0.4

# esperas em silêncio (silencedetect -38 dB, >= 3 s), em segundos do original
SIL = [(30.9, 34.3), (202.2, 207.3), (249.3, 253.4), (346.0, 353.1), (495.5, 498.7), (561.2, 564.2),
       (572.4, 580.4), (624.7, 629.4), (646.1, 653.1), (663.5, 668.8), (691.6, 695.2), (726.9, 730.3),
       (734.2, 740.6), (778.2, 796.3), (801.4, 805.6), (824.4, 829.1), (880.7, 884.1), (897.3, 902.5)]

# desfoques (tempo do original, retângulo x, y, w, h em 1920x1080)
CARD = (60, 150, 1590, 820)
BLUR = [
    (42.5, 57.0, (370, 560, 1180, 340), None),                 # lista "Suas lojas" no painel
    (57.0, 94.5, CARD, (646, 220, 424, 700)),                   # lista escurecida atrás das janelas; janela nítida
    (94.5, 102.5, (390, 460, 1120, 510), None),                 # lista "Suas integrações"
]
for a, b in json.load(open(os.path.join(TRAB, 'sidebar_win.json'))):   # lateral do ChatGPT (projetos e conversas)
    BLUR.append((a, b, (66, 440, 250, 500), None))

# EDL: trechos normais e trechos acelerados
edl, t = [], 0.0
for a, b in SIL:
    fa, fb = a + BORDA, b - BORDA
    if fa > t: edl.append([t, fa, 1.0])
    edl.append([fa, fb, FAST]); t = fb
edl.append([t, DUR, 1.0])
out = 0.0
for e in edl:
    e.append(round(out, 3)); out += (e[1] - e[0]) / e[2]
json.dump({'segmentos': [dict(ini=a, fim=b, vel=v, saida=o) for a, b, v, o in edl], 'duracao': out},
          open(os.path.join(TRAB, 'edl.json'), 'w'), indent=1)
print('trechos', len(edl), 'duração editada %.1f s (original %.1f s)' % (out, DUR))

def grafo(a, b, vel):
    """filtergraph do trecho [a, b] do original: desfoques com tempo relativo ao trecho."""
    ws = [(max(w0, a) - a, min(w1, b) - a, r, s) for w0, w1, r, s in BLUR if w0 < b and w1 > a]
    g, cur = [], '0:v'
    for k, (w0, w1, (x, y, w, h), sharp) in enumerate(ws):
        en = "enable='between(t,%.3f,%.3f)'" % (w0, w1)
        g.append('[%s]split=%d[b%d][c%d]%s' % (cur, 3 if sharp else 2, k, k, '[s%d]' % k if sharp else ''))
        g.append('[c%d]crop=%d:%d:%d:%d,boxblur=22:3[bl%d]' % (k, w, h, x, y, k))
        g.append('[b%d][bl%d]overlay=%d:%d:%s[o%d]' % (k, k, x, y, en, k))
        cur = 'o%d' % k
        if sharp:
            sx, sy, sw, sh = sharp
            g.append('[s%d]crop=%d:%d:%d:%d[sc%d]' % (k, sw, sh, sx, sy, k))
            g.append('[o%d][sc%d]overlay=%d:%d:%s[p%d]' % (k, k, sx, sy, en, k))
            cur = 'p%d' % k
    g.append('[%s]setpts=(PTS-STARTPTS)/%g,fps=30,format=yuv420p[v]' % (cur, vel))
    return ';'.join(g)

lista = []
for i, (a, b, vel, o) in enumerate(edl):
    arq = os.path.join(TRAB, 'seg', '%03d.ts' % i)
    lista.append("file '%s'" % os.path.abspath(arq))
    if os.path.exists(arq): continue
    dur = b - a
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % a, '-t', '%.3f' % dur, '-i', SRC]
    if vel != 1.0:
        cmd += ['-f', 'lavfi', '-t', '%.3f' % (dur / vel), '-i', 'anullsrc=r=48000:cl=stereo']
        amap = '1:a'
    else:
        amap = '0:a'
    cmd += ['-filter_complex', grafo(a, b, vel), '-map', '[v]', '-map', amap,
            '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-r', '30', '-g', '60',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest', '-f', 'mpegts', arq]
    subprocess.run(cmd, check=True)
    print('trecho %d/%d ok' % (i + 1, len(edl)), flush=True)
open(os.path.join(TRAB, 'lista.txt'), 'w').write('\n'.join(lista) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(TRAB, 'lista.txt'),
                '-c', 'copy', '-movflags', '+faststart', os.path.join(TRAB, 'base.mp4')], check=True)
print('base.mp4 pronto')
