#!/usr/bin/env python3
"""Sobe a aula como NÃO LISTADA no canal Itamar Rocha, põe a capa (thumb.jpg da pasta) e
coloca na playlist "GestorPro — Treinamento" (cria não listada se não existir).
Título, descrição e tags vêm de roteiro.AULA; capítulos, dos tempos das seções.

  python3 publica.py <pasta-da-aula> texto    mostra título, descrição e tags
  python3 publica.py <pasta-da-aula> sobe     publica (grava publicado.json na pasta)
"""
import json, os, sys, urllib.request

AQUI = os.path.abspath(sys.argv[1])
MOTOR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, MOTOR)
sys.path.append(os.path.expanduser('~/git/gestao-redes-sociais/scripts/trilha'))
import roteiro as R

PLAYLIST = 'GestorPro — Treinamento'
TAGS_BASE = ['gestorpro', 'treinamento gestorpro', 'agentes de ia', 'ia para marketplaces', 'mercado livre', 'tiops']


def titulo():
    return '%s | Treinamento GestorPro' % R.AULA['titulo']


def tags():
    out = []
    for t in R.AULA.get('tags', []) + TAGS_BASE:
        if t not in out:
            out.append(t)
    while sum(len(t) + (2 if ' ' in t else 0) for t in out) + len(out) - 1 > 480:
        out.pop()
    return out


def capitulos():
    import aula
    linhas = ['0:00 Abertura']
    for s in aula.SECS:
        x = aula.INI[s]
        linhas.append('%d:%02d %s' % (x // 60, x % 60, R.CAPITULOS[s]))
    return '\n'.join(linhas)


def descricao():
    itens = '\n'.join('• ' + i for i in R.AULA.get('itens', []))
    return ('%s\n\nCapítulos:\n%s\n\nNesta aula:\n%s\n\n'
            'Narração com o avatar e a voz do Itamar gerados por IA (HeyGen). '
            'Valores e nomes de produto aparecem ocultos na tela.') % (R.AULA['descricao'], capitulos(), itens)


def confere(desc):
    assert len(titulo()) <= 100 and '<' not in desc and '>' not in desc and len(desc) <= 5000
    import aula
    ini = [aula.INI[s] for s in aula.SECS] + [aula.FIM_AULA]
    assert all(b - a >= 10 for a, b in zip(ini, ini[1:])), 'seção com menos de 10 s apaga os capítulos'


def api(tok, metodo, url, corpo=None):
    req = urllib.request.Request(url, method=metodo, data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8'})
    return json.loads(urllib.request.urlopen(req).read() or b'{}')


def playlist(tok):
    r = api(tok, 'GET', 'https://www.googleapis.com/youtube/v3/playlists?part=snippet&mine=true&maxResults=50')
    for p in r.get('items', []):
        if p['snippet']['title'] == PLAYLIST:
            return p['id']
    p = api(tok, 'POST', 'https://www.googleapis.com/youtube/v3/playlists?part=snippet,status', {
        'snippet': {'title': PLAYLIST, 'defaultLanguage': 'pt-BR',
                    'description': 'Aulas do GestorPro, o escritório de agentes de IA da Tiops para quem vende em marketplaces.'},
        'status': {'privacyStatus': 'unlisted'}})
    return p['id']


def sobe():
    import yt
    yt.refresh()
    tok = yt._tok()['access_token']
    video = os.path.join(AQUI, 'videos', 'final.mp4')
    desc = descricao()
    confere(desc)
    corpo = {'snippet': {'title': titulo(), 'description': desc, 'tags': tags(), 'categoryId': '27',
                         'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
             'status': {'privacyStatus': 'unlisted', 'selfDeclaredMadeForKids': False, 'embeddable': True,
                        'containsSyntheticMedia': True}}
    tam = os.path.getsize(video)
    req = urllib.request.Request(
        'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status&notifySubscribers=false',
        data=json.dumps(corpo).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                 'X-Upload-Content-Length': str(tam), 'X-Upload-Content-Type': 'video/mp4'})
    sessao = urllib.request.urlopen(req).headers['Location']
    with open(video, 'rb') as f:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(
            sessao, data=f, method='PUT', headers={'Content-Length': str(tam)}), timeout=3600).read())
    vid = d['id']
    res = {'id': vid, 'url': 'https://youtu.be/' + vid}
    thumb = os.path.join(AQUI, 'thumb.jpg')
    if os.path.exists(thumb):
        with open(thumb, 'rb') as f:
            r = urllib.request.urlopen(urllib.request.Request(
                'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + vid, data=f.read(), method='POST',
                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'}))
            res['thumb'] = r.status
    pl = playlist(tok)
    api(tok, 'POST', 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
        {'snippet': {'playlistId': pl, 'resourceId': {'kind': 'youtube#video', 'videoId': vid}}})
    res['playlist'] = pl
    res['playlist_url'] = 'https://www.youtube.com/playlist?list=' + pl
    json.dump(res, open(os.path.join(AQUI, 'publicado.json'), 'w'), indent=1)
    print(res)


if __name__ == '__main__':
    modo = sys.argv[2]
    sys.argv = [sys.argv[0], AQUI]          # o motor (aula.py) lê a pasta em argv[1]
    if modo == 'texto':
        d = descricao()
        confere(d)
        print(titulo(), '\n\n' + d, '\n\nTAGS:', ', '.join(tags()))
    elif modo == 'sobe':
        sobe()
