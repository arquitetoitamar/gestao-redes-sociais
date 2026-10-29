#!/usr/bin/env python3
"""Publica videos/final.mp4 no canal Itamar Rocha como PÚBLICO (pedido do Itamar),
com thumb, descrição com capítulos, tags, idioma e categoria.

  python3 publica.py texto    só mostra título, descrição e tags
  python3 publica.py sobe     publica (grava publicado.json)
"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/git/gestao-redes-sociais/scripts/trilha'))

TITULO = 'Treinamento do Marketplace Connect do zero | Trilha gamificada com IA no ChatGPT'
LINK = 'https://l.tiops.com.br/automatizar-loja?o=youtube'

TAGS = ['marketplace connect', 'treino mac', 'treinamento marketplace connect', 'chatgpt', 'ia para marketplaces',
        'inteligência artificial', 'treinamento gamificado', 'gamificação', 'conector mcp', 'servidor mcp',
        'mcp no chatgpt', 'claude', 'mercado livre', 'shopee', 'ecommerce', 'ia para vendedores',
        'ia no mercado livre', 'automação com ia', 'tiops', 'itamar rocha']


def capitulos():
    import render, roteiro
    ab = json.load(open(os.path.join(AQUI, 'trab', 'tempos.json')))['abertura_s']
    linhas = ['0:00 Abertura']
    for s, t in roteiro.CAPITULOS:
        x = ab + (render.final_t(s) if s > 0 else 0.0)
        linhas.append('%d:%02d %s' % (x // 60, x % 60, t))
    return '\n'.join(linhas)


def descricao():
    return """Novidade no Marketplace Connect: o Treino MAC, um treinamento do zero com IA que roda dentro do ChatGPT (e também no Claude). Você instala o conector, escreve "@Treino MAC iniciar treinamento" e aprende a operar a sua loja na prática, numa trilha gamificada com missões, níveis, ranking, medalhas e habilidades.

👉 Conheça o Marketplace Connect: %s
🎥 Imersão IA para Marketplaces completa (3 horas, de graça): https://youtu.be/7VVhSzlHfdI

Capítulos:
%s

O que você vai ver:
• Como instalar o conector no ChatGPT (Plugins, Adicionar servidor MCP personalizado)
• Onde pegar a URL do conector no Marketplace Connect
• O ambiente gamificado: Força, Estoque, Vendas, Balcão e Estúdio
• Missões que liberam as próximas etapas, com o prompt exato em cada uma
• Ranking real dos sellers, conquistas e medalhas
• O treino funcionando no celular
• O que vem por aí: brindes, trilha Expert, certificação e programa de embaixador
• Indique e ganhe: o seu cupom e o link curto para divulgar

Não precisa ser programador. Só precisa da licença do Marketplace Connect.

#MarketplaceConnect #InteligenciaArtificial #ChatGPT #MercadoLivre #Ecommerce""" % (LINK, capitulos())


def confere(desc):
    n = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1
    assert n <= 500, 'tags com %d caracteres' % n
    assert len(TITULO) <= 100 and '<' not in desc and '>' not in desc and len(desc) <= 5000
    import render, roteiro
    ts = [render.final_t(s) for s, _ in roteiro.CAPITULOS] + [render.DUR]
    assert all(b - a >= 10 for a, b in zip(ts, ts[1:])), 'capítulo com menos de 10 s'
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
        'recordingDetails': {'recordingDate': '2026-10-29T00:00:00Z'},
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
