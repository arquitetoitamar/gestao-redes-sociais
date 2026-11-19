"""Zoom automático a partir do mapa de atividade (trab/atividade.json), no tempo do BRUTO.

Regra: janela de 2,5 s; se o que mudou cabe num retângulo pequeno, aproxima nele (16:9, com folga);
se a tela inteira mudou (troca de página), volta para a vista cheia. Cada estado dura no mínimo 3 s.
Saída: trab/zoom.json  [{"ini": s, "fim": s, "rect": [x0,y0,x1,y1]}]  (rect no bruto; vista cheia = TELA)
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
TELA = [62, 74, 1652, 968]            # 1590 x 894 (16:9)
ZOOM_MAX = 1.85                       # sobre a vista cheia
MIN_W = (TELA[2] - TELA[0]) / ZOOM_MAX
FOLGA = 70
JAN = 2.5
MIN_DUR = 3.0
# piscas que não são conteúdo: selo "Renovação" do MoreLogin (canto inferior esquerdo)
IGNORA = [[125, 840, 240, 895]]
MIN_ZOOM = 6          # zoom mais curto que isso vira vista cheia
MIN_CHEIO = 4         # vista cheia mais curta que isso entre dois zooms parecidos é absorvida


def rect_169(x0, y0, x1, y1):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w = max(x1 - x0 + 2 * FOLGA, (y1 - y0 + 2 * FOLGA) * 16 / 9, MIN_W)
    w = min(w, TELA[2] - TELA[0])
    h = w * 9 / 16
    x0 = min(max(cx - w / 2, TELA[0]), TELA[2] - w)
    y0 = min(max(cy - h / 2, TELA[1]), TELA[3] - h)
    return [round(x0), round(y0), round(x0 + w), round(y0 + h)]


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    return i / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i)


def main():
    at = json.load(open(os.path.join(AQUI, 'trab', 'atividade.json')))
    fps = 5
    n = len(at)
    alvo = []                         # um alvo por segundo
    for s in range(int(n / fps)):
        js = range(max(0, int((s - JAN / 2) * fps)), min(n, int((s + JAN / 2) * fps)))
        cx = [c[:4] for j in js for c in at[j].get('comps', [])
              if not any(c[0] >= g[0] and c[1] >= g[1] and c[2] <= g[2] and c[3] <= g[3] for g in IGNORA)]
        if sum((c[2] - c[0]) * (c[3] - c[1]) for c in cx) < 900:
            cx = []
        if not cx:
            alvo.append(None)         # parado: mantém o que estiver
            continue
        u = [min(c[0] for c in cx), min(c[1] for c in cx), max(c[2] for c in cx), max(c[3] for c in cx)]
        r = rect_169(*u)
        larg = (r[2] - r[0]) / (TELA[2] - TELA[0])
        alvo.append(TELA if larg > 0.8 else r)
    # segmentos
    segs = []
    atual = TELA
    for s, a in enumerate(alvo):
        if a is None:
            a = atual
        if segs and (iou(a, segs[-1]['rect']) > 0.55 or s - segs[-1]['ini'] < MIN_DUR):
            segs[-1]['fim'] = s + 1
            continue
        segs.append({'ini': s, 'fim': s + 1, 'rect': a})
        atual = a
    # 1) zoom curto vira vista cheia
    for x in segs:
        if x['rect'] != TELA and x['fim'] - x['ini'] < MIN_ZOOM:
            x['rect'] = TELA
    # 2) funde vizinhos iguais; zooms vizinhos parecidos viram um só (retângulo que cobre os dois, se couber)
    def junta(segs):
        out = []
        for x in segs:
            if out and out[-1]['rect'] == x['rect']:
                out[-1]['fim'] = x['fim']; continue
            if out and out[-1]['rect'] != TELA and x['rect'] != TELA:
                a, b = out[-1]['rect'], x['rect']
                u = rect_169(min(a[0], b[0]) + FOLGA, min(a[1], b[1]) + FOLGA, max(a[2], b[2]) - FOLGA, max(a[3], b[3]) - FOLGA)
                if (u[2] - u[0]) / (TELA[2] - TELA[0]) <= 0.72:
                    out[-1]['rect'] = u; out[-1]['fim'] = x['fim']; continue
            out.append(dict(x))
        return out
    segs = junta(segs)
    # 3) vista cheia curta entre dois zooms: absorve (pan direto)
    for i in range(1, len(segs) - 1):
        x = segs[i]
        if x['rect'] == TELA and x['fim'] - x['ini'] < MIN_CHEIO and segs[i-1]['rect'] != TELA and segs[i+1]['rect'] != TELA:
            x['rect'] = segs[i-1]['rect']
    segs = junta(segs)
    json.dump(segs, open(os.path.join(AQUI, 'trab', 'zoom.json'), 'w'))
    cheio = sum(x['fim'] - x['ini'] for x in segs if x['rect'] == TELA)
    print('segmentos', len(segs), '| vista cheia', cheio, 's de', len(alvo))


if __name__ == '__main__':
    main()
