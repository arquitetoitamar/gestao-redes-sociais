#!/usr/bin/env python3
"""Monta o .md das trilhas para o disparo de e-mail, lendo o estado real."""
import json, os, re

import yt

SAIDA = '../../output/trilha-basica/NOVIDADES-PARA-EMAIL.md'
PL_MC, PL_INICIO, PL_CLAUDE = 'PLW3upCIZHed4', 'PLGhRDamQTH7o', 'PLRRzEvlO7GjU'
KIT = 'https://drive.google.com/drive/folders/1mRnzxFIWPibvLqTBCO6xiZIG6J5cxGac'
GUIA = 'https://claude.ai/code/artifact/53bebbdf-0a74-4309-9c3c-ea591be370f9'


def itens(pl):
    d = yt.call('GET', 'playlistItems', {'part': 'snippet', 'playlistId': pl, 'maxResults': 50})
    ids = [i['snippet']['resourceId']['videoId'] for i in d['items']]
    det = {v['id']: v for v in yt.call('GET', 'videos',
           {'part': 'contentDetails,snippet', 'id': ','.join(ids)})['items']} if ids else {}
    saida = []
    for i in d['items']:
        s = i['snippet']
        v = det.get(s['resourceId']['videoId'], {})
        dur = v.get('contentDetails', {}).get('duration', '')
        m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', dur or '')
        h, mi, se = [int(x or 0) for x in (m.groups() if m else (0, 0, 0))]
        mins = h * 60 + mi + (1 if se >= 30 else 0)
        saida.append((s['title'], s['resourceId']['videoId'], mins))
    return saida


def bloco(titulo, pl, itens_):
    tot = sum(x[2] for x in itens_)
    L = ['### %s' % titulo, '',
         'https://www.youtube.com/playlist?list=' + pl, '',
         '| Aula | Dura |', '|---|---:|']
    for t, _, m in itens_:
        L.append('| %s | %d min |' % (t.replace('|', '—'), m))
    L.append('')
    L.append('_%d vídeos · cerca de %d minutos no total._' % (len(itens_), tot))
    L.append('')
    return '\n'.join(L)


mc, inicio, claude = itens(PL_MC), itens(PL_INICIO), itens(PL_CLAUDE)

texto = """# Novidades para a base — trilhas de treinamento

Material pronto para você montar o e-mail. Os links são **não listados**: abrem
para quem tem o endereço e não aparecem em busca nem no seu canal.

---

## Assunto (escolha um)

- Seu acesso ao treinamento do Marketplace Connect está liberado
- Duas trilhas novas: Marketplace Connect e Claude, do zero
- Arrumamos o treinamento — e separamos em duas trilhas

---

## Corpo do e-mail

Oi,

Reorganizei o material de treinamento e agora são duas trilhas separadas, cada
uma com o seu propósito.

**Trilha do Marketplace Connect** — como ligar a sua IA nas suas contas de
marketplace e começar a operar por conversa. Aulas curtas, na ordem de quem
acabou de contratar.

**Trilha de Claude** — formação geral na ferramenta: conversa, trabalho em
conjunto, skills e conectores. Serve mesmo para quem ainda não usa o
Marketplace Connect.

As duas vêm com material de apoio: um kit de skills com template comentado e
exemplos prontos para instalar.

%s
%s
%s
### Material de apoio

Kit de skills — template comentado e três exemplos que funcionam:
%s

Guia de integração (REST + MCP) — para quem vai ligar o próprio sistema no
Connect: endpoint, chave, as duas formas de chamar e os erros que mais custam
caro. Faz par com o vídeo "Como integrar sistema com Marketplace Connect".
%s

---

## Observações para você antes de disparar

- Os vídeos são **não listados**. Quem receber o link assiste; quem não
  receber, não encontra. Se encaminharem, o link funciona — é a natureza do
  não listado.
- A trilha do Marketplace Connect ainda está incompleta: faltam as aulas que
  você vai gravar. Vale dizer no e-mail que ela cresce toda semana, para a
  pessoa voltar.
- A playlist "Comece por aqui" é a mesma trilha com a demonstração de 22
  minutos na frente. Para cliente novo, mande essa. Para quem já usa, a trilha
  direto.
""" % (bloco('Trilha do Marketplace Connect', PL_MC, mc),
       bloco('Comece por aqui (demonstração + trilha)', PL_INICIO, inicio),
       bloco('Trilha de Claude', PL_CLAUDE, claude),
       KIT,
       GUIA)

os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
open(SAIDA, 'w', encoding='utf-8').write(texto)
print('escrito:', os.path.abspath(SAIDA))
print('MC %d · Comece %d · Claude %d' % (len(mc), len(inicio), len(claude)))
