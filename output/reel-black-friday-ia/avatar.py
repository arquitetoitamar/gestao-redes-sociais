"""Avatar do Itamar (gêmeo nov26 + voz c463ef5b) para o Reel da Black Friday com IA.
  python3 avatar.py cria   -> dispara avatar_v 9:16 1080p
  python3 avatar.py baixa  -> espera e baixa videos/avatar.mp4
"""
import json, os, sys, time, urllib.request, urllib.error
AQUI = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(AQUI, '../../.env')):
    if l.startswith('HEYGEN_API_KEY='):
        KEY = l.split('=', 1)[1].strip().strip('"')
B = 'https://api.heygen.com/v3'
EST = os.path.join(AQUI, 'estado.json')
est = json.load(open(EST)) if os.path.exists(EST) else {}
LOOK, VOZ = '5147cda8da2612d8b2a6b7a3aaeca01a', 'c463ef5bf11146d49bf754fa1e515401'
TEXTO = open(os.path.join(AQUI, 'roteiro.txt'), encoding='utf-8').read().strip()

def api(met, path, corpo=None):
    req = urllib.request.Request(B + path, method=met, headers={'X-Api-Key': KEY, 'Content-Type': 'application/json'},
                                 data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        raise SystemExit('%s %s -> %s %s' % (met, path, e.code, e.read().decode()[:600]))

if sys.argv[1] == 'cria':
    r = api('POST', '/videos', {'type': 'avatar', 'avatar_id': LOOK, 'script': TEXTO, 'voice_id': VOZ,
                                'resolution': '1080p', 'aspect_ratio': '9:16', 'engine': {'type': 'avatar_v'}})['data']
    est['video_id'] = r.get('video_id') or r.get('id'); json.dump(est, open(EST, 'w'), indent=1); print('criado', est['video_id'])
else:
    os.makedirs(os.path.join(AQUI, 'videos'), exist_ok=True)
    for _ in range(60):
        d = api('GET', '/videos/%s' % est['video_id'])['data']
        if d.get('status') == 'completed':
            urllib.request.urlretrieve(d['video_url'], os.path.join(AQUI, 'videos', 'avatar.mp4')); print('ok', d.get('duration')); break
        if d.get('status') == 'failed':
            raise SystemExit('FALHOU %s' % (d.get('failure_message') or d.get('error')))
        time.sleep(20)
