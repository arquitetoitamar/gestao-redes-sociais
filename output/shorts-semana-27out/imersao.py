#!/usr/bin/env python3
"""Cortes verticais das gravações da Imersão de 24/10.

Reaproveita o motor do `monta.py` (fundo desfocado + gancho + legenda em
PNG), só trocando de onde vêm o vídeo e o SRT.

Cada janela fecha ANTES da parte em que o participante diz número de
faturamento, margem ou nicho que identifique a loja — os participantes
autorizaram aparecer, o que não é o mesmo que autorizar publicar o
próprio resultado. Ver a regra de publicação nas memórias.
"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import monta

DRIVE = os.path.expanduser(
    '~/Library/CloudStorage/GoogleDrive-isantos.ads@gmail.com/'
    'Meu Drive/Fotos e videos de imersao')
SCRATCH = ('/private/tmp/claude-501/-Users-itamar-git-gestao-redes-sociais/'
           'b2908fef-345f-4be4-96f1-b08c122b4fc8/scratchpad/shorts')

# chave, clipe, ini, fim, gancho, o que fica de fora
CORTES = [
    ('agente-plataforma', '9806', 82.0, 110.0,
     'NAO FOQUE NA\nPLATAFORMA\nDE AGENTE', None),
    ('ferramenta-nova', '9806', 18.0, 35.0,
     'TODO DIA SAI\nUMA FERRAMENTA\nNOVA', None),
    ('perdido-youtube', '9826', 33.0, 54.0,
     'EU SABIA QUE\nIA AJUDAVA\nMAS ME PERDIA',
     'corta antes do nicho e da cidade da loja (54 s)'),
    ('substituir', '9826', 74.0, 90.0,
     'ACHEI QUE IA\nDEMITIR TODO\nMUNDO', None),
    ('estampa', '9792', 17.0, 60.0,
     'FOTO DA RUA\nVIRA ESTAMPA\nEM 2 MINUTOS',
     'corta antes do "60% do desenvolvimento" (68 s)'),
    ('cerebro', '9703', 34.0, 49.0,
     'CONECTEI NA\nCONTA DELE\nE TRAVOU', None),
]


def main(pedidos):
    # o motor olha para estes dois caminhos; redireciona para a Imersão
    monta.NORM = DRIVE
    monta.SRT = SCRATCH
    for chave, num, ini, fim, gancho, _nota in CORTES:
        if pedidos and chave not in pedidos:
            continue
        # monta() deriva o nome do SRT de 'NN-XXXX.mp4' -> 'tr-XXXX.srt';
        # aqui os arquivos são 'IMG_9806.MOV' e 'srt-IMG_9806.srt'
        alvo, dur, n = monta.monta(chave, 'IMG_%s.MOV' % num, ini, fim, gancho)
        print('%-18s %4.0fs  %2d legendas' % (chave, dur, n))


if __name__ == '__main__':
    main(sys.argv[1:])
