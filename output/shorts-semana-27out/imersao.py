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

# --- segunda leva, cortada em 27/10 do material que sobrou ---
CORTES += [
    ('tralha', '9719', 3.0, 31.0,
     'VENDO TRALHA\nDESDE OS\n10 ANOS',
     'fecha antes do nome da empresa e do percentual de faturamento (47 s)'),
    ('executor', '9779', 4.0, 33.0,
     'SEM EXECUTOR\nO NEGOCIO\nNAO ANDA',
     'fecha antes das linhas de negocio e dos clientes citados (39 s)'),
    ('print-do-zap', '9715', 39.0, 59.0,
     'PRINT DO ZAP\nCONSERTA O\nSISTEMA', None),
    ('portfolio', '9788', 15.0, 40.0,
     'MEU LIMITE NAO\nE PRODUZIR\nE ANUNCIAR',
     'comeca depois da conversa sobre venda que caiu e subiu (0-11 s)'),
    ('respondeu-1h15', '9826', 8.0, 26.0,
     'ESPEREI 30 DIAS\nELE RESPONDEU\n1H15 DA MANHA', None),
    ('hype', '9806', 45.0, 80.0,
     'ESSES AGENTES\nDE ALTO NIVEL\nSAO O QUE?', None),
]


# Regiões a borrar depois de renderizar: (x, y, larg, alt, de, ate) no quadro
# final 1080x1920. O quadro 16:9 fica em y 656..1264.
TAPAS = {
    # slide do participante com "2000 · 600 mil" na TV ao fundo, plano aberto
    'executor': [(680, 666, 400, 390, 20.4, 99.0)],
}


def tapa(chave):
    """Borra as regiões de TAPAS por cima do Short já renderizado."""
    import subprocess
    regioes = TAPAS.get(chave)
    if not regioes:
        return
    alvo = os.path.join(AQUI, chave + '.mp4')
    tmp = os.path.join(AQUI, 'trab', chave + '-sem-tapa.mp4')
    os.replace(alvo, tmp)
    f, marca = ['[0:v]split=%d[base]%s' % (len(regioes) + 1,
                ''.join('[r%d]' % i for i in range(len(regioes))))], 'base'
    for i, (x, y, w, h, de, ate) in enumerate(regioes):
        f.append('[r%d]crop=%d:%d:%d:%d,boxblur=30:4[b%d]' % (i, w, h, x, y, i))
        f.append("[%s][b%d]overlay=%d:%d:enable='between(t,%.2f,%.2f)'[o%d]"
                 % (marca, i, x, y, de, ate, i))
        marca = 'o%d' % i
    subprocess.run(['ffmpeg', '-v', 'error', '-i', tmp,
                    '-filter_complex', ';'.join(f), '-map', '[%s]' % marca,
                    '-map', '0:a', '-c:v', 'h264_videotoolbox', '-b:v', '9M',
                    '-c:a', 'copy', alvo, '-y'], check=True)


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
        tapa(chave)
        print('%-18s %4.0fs  %2d legendas' % (chave, dur, n))


if __name__ == '__main__':
    main(sys.argv[1:])
