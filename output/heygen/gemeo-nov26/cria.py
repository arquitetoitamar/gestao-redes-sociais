"""Gêmeo digital novo (nov/26): sobe o vídeo de treino e cria o look no grupo do Itamar.
O grupo fcd7fefe… já tem consentimento aceito, então o look novo herda a autorização.
  python3 cria.py sobe     -> asset_id em estado.json
  python3 cria.py cria     -> look/grupo em estado.json
  python3 cria.py status   -> status do treino
"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '../../..'))
for l in open(os.path.join(RAIZ, '.env')):
    if l.startswith('HEYGEN_API_KEY='):
        KEY = l.split('=', 1)[1].strip().strip('"')
B = 'https://api.heygen.com/v3'
GRUPO = 'fcd7fefe06494ca9802154d07e4d4cd7'
EST = os.path.join(AQUI, 'estado.json')
est = json.load(open(EST)) if os.path.exists(EST) else {}


def api(met, path, corpo=None):
    req = urllib.request.Request(B + path, method=met, headers={'X-Api-Key': KEY, 'Content-Type': 'application/json'},
                                 data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        raise SystemExit('%s %s -> %s %s' % (met, path, e.code, e.read().decode()[:600]))


def salva():
    json.dump(est, open(EST, 'w'), indent=1, ensure_ascii=False)


cmd = sys.argv[1]
if cmd == 'sobe':
    arq = os.path.join(AQUI, 'treino.mp4')
    tam = os.path.getsize(arq)
    ini = api('POST', '/assets/direct-uploads', {'filename': 'itamar_treino_nov26.mp4', 'content_type': 'video/mp4', 'size_bytes': tam})['data']
    put = urllib.request.Request(ini['upload_url'], method='PUT', data=open(arq, 'rb').read(), headers=ini.get('upload_headers') or {})
    print('PUT', urllib.request.urlopen(put, timeout=600).status)
    fim = api('POST', '/assets/%s/complete' % ini['asset_id'])['data']
    est['asset_id'] = ini['asset_id']; salva()
    print('asset', ini['asset_id'], fim.get('status'))
elif cmd == 'cria':
    r = api('POST', '/avatars', {'type': 'digital_twin', 'name': 'Itamar nov26', 'avatar_group_id': GRUPO,
                                 'file': {'type': 'asset_id', 'asset_id': est['asset_id']}})['data']
    est['look_id'] = r['avatar_item']['id']
    est['voz_clonada_do_treino'] = r['avatar_item'].get('default_voice_id')
    est['grupo'] = r['avatar_group']['id']; salva()
    print(json.dumps({k: est[k] for k in ('look_id', 'grupo', 'voz_clonada_do_treino')}))
elif cmd == 'status':
    d = api('GET', '/avatars/looks/%s' % est['look_id'])['data']
    print(d.get('status'), d.get('error'), d.get('supported_api_engines'))
