#!/usr/bin/env python3
"""Cartela de título em PNG. ffmpeg desta máquina não tem drawtext nem libass."""
from PIL import Image, ImageDraw, ImageFont

L, A = 1920, 1080
PRETO = '/System/Library/Fonts/Supplemental/Arial Black.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
AMBAR = (255, 193, 7, 255)

def fonte(p, t):
    return ImageFont.truetype(p, t)

im = Image.new('RGBA', (L, A), (0, 0, 0, 0))
d = ImageDraw.Draw(im)

# Escurece só a faixa de baixo, pra legibilidade sem tapar a animação.
scrim = Image.new('RGBA', (L, A), (0, 0, 0, 0))
sd = ImageDraw.Draw(scrim)
topo = 560
for y in range(topo, A):
    a = int(200 * ((y - topo) / (A - topo)) ** 1.3)
    sd.line([(0, y), (L, y)], fill=(0, 0, 0, a))
im = Image.alpha_composite(im, scrim)
d = ImageDraw.Draw(im)

x = 110
f1 = fonte(PRETO, 104)
f2 = fonte(BOLD, 46)
linhas = [('COMPREI UMA', (255, 255, 255, 255), f1),
          ('CASA NOVA', (255, 255, 255, 255), f1)]
y = 690
for txt, cor, f in linhas:
    d.text((x + 4, y + 4), txt, font=f, fill=(0, 0, 0, 170))
    d.text((x, y), txt, font=f, fill=cor)
    y += 112

# Faixa âmbar com a segunda metade do título.
sub = 'A IA GERA RESULTADOS'
cx0, cy0, cx1, cy1 = d.textbbox((0, 0), sub, font=f2)
pw, ph = 26, 18
d.rectangle([x, y + 16, x + (cx1 - cx0) + pw * 2, y + 16 + (cy1 - cy0) + ph * 2], fill=AMBAR)
d.text((x + pw - cx0, y + 16 + ph - cy0), sub, font=f2, fill=(10, 10, 10, 255))

im.save('titulo.png')
print('titulo.png', im.size)
