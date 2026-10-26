#!/usr/bin/env python3
"""Define os cortes verticais do vlog da casa nova.

Os tempos são do material normalizado em
scratchpad/offtopic/norm/ (1920x1080, 30 fps), conferidos contra os SRT
tr-4293.srt e tr-3868.srt. Nenhum corte usa 01-3866.mp4: é o clipe da
entrada, onde o número da casa fica legível.
"""

# chave, fonte, ini, fim, gancho (vai no topo, estático), tema
CORTES = [
    ('condominio', '04-4293.mp4', 122.0, 143.0,
     'EU PERGUNTAVA\nCOMO ELES\nCONSEGUEM',
     'pessoal'),
    ('solucao', '04-4293.mp4', 206.0, 236.0,
     'PARE DE OLHAR\nO PROBLEMA',
     'negocio'),
    ('ostentar', '04-4293.mp4', 79.0, 94.0,
     'NAO E\nOSTENTACAO',
     'pessoal'),
    ('moveis-ia', '04-4293.mp4', 250.0, 270.0,
     'USEI IA PRA\nPROJETAR\nOS MOVEIS',
     'negocio'),
    ('empresarios', '04-4293.mp4', 274.0, 310.0,
     'O QUE OS DONOS\nDE EMPRESA\nQUEREM',
     'negocio'),
    ('parcelas', '04-4293.mp4', 26.0, 79.0,
     'COMPREI E\nAINDA NAO\nMOREI',
     'pessoal'),
    ('canal', '04-4293.mp4', 167.0, 190.0,
     'NAO SOU DO\nMARKETING\nDIGITAL',
     'pessoal'),
    ('remoto', '03-3868.mp4', 28.0, 50.0,
     'O DIGITAL ME\nDEIXOU ESCOLHER\nONDE MORAR',
     'pessoal'),
]
