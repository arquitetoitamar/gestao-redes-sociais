#!/usr/bin/env python3
"""Contact sheet determinístico com PIL. ffmpeg tile duplica quadro."""
import os, subprocess, sys
from PIL import Image

def amostra(src, dst, passo, cols, larg):
    tmp = dst + '_q'
    os.makedirs(tmp, exist_ok=True)
    for n in os.listdir(tmp):
        os.unlink(os.path.join(tmp, n))
    subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', 'fps=1/%g' % passo,
                    '-q:v', '4', os.path.join(tmp, 'q%04d.jpg')], check=True)
    nomes = sorted(os.listdir(tmp))
    ims = [Image.open(os.path.join(tmp, n)) for n in nomes]
    if not ims:
        print('sem quadro', src); return
    w0, h0 = ims[0].size
    alt = int(larg * h0 / w0)
    linhas = (len(ims) + cols - 1) // cols
    folha = Image.new('RGB', (cols * larg, linhas * alt), 'black')
    for i, im in enumerate(ims):
        folha.paste(im.resize((larg, alt)), ((i % cols) * larg, (i // cols) * alt))
    folha.save(dst, quality=88)
    print(dst, len(ims), 'quadros, passo', passo, 's')

if __name__ == '__main__':
    amostra(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
