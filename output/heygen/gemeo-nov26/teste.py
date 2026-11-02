"""Teste do gêmeo nov26 com a voz oficial (c463ef5b), em dois motores.
  python3 teste.py cria   -> dispara avatar_iii e avatar_v
  python3 teste.py baixa  -> espera e baixa teste_<motor>.mp4
"""
import json, os, sys, time, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(AQUI, '../../../.env')):
    if l.startswith('HEYGEN_API_KEY='):
        KEY = l.split('=', 1)[1].strip().strip('"')
B = 'https://api.heygen.com/v3'
EST = os.path.join(AQUI, 'estado.json'); est = json.load(open(EST))
VOZ = 'c463ef5bf11146d49bf754fa1e515401'
TEXTO = ('Antes de contratar alguém só pra emitir nota fiscal, olha isso. '
         'Você manda a venda pro ChatGPT ou pro Claude, em português, e a nota sai autorizada na SEFAZ.')

def api(met, path, corpo=None):
    req = urllib.request.Request(B + path, method=met, headers={'X-Api-Key': KEY, 'Content-Type': 'application/json'},
                                 data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        raise SystemExit('%s %s -> %s %s' % (met, path, e.code, e.read().decode()[:600]))

if sys.argv[1] == 'cria':
    est['testes'] = {}
    for eng in ('avatar_iii', 'avatar_v'):
        r = api('POST', '/videos', {'type': 'avatar', 'avatar_id': est['look_id'], 'script': TEXTO, 'voice_id': VOZ,
                                    'resolution': '1080p', 'aspect_ratio': '9:16', 'engine': {'type': eng}})['data']
        est['testes'][eng] = r.get('video_id') or r.get('id')
        print(eng, est['testes'][eng])
    json.dump(est, open(EST, 'w'), indent=1)
else:
    pend = dict(est['testes'])
    while pend:
        for eng, vid in list(pend.items()):
            d = api('GET', '/videos/%s' % vid)['data']
            st = d.get('status')
            if st == 'completed':
                urllib.request.urlretrieve(d['video_url'], os.path.join(AQUI, 'teste_%s.mp4' % eng))
                print(eng, 'ok', d.get('duration')); pend.pop(eng)
            elif st == 'failed':
                print(eng, 'FALHOU', d.get('failure_message') or d.get('error')); pend.pop(eng)
        if pend:
            time.sleep(20)
