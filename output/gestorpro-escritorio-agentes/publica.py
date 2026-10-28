#!/usr/bin/env python3
"""Publica videos/final.mp4 no canal Itamar Rocha como PÚBLICO (pedido do Itamar),
com thumb, descrição com capítulos, tags, idioma, categoria e local.

  python3 publica.py texto    só mostra título, descrição e tags
  python3 publica.py sobe     publica (grava publicado.json)
"""
import json, os, sys, urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/git/gestao-redes-sociais/scripts/trilha'))

TITULO = 'Escritório de Agentes no Mercado Livre | Agente de IA no Mercado Livre'
LINK = 'https://gestorpro.tiops.com.br/'

TAGS = ['agente de ia no mercado livre', 'escritório de agentes', 'agentes de ia', 'gestorpro', 'mercado livre',
        'mercadolivre', 'inteligência artificial', 'ia no mercado livre', 'claude', 'ecommerce', 'shopee',
        'ia nos marketplaces', 'automação mercado livre', 'crm mercado livre', 'recomendação de produtos',
        'whatsapp', 'pós-venda mercado livre', 'margem de lucro mercado livre', 'ia para vendedores',
        'automação com ia', 'ia para empresas', 'marketplace connect', 'tiops', 'itamar rocha']


def capitulos():
    import render
    ab = json.load(open(os.path.join(AQUI, 'trab', 'tempos.json')))['abertura_s']
    linhas = ['0:00 Abertura']
    for s, t in render.CAPITULOS:
        x = ab + (render.final_t(s) if s > 0 else 0.0)
        linhas.append('%d:%02d %s' % (x // 60, x % 60, t))
    return '\n'.join(linhas)


def descricao():
    return """O GestorPro é um escritório de agentes de IA que trabalha na sua loja do Mercado Livre o dia inteiro: recomenda produtos para quem já comprou, manda a recomendação pelo WhatsApp com o Claude, cuida do pós-venda, abre contestação de devolução com a IA do Mercado Livre, sugere o ajuste de preço para entrar na banda de margem e coloca e tira anúncios de promoção no automático.

Neste vídeo eu mostro, na tela, o CRM novo, a recomendação de produtos com IA e uma navegada geral pela operação.

👉 Conheça o GestorPro: %s
🔗 Conecte suas lojas pelo Marketplace Connect: https://l.tiops.com.br/automatizar-loja?o=youtube
🎥 Imersão IA para Marketplaces completa (3 horas, de graça): https://youtu.be/7VVhSzlHfdI

Capítulos:
%s

O que você vai ver:
• CRM de clientes do Mercado Livre, com histórico de compras e anotações
• Recomendação de produtos feita pela IA a partir do que o cliente comprou
• O agente mandando a recomendação pelo WhatsApp, com o Claude conectado
• Link pelo chat do pedido, com a sua aprovação antes de enviar
• Pós-venda, devoluções e contestação com a IA do Mercado Livre
• Decisões para aprovar: ajuste de preço na banda de margem, título e descrição
• Margem por canal, ads e promoções que entram e saem no automático
• Como os agentes enxergam a sua operação, em tempo real

Os dados de clientes foram ocultados no vídeo.

#AgentesDeIA #MercadoLivre #GestorPro #InteligenciaArtificial #Ecommerce""" % (LINK, capitulos())


def confere(desc):
    n = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1
    assert n <= 500, 'tags com %d caracteres' % n
    assert len(TITULO) <= 100 and '<' not in desc and '>' not in desc and len(desc) <= 5000
    return n


def sobe():
    import yt
    yt.refresh()
    tok = yt._tok()['access_token']
    video = os.path.join(AQUI, 'videos', 'final.mp4')
    desc = descricao()
    confere(desc)
    corpo = {
        'snippet': {'title': TITULO, 'description': desc, 'tags': TAGS, 'categoryId': '28',
                    'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'license': 'youtube',
                   'embeddable': True, 'publicStatsViewable': True, 'containsSyntheticMedia': False},
        'recordingDetails': {'locationDescription': 'São Paulo, SP, Brasil',
                             'location': {'latitude': -23.5505, 'longitude': -46.6333, 'altitude': 0},
                             'recordingDate': '2026-10-28T00:00:00Z'},
    }
    tam = os.path.getsize(video)
    req = urllib.request.Request(
        'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status,recordingDetails&notifySubscribers=true',
        data=json.dumps(corpo).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                 'X-Upload-Content-Length': str(tam), 'X-Upload-Content-Type': 'video/mp4'})
    sessao = urllib.request.urlopen(req).headers['Location']
    with open(video, 'rb') as f:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(
            sessao, data=f, method='PUT', headers={'Content-Length': str(tam)}), timeout=3600).read())
    vid = d['id']
    print('vídeo', vid)
    res = {'id': vid, 'url': 'https://youtu.be/' + vid}
    thumb = os.path.join(AQUI, 'thumb.jpg')
    with open(thumb, 'rb') as f:
        r = urllib.request.urlopen(urllib.request.Request(
            'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + vid, data=f.read(), method='POST',
            headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'}))
        res['thumb'] = r.status
    json.dump(res, open(os.path.join(AQUI, 'publicado.json'), 'w'), indent=1)
    print(res)


if __name__ == '__main__':
    if sys.argv[1] == 'texto':
        d = descricao()
        print(TITULO, '\n\n' + d, '\n\nTAGS (%d car.):' % confere(d), ', '.join(TAGS))
    elif sys.argv[1] == 'sobe':
        sobe()
