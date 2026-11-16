"""Gêmeo digital do Itamar (look nov26) falando a narração gravada com a voz clonada (lip-sync pelo áudio).
  python3 avatar.py cria   -> sobe audio/voz.wav, dispara POST /v3/videos (avatar_iii, 9:16, 1080p)
  python3 avatar.py baixa  -> espera e baixa trab/avatar.mp4
"""
import json, os, sys, time, uuid, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__))
KEY = [l.split('=', 1)[1].strip().strip('"') for l in open(os.path.join(AQUI, '../../../.env')) if l.startswith('HEYGEN_API_KEY=')][0]
B = 'https://api.heygen.com'
LOOK = '5147cda8da2612d8b2a6b7a3aaeca01a'      # "Itamar nov26" (grupo fcd7fefe, consent aceito)
EST = os.path.join(AQUI, 'trab', 'heygen.json')


def api(met, path, corpo=None, raw=None, ctype='application/json'):
    req = urllib.request.Request(B + path, method=met, headers={'X-Api-Key': KEY, 'Content-Type': ctype},
                                 data=raw if raw is not None else (json.dumps(corpo).encode() if corpo is not None else None))
    try:
        return json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        raise SystemExit('%s %s -> %s %s' % (met, path, e.code, e.read().decode()[:800]))


if sys.argv[1] == 'cria':
    arq = os.path.join(AQUI, 'audio', 'voz.wav')
    lim = uuid.uuid4().hex
    corpo = (('--%s\r\nContent-Disposition: form-data; name="file"; filename="voz.wav"\r\nContent-Type: audio/wav\r\n\r\n' % lim).encode()
             + open(arq, 'rb').read() + ('\r\n--%s--\r\n' % lim).encode())
    up = api('POST', '/v3/assets', raw=corpo, ctype='multipart/form-data; boundary=' + lim)['data']
    print('asset', {k: (v if k != 'url' else str(v)[:60]) for k, v in up.items()})
    corpo = {'type': 'avatar', 'avatar_id': LOOK, 'resolution': '1080p', 'aspect_ratio': '9:16',
             'engine': {'type': 'avatar_iii'}}
    if sys.argv[2:] == ['url']:
        corpo['audio_url'] = up['url']
    else:
        corpo['audio_asset_id'] = up.get('asset_id') or up.get('id')
    r = api('POST', '/v3/videos', corpo)['data']
    json.dump({'asset': up, 'video': r}, open(EST, 'w'), indent=1)
    print('video', r)
else:
    vid = json.load(open(EST))['video']['video_id']
    while True:
        d = api('GET', '/v3/videos/%s' % vid)['data']
        st = d.get('status')
        if st == 'completed':
            urllib.request.urlretrieve(d['video_url'], os.path.join(AQUI, 'trab', 'avatar.mp4'))
            print('ok', d.get('duration')); break
        if st == 'failed':
            sys.exit('FALHOU %s' % (d.get('failure_message') or d.get('error')))
        print(st, flush=True); time.sleep(20)
