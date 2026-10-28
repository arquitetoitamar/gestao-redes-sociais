#!/usr/bin/env python3
"""Auditoria de privacidade do vídeo final: OCR a cada 0,5 s na área da tela
gravada (fora de B-roll, painel lateral, cartão de pedido, abertura e final) e
lista qualquer palavra legível que não seja rótulo do app, e qualquer número.

  python3 auditoria.py     -> trab/auditoria.json + resumo na tela
"""
import json, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np, cv2
import ocr, render

AQUI = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(AQUI, 'videos', 'final.mp4')
X0, Y0, X1, Y1 = render.WIN
CAMX = render.CAM[0]


def tela_pura(t, cam):
    if cam.broll_em(t) or cam.lateral_em(t):
        return False
    for a, b, _ in cam.prompts:
        if a - 0.5 <= t < b + 0.5:
            return False
    return True


def checa(args):
    tf, img = args
    ws = ocr.palavras_ocr(img)
    achados = []
    for x0, y0, x1, y1, t, c in ws:
        if x0 >= CAMX - 4 and y0 >= render.CAM[1] - 4:
            continue                            # balão da câmera
        limpa = ''.join(ch for ch in t if ch.isalnum())
        if c < 80 or len(limpa) < 3:
            continue
        if any(ch.isdigit() for ch in limpa):
            if ocr.estado_numero(t, c, None) == 'x':
                achados.append([round(tf, 1), t, c, [x0, y0]])
        elif ocr.palavra_ok(t, c) is False and len(limpa) >= 4:
            achados.append([round(tf, 1), t, c, [x0, y0]])
    return achados


def main():
    tempos = json.load(open(os.path.join(AQUI, 'trab', 'tempos.json')))
    ab = tempos['abertura_s']
    cam = render.Camadas()
    alvos = [ab + k * 0.5 for k in range(int(render.DUR / 0.5))]
    alvos = [t for t in alvos if tela_pura(t - ab, cam)]
    validos = {int(round(t * 30)) for t in alvos}
    cmd = ['ffmpeg', '-v', 'error', '-i', FINAL, '-vf',
           "select='not(mod(n\\,15))',crop=%d:%d:%d:%d,format=gray,scale=%d:%d" % (X1 - X0, Y1 - Y0, X0, Y0, ocr.CW, ocr.CH),
           '-fps_mode', 'passthrough', '-f', 'rawvideo', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    lidos = [0]

    def quadros():
        n = 0
        while True:
            b = p.stdout.read(ocr.CW * ocr.CH)
            if len(b) < ocr.CW * ocr.CH:
                return
            if n in validos:
                lidos[0] += 1
                yield (n / 30, np.frombuffer(b, np.uint8).reshape(ocr.CH, ocr.CW))
            n += 15
    todos = []
    with ProcessPoolExecutor(9) as ex:
        for r in ex.map(checa, quadros(), chunksize=4):
            todos += r
    json.dump(todos, open(os.path.join(AQUI, 'trab', 'auditoria.json'), 'w'), ensure_ascii=False)
    print('quadros auditados:', lidos[0], 'de', len(alvos), '| achados:', len(todos))
    for a in todos[:80]:
        print(a)


if __name__ == '__main__':
    main()
