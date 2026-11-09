"""Sobe reel_madeiramadeira.mp4 como Short, agendado (publishAt), com capa.
uso: python3 sobe_youtube.py "2026-11-09T21:00:00Z"   (horário em UTC; 21:00Z = 18:00 BRT)"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(AQUI, 'reel_madeiramadeira.mp4')
QUANDO = sys.argv[1]
DESC = """Novidade: a MadeiraMadeira chegou no Marketplace Connect.

Conecte a sua loja da MadeiraMadeira no Claude ou no ChatGPT e peça em português: pedidos do dia, produtos sem estoque e as vendas junto com Mercado Livre, Shopee, Amazon e as outras lojas, numa conversa só. Sem código. E nada muda na loja sem o seu OK.

Saiba mais: https://l.tiops.com.br/madeira?o=youtube

Exemplo ilustrativo, com números fictícios.
#madeiramadeira #marketplace #claude"""
corpo = {
    'snippet': {'title': 'Novidade: MadeiraMadeira no Claude com o Marketplace Connect #shorts', 'description': DESC,
                'tags': ['madeiramadeira', 'marketplace connect', 'claude', 'chatgpt', 'ia para marketplace',
                         'mercado livre', 'vender na madeiramadeira', 'ecommerce', 'tiops'],
                'categoryId': '28', 'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
    'status': {'privacyStatus': 'private', 'publishAt': QUANDO, 'selfDeclaredMadeForKids': False,
               'containsSyntheticMedia': False},
}
assert '<' not in DESC and '>' not in DESC and len(corpo['snippet']['title']) <= 100
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
json.dump({'id': vid, 'url': 'https://youtube.com/shorts/' + vid, 'status': 'agendado ' + QUANDO, 'capa': capa},
          open(os.path.join(AQUI, 'youtube_publicado.json'), 'w'), indent=1)
