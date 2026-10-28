#!/usr/bin/env python3
"""Corte do depoimento do Phellipe na Imersão (24/10): como ele conheceu o Itamar.

Etapa 1 (`base`): junta os trechos escolhidos do IMG_9717.MOV, aproxima 1,6x
os planos abertos (ele e o Itamar ficam no quadro) e mantém o áudio original,
só com fade de 30-40 ms nas emendas.
Etapa 2 (`final`): queima a legenda animada gerada por `legenda.py`.
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.expanduser('~/Downloads/IMG_9717.MOV')
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
TRAB = os.path.join(AQUI, 'trab')

# (início, fim) em segundos do original. Cortes em pausa, conferidos por energia.
TRECHOS = [
    (20.08, 41.32),   # acha que a IA vai dominar a gente -> 24 visualizações -> liguei
    (51.11, 61.09),   # não tinha visualização mas já explicava; sou fabricante
    (66.05, 82.18),   # dificuldade com gente -> consultoria -> conectou as contas
    (94.35, 104.90),  # você criou um ecossistema... aí está o ouro
    (145.36, 152.90), # mega cérebro sobre marketplace
    (153.72, 162.86), # posso bater palmas? é nosso ouro
]
# Planos abertos (câmera longe): ganham zoom.
ABERTOS = [(20.08, 28.5), (30.4, 41.32), (51.11, 61.09), (66.05, 67.6)]
ZOOM, CX, CY = 1.6, 0.52, 0.50


def pedacos_video():
    """Divide os trechos onde muda o plano, marcando quais levam zoom."""
    cortes = sorted({t for a, b in ABERTOS for t in (a, b)})
    out = []
    for a, b in TRECHOS:
        pts = [a] + [t for t in cortes if a < t < b] + [b]
        for x, y in zip(pts, pts[1:]):
            aberto = any(p <= x and y <= q for p, q in ABERTOS)
            out.append((x, y, aberto))
    return out


def base():
    w, h = round(1080 / ZOOM / 2) * 2, round(1920 / ZOOM / 2) * 2
    x, y = round(1080 * CX - w / 2), round(1920 * CY - h / 2)
    f, vs, as_ = [], [], []
    for i, (a, b, aberto) in enumerate(pedacos_video()):
        z = f',crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos' if aberto else ''
        f.append(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30{z},setsar=1[v{i}]')
        vs.append(f'[v{i}]')
    for i, (a, b) in enumerate(TRECHOS):
        d = b - a
        f.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,'
                 f'afade=t=in:d=0.03,afade=t=out:st={d - 0.04:.3f}:d=0.04[a{i}]')
        as_.append(f'[a{i}]')
    f.append(''.join(vs) + f'concat=n={len(vs)}:v=1:a=0[v]')
    f.append(''.join(as_) + f'concat=n={len(as_)}:v=0:a=1[a]')
    subprocess.run([FF, '-v', 'error', '-y', '-i', FONTE, '-filter_complex', ';'.join(f),
                    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                    os.path.join(TRAB, 'base.mp4')], check=True)


def final():
    subprocess.run([FF, '-v', 'error', '-y', '-i', os.path.join(TRAB, 'base.mp4'),
                    '-vf', 'ass=' + os.path.join(TRAB, 'legenda.ass'),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
                    '-c:a', 'copy', '-movflags', '+faststart',
                    os.path.join(AQUI, 'depoimento-phellipe.mp4')], check=True)


if __name__ == '__main__':
    {'base': base, 'final': final}[sys.argv[1]]()
