"""Sobe saida/reel_mc_es_post.mp4 como Short público, em espanhol (es-419), com capa."""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(AQUI, 'saida', 'reel_mc_es_post.mp4')
DESC = """Tu IA ya responde sobre tu tienda. ¿Y si la operara?

Marketplace Connect conecta Claude o ChatGPT a tu cuenta de Mercado Libre: le pides en español, la IA prepara el cambio y te lo muestra, tú apruebas y ella ejecuta. Una autorización, sin código.

Ya disponible en Mercado Libre Argentina y México:
Argentina: https://l.tiops.com.br/ar?o=youtube
México: https://l.tiops.com.br/mx?o=youtube

Conversación ilustrativa, tienda y números ficticios. Voz generada con IA a partir de la voz de Itamar.
#mercadolibre #mercadolibreargentina #mercadolibremexico #inteligenciaartificial #chatgpt"""
corpo = {
    'snippet': {'title': 'Tu IA ahora opera tu Mercado Libre (Argentina y México) #shorts', 'description': DESC,
                'tags': ['mercado libre', 'mercado libre argentina', 'mercado libre mexico', 'vender en mercado libre',
                         'chatgpt', 'claude', 'inteligencia artificial', 'ecommerce', 'marketplace connect', 'tiops'],
                'categoryId': '28', 'defaultLanguage': 'es-419', 'defaultAudioLanguage': 'es-419'},
    'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True},
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
                                data=open(os.path.join(AQUI, 'saida', 'capa.jpg'), 'rb').read(), method='POST',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'})
    urllib.request.urlopen(th); capa = 'ok'
except urllib.error.HTTPError as e:
    capa = 'falhou %s %s' % (e.code, e.read().decode()[:200])
print('capa', capa)
json.dump({'id': vid, 'url': 'https://youtube.com/shorts/' + vid, 'status': 'publico', 'capa': capa},
          open(os.path.join(AQUI, 'youtube_publicado.json'), 'w'), indent=1)
