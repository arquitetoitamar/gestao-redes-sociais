#!/usr/bin/env python3
"""Título, descrição e tags. Os capítulos saem dos tempos reais do corte."""
import re, subprocess

def dur(p):
    return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                                 '-of','csv=p=0',p], capture_output=True, text=True).stdout)

PARTES = ['abertura.mp4','norm/01-3866.mp4','norm/02-3867.mp4','norm/03-3868.mp4','norm/04-4293.mp4']
ini, acc = [], 0.0
for p in PARTES:
    ini.append(acc); acc += dur(p)
TOTAL = acc
A, B, C, D, E = ini          # E = início do vídeo longo

def mm(s):
    return '%d:%02d' % (int(s)//60, int(s) % 60)

CAPS = [
 (A + 0,    'Abertura'),
 (B + 1,    'A casa nova por dentro'),
 (C + 0,    'Quintal, área gourmet e a piscina'),
 (D + 0,    'Samuel, Sofia e a mudança pro interior'),
 (E + 0,    'Por que eu gravei esse vídeo'),
 (E + 41,   'Até onde a inteligência artificial leva a gente'),
 (E + 80,   'Por que um condomínio: as crianças na rua de novo'),
 (E + 145,  'Como eu ganho dinheiro com isso'),
 (E + 208,  'Pare de olhar o problema, entregue solução'),
 (E + 251,  'IA até no projeto dos móveis'),
 (E + 278,  'O que os empresários estão querendo agora'),
 (E + 337,  'Tudo tem um preço: a saúde que eu gastei'),
 (E + 372,  'Isso aqui não é prova social'),
 (E + 400,  'O fim da escala 6x1 e os funcionários digitais'),
 (E + 444,  'Recado final'),
]

cap = '\n'.join('%s - %s' % (mm(t), n) for t, n in CAPS)

TITULO = 'Comprei uma casa nova 🏡 A IA gera resultados | Saí de São Paulo pro interior'

DESC = """🏡 Comprei uma casa nova. Esse vídeo não é para ostentar — é agradecimento,
e é para mostrar onde o trabalho com inteligência artificial pode levar quem
resolve estudar e entregar solução de verdade.

Eu saí de São Paulo e estou de mudança para o interior, São José dos Campos.
Mostro a casa ainda vazia, o quintal, a área que vai virar gourmet, e depois
dou uma volta a pé pelo condomínio falando sem roteiro sobre o que mudou:
o trabalho remoto, os contratos, o canal que começou a andar agora, e o que
vem com o fim da escala 6x1 — mais automação, mais agente de IA, mais
funcionário digital.

Um recado que eu repito no meio do caminho: pare de se preocupar tanto com o
problema e comece a trabalhar na solução. Quando você entrega solução para as
pessoas, o resultado concreto aparece.

E tem o outro lado, que eu também falo: tudo tem um preço. Nesses últimos
meses eu troquei rotina de exercício por demanda. Morar aqui é parte de
arrumar isso.

%s

👨‍👩‍👧‍👦 Com o Samuel e a Sofia, que são o motivo de quase tudo isso.

🔗 Marketplace Connect — a ferramenta que eu uso e ensino:
https://l.tiops.com.br/comece

#InteligenciaArtificial #AgentesDeIA #CasaNova #Empreendedorismo #Automacao""" % cap

TAGS = ['casa nova','comprei uma casa','mudanca para o interior','sao jose dos campos',
        'morar no interior','sair de sao paulo','condominio fechado','inteligencia artificial',
        'agentes de ia','automacao','trabalho remoto','ganhar dinheiro com ia',
        'resultado com ia','empreendedorismo','fim da escala 6x1','funcionario digital',
        'automacao de processos','ia para empresas','itamar rocha','tiops',
        'marketplace connect','tour pela casa nova','qualidade de vida','vlog','ia']

# Guardas: o YouTube esconde TODOS os capítulos se um deles tiver menos de 10 s,
# e recusa < e > na descrição.
marcas = [int(m[0]) * 60 + int(m[1]) for m in re.findall(r'^(\d+):(\d\d) - ', DESC, re.M)]
assert marcas and marcas[0] == 0, 'capítulo tem de começar em 0:00'
assert len(marcas) >= 3, 'mínimo de 3 capítulos'
curtos = [(a, b) for a, b in zip(marcas, marcas[1:] + [int(TOTAL)]) if b - a < 10]
assert not curtos, 'capítulos curtos demais: %s' % curtos
assert '<' not in DESC and '>' not in DESC, 'YouTube recusa < e > (invalidDescription)'
assert len(TITULO) <= 100, 'título > 100'
assert len(DESC) <= 5000, 'descrição > 5000'
_custo = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1
assert _custo <= 500, 'tags > 500 como o YouTube conta: %d' % _custo

if __name__ == '__main__':
    print('total %s | %d capitulos | menor intervalo %ds | tags %d chars'
          % (mm(TOTAL), len(marcas), min(b - a for a, b in zip(marcas, marcas[1:] + [int(TOTAL)])),
             _custo))
    print('\nTITULO (%d):\n%s' % (len(TITULO), TITULO))
    print('\nDESC (%d):\n%s' % (len(DESC), DESC))
