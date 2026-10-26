#!/usr/bin/env python3
"""Monta os Shorts 1080x1920 a partir do material 16:9 do vlog.

Esta máquina não tem drawtext nem libass no ffmpeg, então todo texto sai
como PNG do PIL e entra por overlay (mesma receita do vlog).

Layout: fundo é o próprio quadro ampliado e desfocado; o quadro original
fica centrado (1080x608); o gancho ocupa a faixa de cima e a legenda
rolante a de baixo.
"""
import os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

NORM = os.path.expanduser(
    '/private/tmp/claude-501/-Users-itamar-git-gestao-redes-sociais/'
    'b2908fef-345f-4be4-96f1-b08c122b4fc8/scratchpad/offtopic/norm')
SRT = os.path.expanduser(
    '/Users/itamar/git/gestao-redes-sociais/output/offtopic-casa-nova')
SAIDA = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(SAIDA, 'trab')
PRETO = '/System/Library/Fonts/Supplemental/Arial Black.ttf'

L, A = 1080, 1920
FAIXA = (A - 608) // 2          # 656 px de folga em cima e embaixo


def quebra(texto, fonte, largura, desenho):
    """Quebra o texto em linhas que caibam em `largura`."""
    linhas, atual = [], ''
    for p in texto.split():
        teste = (atual + ' ' + p).strip()
        if desenho.textlength(teste, font=fonte) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def cartao(texto, tam, cor, largura=980, entrelinha=1.12):
    """PNG transparente com o texto centrado e contorno preto."""
    fonte = ImageFont.truetype(PRETO, tam)
    regua = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    linhas = [l for bruto in texto.split('\n')
              for l in quebra(bruto, fonte, largura, regua)]
    alt = int(tam * entrelinha)
    img = Image.new('RGBA', (L, alt * len(linhas) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, linha in enumerate(linhas):
        x = (L - d.textlength(linha, font=fonte)) / 2
        d.text((x, 20 + i * alt), linha, font=fonte, fill=cor,
               stroke_width=max(6, tam // 12), stroke_fill=(0, 0, 0, 235))
    return img


def le_srt(caminho):
    """Devolve [(ini, fim, fala)] em segundos."""
    def seg(s):
        h, m, resto = s.split(':')
        sg, ms = resto.split(',')
        return int(h) * 3600 + int(m) * 60 + int(sg) + int(ms) / 1000
    itens = []
    bloco = open(caminho, encoding='utf-8').read().strip().split('\n\n')
    for b in bloco:
        linhas = b.strip().split('\n')
        if len(linhas) < 3:
            continue
        m = re.match(r'(\S+) --> (\S+)', linhas[1])
        if m:
            itens.append((seg(m.group(1)), seg(m.group(2)),
                          ' '.join(linhas[2:]).strip()))
    return itens


def fatia(itens, ini, fim, limite=5.0):
    """Recorta a janela e reposiciona os tempos em zero.

    Falas longas (o whisper junta parágrafos inteiros em 3868) são
    picadas em pedaços de no máximo `limite` segundos para a legenda
    acompanhar a voz.
    """
    saida = []
    for a, b, txt in itens:
        if b <= ini or a >= fim:
            continue
        a, b = max(a, ini) - ini, min(b, fim) - ini
        dur = b - a
        if dur <= limite:
            saida.append((a, b, txt))
            continue
        n = int(dur // limite) + 1
        palavras, passo = txt.split(), dur / n
        tam = len(palavras) // n + 1
        for i in range(n):
            parte = ' '.join(palavras[i * tam:(i + 1) * tam])
            if parte:
                saida.append((a + i * passo, a + (i + 1) * passo, parte))
    return saida


def monta(chave, fonte_video, ini, fim, gancho):
    os.makedirs(TRAB, exist_ok=True)
    dur = fim - ini
    num = fonte_video.split('-')[1].split('.')[0]
    legendas = fatia(le_srt(os.path.join(SRT, 'tr-%s.srt' % num)), ini, fim)

    png_gancho = os.path.join(TRAB, '%s-gancho.png' % chave)
    cartao(gancho, 104, (255, 216, 0, 255)).save(png_gancho)

    entradas = ['-i', os.path.join(NORM, fonte_video), '-i', png_gancho]
    pngs = []
    for i, (a, b, txt) in enumerate(legendas):
        p = os.path.join(TRAB, '%s-%02d.png' % (chave, i))
        cartao(txt.upper(), 68, (255, 255, 255, 255)).save(p)
        pngs.append((p, a, b))
        entradas += ['-i', p]

    # fundo desfocado + quadro original centrado
    f = ['[0:v]split=2[bg][fg]',
         '[bg]scale=%d:%d:force_original_aspect_ratio=increase,'
         'crop=%d:%d,boxblur=28:2,eq=brightness=-0.12[bgb]' % (L, A, L, A),
         '[fg]scale=%d:-2[fgs]' % L,
         '[bgb][fgs]overlay=(W-w)/2:(H-h)/2[base]',
         # gancho fica fixo na faixa de cima
         '[base][1:v]overlay=0:%d[comg]' % int(FAIXA * 0.30)]
    marca = 'comg'
    for i, (_, a, b) in enumerate(pngs):
        prox = 'c%d' % i
        f.append("[%s][%d:v]overlay=0:%d:enable='between(t,%.3f,%.3f)'[%s]"
                 % (marca, i + 2, A - FAIXA + int(FAIXA * 0.18), a, b, prox))
        marca = prox

    alvo = os.path.join(SAIDA, '%s.mp4' % chave)
    cmd = (['ffmpeg', '-v', 'error', '-ss', '%.3f' % ini, '-t', '%.3f' % dur]
           + entradas
           + ['-filter_complex', ';'.join(f),
              '-map', '[%s]' % marca, '-map', '0:a',
              '-c:v', 'h264_videotoolbox', '-b:v', '9M',
              '-c:a', 'aac', '-b:a', '160k',
              '-r', '30', '-pix_fmt', 'yuv420p', alvo, '-y'])
    subprocess.run(cmd, check=True)
    return alvo, dur, len(pngs)


if __name__ == '__main__':
    sys.path.insert(0, SAIDA)
    from cortes import CORTES
    pedidos = sys.argv[1:] or [c[0] for c in CORTES]
    for chave, fonte, ini, fim, gancho, _tema in CORTES:
        if chave not in pedidos:
            continue
        alvo, dur, n = monta(chave, fonte, ini, fim, gancho)
        print('%-12s %4.0fs  %2d legendas  %s'
              % (chave, dur, n, os.path.basename(alvo)))
