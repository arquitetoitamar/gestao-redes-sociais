#!/usr/bin/env python3
"""Cria a pasta de recursos no Drive e sobe o kit de skills.

Usa um token só com drive.file: alcança apenas o que este script criar.
"""
import json, mimetypes, os, urllib.parse, urllib.request

TOK = os.path.expanduser('~/.hermes/credentials/google_drive_file.json')
SEG = os.path.expanduser('~/client_secret.json')
PAI = '1mUfVNY2nlZUT8_cscCxl0ppIR9pFOXMP'
KIT = os.path.expanduser('~/midia-tmp/claude/kit-skills')


def tokn():
    return json.load(open(TOK))['access_token']


def refresh():
    t = json.load(open(TOK))
    c = json.load(open(SEG))['installed']
    n = json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id': c['client_id'],
                                'client_secret': c['client_secret'],
                                'refresh_token': t['refresh_token'],
                                'grant_type': 'refresh_token'}).encode()))
    t['access_token'] = n['access_token']
    json.dump(t, open(TOK, 'w'), indent=2)


def pasta(nome, pai):
    corpo = json.dumps({'name': nome, 'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [pai]}).encode()
    r = urllib.request.Request('https://www.googleapis.com/drive/v3/files?fields=id,name',
                               data=corpo, method='POST',
                               headers={'Authorization': 'Bearer ' + tokn(),
                                        'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(r))['id']


def arquivo(caminho, pai):
    nome = os.path.basename(caminho)
    tipo = mimetypes.guess_type(nome)[0] or 'text/plain'
    dados = open(caminho, 'rb').read()
    meta = json.dumps({'name': nome, 'parents': [pai]}).encode()
    lim = b'-----limite-kit-skills'
    corpo = (b'--' + lim + b'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' +
             meta + b'\r\n--' + lim + b'\r\nContent-Type: ' + tipo.encode() + b'\r\n\r\n' +
             dados + b'\r\n--' + lim + b'--')
    r = urllib.request.Request(
        'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name',
        data=corpo, method='POST',
        headers={'Authorization': 'Bearer ' + tokn(),
                 'Content-Type': 'multipart/related; boundary=' + lim.decode()})
    return json.load(urllib.request.urlopen(r))


def publica(file_id):
    corpo = json.dumps({'role': 'reader', 'type': 'anyone'}).encode()
    r = urllib.request.Request(
        'https://www.googleapis.com/drive/v3/files/%s/permissions' % file_id,
        data=corpo, method='POST',
        headers={'Authorization': 'Bearer ' + tokn(), 'Content-Type': 'application/json'})
    urllib.request.urlopen(r)


if __name__ == '__main__':
    refresh()
    raiz = pasta('Recursos — Kit de Skills', PAI)
    print('pasta criada:', raiz)
    mapa = {'': raiz}
    for dir_atual, subdirs, arqs in os.walk(KIT):
        rel = os.path.relpath(dir_atual, KIT)
        rel = '' if rel == '.' else rel
        if rel and rel not in mapa:
            mapa[rel] = pasta(os.path.basename(rel), mapa[os.path.dirname(rel)])
            print('  pasta', rel)
        for a in sorted(arqs):
            f = arquivo(os.path.join(dir_atual, a), mapa[rel])
            print('  arquivo', (rel + '/' if rel else '') + f['name'])
    publica(raiz)
    link = 'https://drive.google.com/drive/folders/' + raiz
    json.dump({'pasta': raiz, 'link': link},
              open(os.path.expanduser('~/midia-tmp/kit-skills.json'), 'w'), indent=2)
    print('\nlink público de leitura:', link)
