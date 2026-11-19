"""Sobe um vídeo vertical como YouTube Short a partir de um spec JSON.

uso: python3 sobe_short.py <spec.json> agora | nao_listado | "2026-11-17T21:00:00Z"   (UTC; 21:00Z = 18:00 BRT)
(serve também para vídeo horizontal comum; o link sai em watch?v= quando o spec tem "formato": "longo")

spec (caminhos relativos à pasta do spec):
  {"arquivo": "video.mp4", "titulo": "... #shorts", "descricao": "...", "tags": [...],
   "sintetico": false, "capa": "capa.jpg"}
Grava <spec>_publicado.json ao lado do spec.
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yt

SPEC, QUANDO = sys.argv[1], sys.argv[2]
AQUI = os.path.dirname(os.path.abspath(SPEC))
s = json.load(open(SPEC, encoding='utf-8'))
ARQ = os.path.join(AQUI, s['arquivo'])
TAGS = s['tags']
assert '<' not in s['descricao'] and '>' not in s['descricao'], 'YouTube recusa < e > na descrição'
assert len(s['titulo']) <= 100, 'título > 100'
assert sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1 <= 500, 'tags > 500'

corpo = {
    'snippet': {'title': s['titulo'], 'description': s['descricao'], 'tags': TAGS,
                'categoryId': s.get('categoria', '28'), 'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
    'status': {'privacyStatus': 'private', 'publishAt': QUANDO, 'selfDeclaredMadeForKids': False,
               'containsSyntheticMedia': bool(s.get('sintetico'))},
}
if QUANDO in ('agora', 'nao_listado'):
    corpo['status'].pop('publishAt')
    corpo['status']['privacyStatus'] = 'public' if QUANDO == 'agora' else 'unlisted'

tok = yt.refresh()
tam = os.path.getsize(ARQ)
req = urllib.request.Request(
    'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
    data=json.dumps(corpo).encode(), method='POST',
    headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
             'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam)})
loc = urllib.request.urlopen(req).headers['Location']
with open(ARQ, 'rb') as f:
    up = urllib.request.Request(loc, data=f, method='PUT',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4',
                                         'Content-Length': str(tam)})
    v = json.load(urllib.request.urlopen(up, timeout=600))
vid = v['id']
print('video', vid, v['status'])

capa = 'sem capa'
if s.get('capa'):
    try:
        th = urllib.request.Request(
            'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + vid,
            data=open(os.path.join(AQUI, s['capa']), 'rb').read(), method='POST',
            headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'})
        urllib.request.urlopen(th)
        capa = 'ok'
    except urllib.error.HTTPError as e:
        capa = 'falhou %s %s' % (e.code, e.read().decode()[:200])
print('capa', capa)
url = ('https://youtu.be/' if s.get('formato') == 'longo' else 'https://youtube.com/shorts/') + vid
estado = {'agora': 'publico', 'nao_listado': 'nao listado'}.get(QUANDO, 'agendado ' + QUANDO)
print(url)
json.dump({'id': vid, 'url': url, 'status': estado, 'capa': capa},
          open(os.path.splitext(os.path.abspath(SPEC))[0] + '_publicado.json', 'w'), indent=1)
