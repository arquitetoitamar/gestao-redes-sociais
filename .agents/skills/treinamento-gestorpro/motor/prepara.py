#!/usr/bin/env python3
"""Monta as peças da tela a partir das capturas (retina, 2 px por ponto):

- capturas/pagina.png   área principal inteira (rolagem costurada), 2468 px de largura
- capturas/moldura16x9.png  barra do topo + menu lateral numa tela 16:9 (2940x1654),
                            com a área principal vazia (a página entra por baixo)
"""
import glob, os
import numpy as np
from PIL import Image

import sys
AQUI = os.path.abspath(sys.argv[1])
C = os.path.join(AQUI, 'capturas')
X0, Y0 = 472, 104          # canto da área principal (236 x 52 pt)
W, H16 = 2940, 1654        # tela 16:9 em retina (1470 x 827 pt)


def confere(ims):
    """faixas vizinhas têm de mostrar o mesmo trecho da página; se não, a página mudou entre capturas"""
    ok = True
    for (s0, a), (s1, b) in zip(ims, ims[1:]):
        a, b = np.asarray(a.convert('L')).astype(np.int16), np.asarray(b.convert('L')).astype(np.int16)
        hi, lo = s0 + (a.shape[0] - Y0) // 2, s1
        if hi <= lo:
            print('BURACO entre', s0, 'e', s1); ok = False; continue
        ya, yb = Y0 + (lo - s0) * 2, Y0
        n = min((hi - lo) * 2, b.shape[0] - yb, a.shape[0] - ya)
        d = np.abs(a[ya:ya + n, X0:W - 40] - b[yb:yb + n, X0:W - 40]).mean()
        if d > 2:
            print('NÃO BATE: faixa %d x %d (diferença %.1f) — recapture a de baixo' % (s0, s1, d)); ok = False
    return ok


def main():
    fs = sorted(glob.glob(os.path.join(C, 'faixa-*.png')), key=lambda f: int(f[-9:-4]))
    ims = [(int(f[-9:-4]), Image.open(f)) for f in fs]
    if not confere(ims):
        print('atenção: a costura vai ter emendas erradas; tire a faixa ruim de capturas/ e recapture')
    alto = (ims[-1][0] * 2) + (ims[-1][1].size[1] - Y0)
    pagina = Image.new('RGB', (W - X0, alto), (250, 250, 250))
    for s, im in ims:
        pagina.paste(im.crop((X0, Y0, W, im.size[1])), (0, s * 2))
    vh = ims[0][1].size[1]
    pagina.save(os.path.join(C, 'pagina.png'))
    base = ims[0][1]
    mold = Image.new('RGB', (W, H16), (250, 250, 250))
    mold.paste(base.crop((0, 0, W, Y0)), (0, 0))
    lat = np.asarray(base.crop((0, Y0, X0, vh)))
    rod = 70                                    # rodapé "suporte@... · 4 lojas"
    cor = tuple(int(c) for c in lat[-rod - 30, X0 // 2])
    col = np.zeros((H16 - Y0, X0, 3), np.uint8)
    col[:] = cor
    col[:lat.shape[0] - rod] = lat[:-rod]
    col[-rod:] = lat[-rod:]
    # mantém a linha vertical que separa o menu do conteúdo
    col[lat.shape[0] - rod:-rod, -3:] = lat[-rod - 30, -3:]
    mold.paste(Image.fromarray(col), (0, Y0))
    mold.save(os.path.join(C, 'moldura16x9.png'))
    print('pagina', pagina.size, 'moldura', mold.size, 'cor menu', cor)


if __name__ == '__main__':
    main()
