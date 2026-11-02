#!/usr/bin/env python3
"""Clone instantâneo da voz do Itamar na HeyGen a partir dos vídeos curtos do canal.

  python3 clona.py monta <id>:<ini>-<fim> ...   junta os trechos escolhidos em amostra.wav
                                               (pausas longas encurtadas, máx. 3 min)
  python3 clona.py cria "<nome>"               sobe amostra.wav e cria a voz (mode instant)
  python3 clona.py fala <voice_id> "<texto>"    gera um teste de fala (gasta saldo da carteira)

Só os 3 primeiros minutos da gravação entram no clone (doc da HeyGen). O áudio
vai como foi gravado: a HeyGen limpa o ruído (remove_background_noise).
O resultado fica em clone.json.
"""
import json, os, subprocess, sys, time, urllib.error, urllib.request, uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(AQUI, 'audio')
AMOSTRA = os.path.join(AQUI, 'amostra.wav')
REPO = os.path.abspath(os.path.join(AQUI, '..', '..', '..'))
BASE = 'https://api.heygen.com'


def chave():
    for linha in open(os.path.join(REPO, '.env')):
        if linha.startswith('HEYGEN_API_KEY='):
            return linha.split('=', 1)[1].strip()
    sys.exit('HEYGEN_API_KEY não está no .env')


def api(caminho, corpo=None, metodo=None, extra=None):
    h = {'X-Api-Key': chave(), 'Accept': 'application/json'}
    dados = None
    if corpo is not None:
        dados = json.dumps(corpo).encode()
        h['Content-Type'] = 'application/json'
    h.update(extra or {})
    req = urllib.request.Request(BASE + caminho, data=dados, headers=h, method=metodo or ('POST' if dados else 'GET'))
    try:
        return json.loads(urllib.request.urlopen(req, timeout=120).read())
    except urllib.error.HTTPError as e:
        sys.exit('HeyGen %s %s: %s' % (e.code, caminho, e.read()[:500].decode()))


def monta(trechos):
    partes = []
    for i, t in enumerate(trechos):
        vid, faixa = t.rsplit(':', 1)
        ini, fim = (float(x) for x in faixa.split('-'))
        out = os.path.join(AQUI, 'trecho_%02d.wav' % i)
        # encurta silêncios acima de 0,6 s para 0,3 s; nada de EQ ou compressão
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ini), '-to', str(fim),
                        '-i', os.path.join(AUDIO, vid + '.wav'), '-af',
                        'silenceremove=stop_periods=-1:stop_duration=0.6:stop_threshold=-40dB:stop_silence=0.3',
                        '-ar', '44100', '-ac', '1', out], check=True)
        partes.append(out)
    lista = os.path.join(AQUI, 'lista.txt')
    open(lista, 'w').write(''.join("file '%s'\n" % p for p in partes))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista,
                    '-t', '180', AMOSTRA], check=True)
    for p in partes + [lista]:
        os.remove(p)
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', AMOSTRA],
                       capture_output=True, text=True).stdout.strip()
    print('amostra.wav: %.1f s, %d KB' % (float(d), os.path.getsize(AMOSTRA) // 1024))


def sobe(arquivo):
    """POST /v3/assets (multipart)."""
    limite = uuid.uuid4().hex
    corpo = (('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
              'Content-Type: audio/wav\r\n\r\n' % (limite, os.path.basename(arquivo))).encode()
             + open(arquivo, 'rb').read() + ('\r\n--%s--\r\n' % limite).encode())
    req = urllib.request.Request(BASE + '/v3/assets', data=corpo, method='POST', headers={
        'X-Api-Key': chave(), 'Content-Type': 'multipart/form-data; boundary=' + limite})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=300).read())['data']
    except urllib.error.HTTPError as e:
        sys.exit('upload falhou %s: %s' % (e.code, e.read()[:400].decode()))
    return d.get('asset_id') or d.get('id')


def cria(nome):
    asset = sobe(AMOSTRA)
    print('asset', asset)
    r = api('/v3/models/audio/voices', {
        'mode': 'instant', 'name': nome, 'language': 'pt',
        'audio': [{'type': 'asset_id', 'asset_id': asset}],
        'remove_background_noise': True,
    }, extra={'Idempotency-Key': 'clone-itamar-' + nome.replace(' ', '-').lower()[:40]})
    vid = r['data']['voice_id']
    for _ in range(60):
        v = api('/v3/models/audio/voices/' + vid)['data']
        if v.get('status') in ('ACTIVE', 'FAILED'):
            break
        time.sleep(3)
    json.dump({'voice_id': vid, 'nome': nome, 'asset_id': asset, 'status': v.get('status'),
               'falha': v.get('failure_reason'), 'criado_em': time.strftime('%Y-%m-%d %H:%M')},
              open(os.path.join(AQUI, 'clone.json'), 'w'), indent=1, ensure_ascii=False)
    print('voz', vid, v.get('status'), v.get('failure_reason') or '')


def fala(voice_id, texto):
    r = api('/v3/models/audio/tts', {'model': 'heygen-voice-1', 'voice_id': voice_id, 'text': texto})
    d = r['data']
    url = d.get('audio_url') or d.get('url')
    out = os.path.join(AQUI, 'teste-%s.wav' % voice_id[:8])
    urllib.request.urlretrieve(url, out)
    print(out)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'monta':
        monta(sys.argv[2:])
    elif cmd == 'cria':
        cria(sys.argv[2])
    elif cmd == 'fala':
        fala(sys.argv[2], sys.argv[3])
