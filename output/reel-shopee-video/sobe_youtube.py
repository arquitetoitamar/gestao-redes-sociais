"""Sobe reel_shopee_video.mp4 como Short agendado (privado com publishAt) e põe a capa."""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(AQUI, 'reel_shopee_video.mp4')
QUANDO = '2026-11-03T21:00:00Z'          # 18:00 em São Paulo
DESC = """Agora o Marketplace Connect gerencia seus vídeos da Shopee Vídeo.

Você pede em português, no ChatGPT ou no Claude: publica o vídeo com o link do produto, edita o título e vê as visualizações e quem está assistindo. Tudo sem abrir o painel da Shopee.

Conheça o Marketplace Connect: https://l.tiops.com.br/connect-saiba-mais?o=youtube

Narração com voz sintética do Itamar. Telas ilustrativas.
#shopee #shopeevideo #marketplace #chatgpt #claude"""
corpo = {
    'snippet': {'title': 'Shopee Vídeo no ChatGPT e no Claude: nova integração #shorts', 'description': DESC,
                'tags': ['shopee', 'shopee video', 'marketplace connect', 'chatgpt', 'claude', 'ecommerce', 'tiops'],
                'categoryId': '28', 'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
    'status': {'privacyStatus': 'private', 'publishAt': QUANDO, 'selfDeclaredMadeForKids': False,
               'containsSyntheticMedia': True},
}
assert '<' not in DESC and '>' not in DESC
tok = yt.refresh()
tam = os.path.getsize(ARQ)
req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                             data=json.dumps(corpo).encode(), method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                      'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam)})
loc = urllib.request.urlopen(req).headers['Location']
up = urllib.request.Request(loc, data=open(ARQ, 'rb').read(), method='PUT',
                            headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4'})
v = json.load(urllib.request.urlopen(up, timeout=600))
vid = v['id']
print('video', vid, v['status'])
try:
    th = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + vid,
                                data=open(os.path.join(AQUI, 'capa.jpg'), 'rb').read(), method='POST',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'})
    urllib.request.urlopen(th); capa = 'ok'
except urllib.error.HTTPError as e:
    capa = 'falhou %s %s' % (e.code, e.read().decode()[:200])
print('capa', capa)
json.dump({'id': vid, 'url': 'https://youtube.com/shorts/' + vid, 'status': 'agendado', 'publishAt': QUANDO, 'capa': capa},
          open(os.path.join(AQUI, 'youtube_agendado.json'), 'w'), indent=1)
