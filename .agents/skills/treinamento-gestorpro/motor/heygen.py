#!/usr/bin/env python3
"""Avatar do Itamar (gêmeo digital) falando a narração, um vídeo por seção.

  python3 heygen.py <pasta> cria <secao>|todas [engine]   gera a(s) seção(ões) de narracao.md
  python3 heygen.py <pasta> espera     baixa as prontas -> videos/av-N.mp4 e tira o tempo por palavra (whisper)
  python3 heygen.py <pasta> saldo      saldo da carteira da API (US$; ~0,62/min no avatar_iii)
Estado em trab/heygen.json. Não imprime a chave.
"""
import json, os, re, subprocess, sys, time, urllib.request, urllib.error

AQUI = os.path.abspath(sys.argv[1])
REPO = os.path.expanduser('~/git/gestao-redes-sociais')
WHISPER = os.path.expanduser('~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin')
EST = os.path.join(AQUI, 'trab', 'heygen.json')
AVATAR = 'fcd7fefe06494ca9802154d07e4d4cd7'
VOZ = '8bed0b172a10497cb244a2bd4fb73503'


def chave():
    for l in open(os.path.join(REPO, '.env')):
        if l.startswith('HEYGEN_API_KEY='):
            return l.split('=', 1)[1].strip()


def api(metodo, caminho, corpo=None):
    req = urllib.request.Request('https://api.heygen.com' + caminho, method=metodo,
                                 data=json.dumps(corpo).encode() if corpo else None,
                                 headers={'X-Api-Key': chave(), 'Content-Type': 'application/json'})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        return {'erro': e.code, 'msg': e.read().decode()[:600]}


def secoes():
    txt = open(os.path.join(AQUI, 'narracao.md')).read()
    out = {}
    for m in re.finditer(r'^## (\d+)\. .*?\n(.*?)(?=^## |\Z)', txt, re.S | re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def estado():
    return json.load(open(EST)) if os.path.exists(EST) else {}


def saldo():
    return api('GET', '/v3/users/me')['data']['wallet']['remaining_balance']


def cria(sec, engine='avatar_iii'):
    texto = secoes()[sec]
    corpo = {'type': 'avatar', 'avatar_id': AVATAR, 'script': texto, 'voice_id': VOZ,
             'resolution': '720p', 'aspect_ratio': '16:9', 'engine': {'type': engine}}
    r = api('POST', '/v3/videos', corpo)
    st = estado()
    st[sec] = {'resp': r, 'engine': engine, 'chars': len(texto)}
    json.dump(st, open(EST, 'w'), indent=1)
    print(json.dumps(r)[:500])


def espera():
    st = estado()
    for sec, d in st.items():
        vid = (d['resp'].get('data') or {}).get('video_id') or d['resp'].get('video_id')
        if not vid or d.get('ok'):
            continue
        r = api('GET', '/v3/videos/' + vid)
        dd = r.get('data', r)
        status = dd.get('status')
        print(sec, vid, status, (dd.get('duration')), (dd.get('error') or '')[:200] if isinstance(dd.get('error'), str) else dd.get('error'))
        url = dd.get('video_url') or dd.get('url')
        if status in ('completed', 'success') and url:
            dst = os.path.join(AQUI, 'videos', 'av-%s.mp4' % sec)
            urllib.request.urlretrieve(url, dst)
            d['ok'] = dst
            d['dur'] = dd.get('duration')
            wav = os.path.join(AQUI, 'trab', 'av-%s.wav' % sec)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', dst, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav], check=True)
            subprocess.run(['whisper-cli', '-m', WHISPER, '-l', 'pt', '-f', wav, '-ml', '1', '-oj', '-of',
                            os.path.join(AQUI, 'trab', 'pal-%s' % sec), '-np'], capture_output=True)
            os.remove(wav)
    json.dump(st, open(EST, 'w'), indent=1)


if __name__ == '__main__':
    os.makedirs(os.path.join(AQUI, 'trab'), exist_ok=True)
    os.makedirs(os.path.join(AQUI, 'videos'), exist_ok=True)
    c = sys.argv[2]
    if c == 'cria':
        alvo = list(secoes()) if sys.argv[3] == 'todas' else [sys.argv[3]]
        for sec in alvo:
            cria(sec, *(sys.argv[4:5]))
    elif c == 'espera':
        espera()
    elif c == 'saldo':
        print(saldo())
