#!/usr/bin/env python3
"""Reel 9:16 do trecho da Gerência Pedidos na reportagem da Band Cidade (BandVale TV), sobre empresas do
PqTec durante a pandemia. Fonte: youtube.com/watch?v=K3MZxI--Dtk (canal Dev Cloud Native).

Pedido do Itamar (04/11/2026): "faça um reel com este vídeo, principalmente a parte em que eu fui
entrevistado, o que eu estava fazendo na pandemia".

- Trecho 0:00–0:52 (narração + entrevista de 0:24 a 0:52), enquadrado cena a cena, sem a tarja da TV.
- Cena 19–24 s (gráficos de faturamento da plataforma) desfocada: print de painel não vai a público.
- Áudio original, sem tratamento (feedback do Itamar: nada de denoise/EQ/música sem pedir).
- Fecho de 3 s ligando a história ao Marketplace Connect, CTA "Comenta CONNECT".

  python3 monta.py     (precisa de trab/original.mp4; gera reel_startup_pandemia.mp4)
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(AQUI, 'trab')
SRC = os.path.join(T, 'original.mp4')
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'   # tem libass (o ffmpeg do PATH não tem)
FIM = 52.0

# cenas (início, fim, centro horizontal do recorte em fração da largura, desfocar?)
CENAS = [(0, 3.7667, .50, False), (3.7667, 5.0333, .45, False), (5.0333, 6.8333, .50, False),
         (6.8333, 9.2, .42, False), (9.2, 14.4333, .58, False), (14.4333, 19.0667, .64, False),
         (19.0667, 24.3333, .50, True), (24.3333, FIM, .45, False)]
# recorte vertical: tira o relógio da TV no topo e a tarja/logo na base
Y0, Y1 = 86, 864
CH = Y1 - Y0
CW = round(CH * 1080 / 1216 / 2) * 2          # proporção da área de vídeo 1080x1216
VY = 360                                       # topo da área de vídeo no quadro 1080x1920

LEG = [  # (início, fim, texto) — da transcrição em trab/transcricao.srt, revisada
    (0.0, 4.24, 'A crise da pandemia fechou mais de 75 mil lojas físicas no Brasil.'),
    (4.70, 8.66, 'E quem trabalha com varejo precisou se reinventar com a ajuda da tecnologia.'),
    (9.34, 14.18, 'Esse é o trabalho da Gerência Pedidos, que integra as contas em comércio eletrônico.'),
    (14.72, 18.92, 'A solução deles já movimentou mais de 81 milhões de reais,'),
    (19.36, 24.06, 'com facilidade e aceleração de processos para compra e entrega de mercadorias.'),
    (24.06, 28.70, 'Dentro da plataforma, desde que nós fundamos ela em julho de 2019,'),
    (29.04, 33.90, 'na sua versão inicial, passaram dentro da ferramenta mais ou menos 800 vendedores.'),
    (34.10, 40.64, 'Dentro desses vendedores, tivemos mais de 2 mil contas de marketplace cadastradas.'),
    (41.38, 44.38, 'No GMV total, o cálculo total bruto de vendas,'),
    (44.84, 49.48, 'nós tivemos aí um faturamento de 81 milhões, aproximadamente,'),
    (49.48, 51.90, 'e 4 milhões de produtos cadastrados.'),
]


def ts(s):
    h, r = divmod(s, 3600); m, r = divmod(r, 60)
    return f'{int(h)}:{int(m):02d}:{r:05.2f}'


def ass():
    cab = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Titulo,Arial Black,92,&H00FFFFFF,&H00FFFFFF,&H00331D0B,&H00331D0B,0,0,0,0,100,100,0,0,1,0,0,8,60,60,120,1
Style: Nome,Arial,46,&H0000E6FF,&H0000E6FF,&H00000000,&HC8331D0B,1,0,0,0,100,100,0,0,3,16,0,1,60,60,640,1
Style: Leg,Arial,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB4000000,1,0,0,0,100,100,0,0,3,14,0,2,70,70,390,1
Style: Credito,Arial,36,&H00C6B09F,&H00C6B09F,&H00331D0B,&H00331D0B,0,0,0,0,100,100,0,0,1,0,0,8,70,70,1600,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f'Dialogue: 0,{ts(0)},{ts(FIM)},Titulo,,0,0,0,,O que eu fazia\\Nna pandemia',
          f'Dialogue: 2,{ts(24.4)},{ts(30.5)},Nome,,0,0,0,,{{\\fad(200,200)}}Itamar Rocha\\N{{\\c&HFFFFFF&\\b0\\fs36}}fundador da Gerência Pedidos',
          f'Dialogue: 0,{ts(0)},{ts(FIM)},Credito,,0,0,0,,Reportagem: Band Cidade · BandVale TV']
    for a, b, t in LEG:
        ev.append(f'Dialogue: 1,{ts(a)},{ts(b)},Leg,,0,0,0,,{{\\fad(80,80)}}{t}')
    p = os.path.join(T, 'legendas.ass')
    open(p, 'w').write(cab + '\n'.join(ev) + '\n')
    return p


def principal():
    partes, rot = [], []
    for k, (a, b, c, blur) in enumerate(CENAS):
        x = int(min(max(c * 1920 - CW / 2, 0), 1920 - CW))
        f = f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,crop={CW}:{CH}:{x}:{Y0},scale=1080:1216'
        if blur:
            f += ',boxblur=18:2'
        partes.append(f + f'[v{k}]'); rot.append(f'[v{k}]')
    fc = ';'.join(partes)
    fc += f';{"".join(rot)}concat=n={len(CENAS)}:v=1:a=0[vid]'
    fc += ';color=c=0x0B1D33:s=1080x1920:r=30[bg]'
    fc += f';[bg][vid]overlay=0:{VY}:shortest=1,subtitles={ass()}[out]'
    fc += f';[0:a]atrim=0:{FIM},asetpts=PTS-STARTPTS,afade=t=out:st={FIM - 0.4}:d=0.4[aud]'
    saida = os.path.join(T, 'parte1.mp4')
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', SRC, '-filter_complex', fc, '-map', '[out]', '-map', '[aud]',
                    '-t', str(FIM), '-r', '30', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', saida], check=True)
    return saida


def fonte(n, tam):
    for f in (f'/System/Library/Fonts/Supplemental/{n}.ttf', f'/Library/Fonts/{n}.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def fecho():
    # último quadro da entrevista, desfocado, com o texto de ligação para hoje
    q = os.path.join(T, 'ultimo.png')
    subprocess.run([FF, '-y', '-loglevel', 'error', '-ss', str(FIM - .2), '-i', os.path.join(T, 'parte1.mp4'),
                    '-frames:v', '1', q], check=True)
    im = Image.open(q).convert('RGB').filter(ImageFilter.GaussianBlur(22))
    ov = Image.new('RGBA', im.size, (11, 29, 51, 200)); im = Image.alpha_composite(im.convert('RGBA'), ov)
    d = ImageDraw.Draw(im)
    W = 1080
    def centro(y, txt, f, cor):
        w = d.textlength(txt, font=f); d.text(((W - w) / 2, y), txt, font=f, fill=cor)
    centro(560, 'Em 2019: integrar as', fonte('Arial Bold', 60), (199, 210, 224))
    centro(640, 'contas de marketplace.', fonte('Arial Bold', 60), (199, 210, 224))
    centro(800, 'Hoje: colocar a IA', fonte('Arial Black', 80), (244, 247, 251))
    centro(900, 'dentro delas.', fonte('Arial Black', 80), (255, 230, 0))
    d.rounded_rectangle((140, 1080, 940, 1300), radius=30, outline=(255, 230, 0), width=5, fill=(20, 42, 70, 255))
    centro(1110, 'Comenta', fonte('Arial Bold', 48), (244, 247, 251))
    centro(1170, 'CONNECT', fonte('Arial Black', 96), (255, 230, 0))
    centro(1360, 'Marketplace Connect · @tiopstecnologia', fonte('Arial Bold', 36), (108, 198, 255))
    p = os.path.join(T, 'fecho.png'); im.convert('RGB').save(p)
    saida = os.path.join(T, 'parte2.mp4')
    subprocess.run([FF, '-y', '-loglevel', 'error', '-loop', '1', '-i', p, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                    '-t', '3', '-r', '30', '-vf', 'fade=t=in:st=0:d=0.35', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', saida], check=True)
    return saida


if __name__ == '__main__':
    p1 = principal()
    p2 = fecho()
    final = os.path.join(AQUI, 'reel_startup_pandemia.mp4')
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', p1, '-i', p2, '-filter_complex',
                    '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]', '-map', '[v]', '-map', '[a]', '-c:v', 'libx264',
                    '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', final], check=True)
    print('ok', final)
