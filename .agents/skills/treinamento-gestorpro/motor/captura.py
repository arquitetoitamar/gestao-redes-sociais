#!/usr/bin/env python3
"""Captura em retina a janela do Chrome com o GestorPro, guiada pelo título da aba.

O JavaScript na página põe document.title = 'CAP-<nome>' quando a tela está pronta;
este laço vê o título pela lista de janelas do macOS e grava capturas/<nome>.png
(só a área da página, sem abas e barra do navegador).

  python3 captura.py <pasta-da-aula> <segundos>

Título com altura: 'CAP-<nome>-h<innerHeight>' (a barra "o Claude está depurando" muda a altura da página).
"""
import os, sys, time
import Quartz
from Quartz import CGWindowListCreateImage, CGRectNull, kCGWindowListOptionIncludingWindow, \
    kCGWindowImageBoundsIgnoreFraming, kCGWindowImageBestResolution
from PIL import Image

AQUI = os.path.abspath(sys.argv[1])
OUT = os.path.join(AQUI, 'capturas')
os.makedirs(OUT, exist_ok=True)
VIEW_H = int(os.environ.get('VIEW_H', '698'))     # altura da página em pontos (innerHeight)


def janela():
    for w in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll, Quartz.kCGNullWindowID):
        if w.get('kCGWindowOwnerName') == 'Google Chrome' and w.get('kCGWindowLayer') == 0:
            nome = w.get('kCGWindowName') or ''
            if nome.startswith('CAP-') or 'GestorPro' in nome:
                return w.get('kCGWindowNumber'), nome, w.get('kCGWindowBounds')
    return None, '', None


def grava(wid, nome, bounds, view_h=None):
    img = CGWindowListCreateImage(CGRectNull, kCGWindowListOptionIncludingWindow, wid,
                                  kCGWindowImageBoundsIgnoreFraming | kCGWindowImageBestResolution)
    w, h = Quartz.CGImageGetWidth(img), Quartz.CGImageGetHeight(img)
    bpr = Quartz.CGImageGetBytesPerRow(img)
    dados = Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(img))
    im = Image.frombuffer('RGBA', (w, h), bytes(dados), 'raw', 'BGRA', bpr, 1).convert('RGB')
    esc = w / bounds['Width']
    top = int(round((bounds['Height'] - (view_h or VIEW_H)) * esc))
    im = im.crop((0, top, w, h))
    im.save(os.path.join(OUT, nome[4:] + '.png'))
    return im.size


if __name__ == '__main__':
    fim = time.time() + float(sys.argv[2])
    feitos = set()
    while time.time() < fim:
        wid, nome, b = janela()
        if wid and nome.startswith('CAP-') and nome not in feitos:
            feitos.add(nome)
            time.sleep(0.15)
            vh = None
            if '-h' in nome:                       # CAP-<nome>-h<innerHeight>
                nome, vh = nome.rsplit('-h', 1)
                vh = float(vh)
            print(nome, vh, grava(wid, nome, b, vh), flush=True)
            feitos.add(nome)
        time.sleep(0.1)
