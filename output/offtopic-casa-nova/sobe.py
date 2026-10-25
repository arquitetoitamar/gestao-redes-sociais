#!/usr/bin/env python3
"""Sobe o vídeo pro YouTube em blocos, com retomada.

Um PUT único de 863 MB estourou em broken pipe. O protocolo retomável do Google
aceita Content-Range: a cada bloco ele responde 308 dizendo quanto já recebeu,
então uma queda custa um bloco, não o arquivo inteiro.
"""
import json, os, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.expanduser('~/git/gestao-redes-sociais/scripts/trilha'))
import yt, textos

ARQ = 'final.mp4'
VIS = sys.argv[1] if len(sys.argv) > 1 else 'unlisted'
BLOCO = 8 * 1024 * 1024          # múltiplo de 256 KB, exigência do protocolo
TAM = os.path.getsize(ARQ)
ESTADO = '.sessao-upload.json'


def abre_sessao():
    yt.refresh()
    corpo = {
        'snippet': {'title': textos.TITULO, 'description': textos.DESC,
                    'tags': textos.TAGS, 'categoryId': '22',
                    'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
        'status': {'privacyStatus': VIS, 'selfDeclaredMadeForKids': False},
    }
    req = urllib.request.Request(
        'https://www.googleapis.com/upload/youtube/v3/videos'
        '?uploadType=resumable&part=snippet,status',
        data=json.dumps(corpo).encode(),
        headers={'Authorization': 'Bearer ' + yt._tok()['access_token'],
                 'Content-Type': 'application/json; charset=UTF-8',
                 'X-Upload-Content-Length': str(TAM),
                 'X-Upload-Content-Type': 'video/mp4'},
        method='POST')
    url = urllib.request.urlopen(req).headers['Location']
    json.dump({'url': url, 'tam': TAM}, open(ESTADO, 'w'))
    return url


def ja_recebido(url):
    """Pergunta ao servidor onde parou. 308 + Range: bytes=0-N."""
    req = urllib.request.Request(url, data=b'', method='PUT',
                                 headers={'Content-Range': 'bytes */%d' % TAM})
    try:
        urllib.request.urlopen(req)
        return TAM                      # 2xx = já acabou
    except urllib.error.HTTPError as e:
        if e.code in (308, 503):
            r = e.headers.get('Range')
            return int(r.split('-')[1]) + 1 if r else 0
        raise


def manda(url, ini):
    with open(ARQ, 'rb') as f:
        while ini < TAM:
            f.seek(ini)
            dados = f.read(BLOCO)
            fim = ini + len(dados) - 1
            req = urllib.request.Request(
                url, data=dados, method='PUT',
                headers={'Content-Length': str(len(dados)),
                         'Content-Range': 'bytes %d-%d/%d' % (ini, fim, TAM)})
            try:
                r = urllib.request.urlopen(req, timeout=180)
                return json.loads(r.read())           # último bloco devolve o vídeo
            except urllib.error.HTTPError as e:
                if e.code == 308:
                    rg = e.headers.get('Range')
                    ini = int(rg.split('-')[1]) + 1 if rg else fim + 1
                    sys.stderr.write('%5.1f%%\n' % (100.0 * ini / TAM))
                    continue
                raise
            except (urllib.error.URLError, OSError) as e:
                sys.stderr.write('queda (%s), reperguntando onde parou\n' % e)
                time.sleep(5)
                ini = ja_recebido(url)
    raise RuntimeError('acabaram os bytes sem resposta final')


if os.path.exists(ESTADO):
    st = json.load(open(ESTADO))
    url = st['url'] if st.get('tam') == TAM else abre_sessao()
else:
    url = abre_sessao()

inicio = ja_recebido(url)
sys.stderr.write('retomando em %.1f MB de %.1f MB\n' % (inicio / 1e6, TAM / 1e6))
r = manda(url, inicio)
os.path.exists(ESTADO) and os.unlink(ESTADO)

print(json.dumps({'id': r['id'],
                  'url': 'https://www.youtube.com/watch?v=' + r['id'],
                  'visibilidade': r['status']['privacyStatus'],
                  'titulo': r['snippet']['title']}, ensure_ascii=False, indent=1))
