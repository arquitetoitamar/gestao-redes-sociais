"""Leitura do Drive com o token de loopback (drive.readonly + youtube)."""
import json, os, urllib.error, urllib.parse, urllib.request

TOK = os.path.expanduser('~/.hermes/credentials/google_drive_youtube.json')
SEG = os.path.expanduser('~/client_secret.json')
API = 'https://www.googleapis.com/drive/v3/'


def _tok():
    return json.load(open(TOK))


def refresh():
    t = _tok()
    c = json.load(open(SEG))['installed']
    novo = json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id': c['client_id'],
                                'client_secret': c['client_secret'],
                                'refresh_token': t['refresh_token'],
                                'grant_type': 'refresh_token'}).encode()))
    t['access_token'] = novo['access_token']
    json.dump(t, open(TOK, 'w'), indent=2)
    return t['access_token']


def _req(url, retry=True):
    r = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + _tok()['access_token']})
    try:
        return urllib.request.urlopen(r)
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            refresh()
            return _req(url, retry=False)
        raise


def listar(pasta):
    """Filhos diretos de uma pasta: id, nome, mime, tamanho."""
    saida, tok = [], ''
    while True:
        p = {'q': "'%s' in parents and trashed=false" % pasta,
             'fields': 'nextPageToken,files(id,name,mimeType,size,owners(emailAddress))',
             'pageSize': 200, 'orderBy': 'name'}
        if tok:
            p['pageToken'] = tok
        d = json.load(_req(API + 'files?' + urllib.parse.urlencode(p)))
        saida += d.get('files', [])
        tok = d.get('nextPageToken')
        if not tok:
            return saida


def arvore(raiz, nivel=0):
    """Percorre a pasta inteira e devolve (caminho, arquivo) de cada vídeo."""
    for f in listar(raiz):
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            for sub in arvore(f['id'], nivel + 1):
                yield (f['name'] + '/' + sub[0], sub[1])
        else:
            yield (f['name'], f)


def baixar(file_id, destino):
    with _req(API + 'files/%s?alt=media' % file_id) as r, open(destino, 'wb') as fh:
        while True:
            pedaco = r.read(1 << 20)
            if not pedaco:
                break
            fh.write(pedaco)
    return os.path.getsize(destino)
