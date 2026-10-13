#!/usr/bin/env python3
"""Publica ou troca uma aula da trilha, mantendo nome, descrição e posição.

    python3 aula.py <numero> <arquivo.mp4>     publica ou substitui a aula
    python3 aula.py --estado                   mostra a playlist e o manifesto
    python3 aula.py --sincroniza               põe a playlist igual ao manifesto

O manifesto é a fonte da verdade: ele diz o título, a descrição, as tags e a
ordem. O script nunca inventa texto — se a aula não está no manifesto, ele para.

Ao substituir uma aula que este script publicou, o vídeo antigo vira privado
(não é apagado) e sai da playlist. Vídeo que já existia no canal antes da
trilha nunca é alterado: ele só sai da playlist.
"""
import json, os, sys, urllib.error, urllib.request

import yt

MANIFESTO = os.path.expanduser('~/midia-tmp/manifesto-trilha-basica.json')
ESPELHO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', '..', 'output', 'trilha-basica',
                       'manifesto-trilha-basica.json')


def carrega():
    return json.load(open(MANIFESTO, encoding='utf-8'))


def salva(m):
    for destino in (MANIFESTO, ESPELHO):
        with open(destino, 'w', encoding='utf-8') as f:
            json.dump(m, f, ensure_ascii=False, indent=2)


def itens(playlist):
    saida, tok = [], ''
    while True:
        p = {'part': 'snippet', 'playlistId': playlist, 'maxResults': 50}
        if tok:
            p['pageToken'] = tok
        d = yt.call('GET', 'playlistItems', p)
        saida += [(i['id'], i['snippet']['position'],
                   i['snippet']['resourceId']['videoId'], i['snippet']['title'])
                  for i in d['items']]
        tok = d.get('nextPageToken')
        if not tok:
            return saida


def posicao_de(m, numero):
    """Onde a aula entra: depois de toda aula de número menor que já está lá."""
    presentes = sorted(a['numero'] for a in m['aulas']
                       if a['numero'] != numero and a.get('video_id_na_playlist'))
    return sum(1 for n in presentes if n < numero)


def sobe(caminho, aula):
    corpo = {
        'snippet': {
            'title': aula['titulo'],
            'description': aula['descricao'],
            'tags': aula['tags'],
            'categoryId': aula.get('categoria', '27'),
            'defaultLanguage': 'pt-BR',
            'defaultAudioLanguage': 'pt-BR',
        },
        'status': {'privacyStatus': 'unlisted', 'selfDeclaredMadeForKids': False},
    }
    tam = os.path.getsize(caminho)
    cab = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Upload-Content-Length': str(tam),
        'X-Upload-Content-Type': 'video/mp4',
    }

    def abre():
        cab['Authorization'] = 'Bearer ' + json.load(open(yt.TOK))['access_token']
        return urllib.request.urlopen(urllib.request.Request(
            'https://www.googleapis.com/upload/youtube/v3/videos'
            '?uploadType=resumable&part=snippet,status',
            data=json.dumps(corpo).encode(), headers=cab, method='POST'))

    try:
        r = abre()
    except urllib.error.HTTPError as e:
        if e.code != 401:
            raise
        yt.refresh()
        r = abre()

    with open(caminho, 'rb') as f:
        v = json.load(urllib.request.urlopen(urllib.request.Request(
            r.headers['Location'], data=f.read(),
            headers={'Content-Type': 'video/mp4', 'Content-Length': str(tam)},
            method='PUT')))
    # a API às vezes ignora as tags do corpo inicial; reaplica
    yt.call('PUT', 'videos', {'part': 'snippet'}, {'id': v['id'], 'snippet': corpo['snippet']})
    return v['id']


def tira(m, vid, era_nosso):
    """Tira um vídeo da playlist. Se foi este script que o publicou, deixa privado."""
    pl = m['playlists']['basica']
    for item_id, _, v, _ in itens(pl):
        if v == vid:
            yt.call('DELETE', 'playlistItems', {'id': item_id})
            print('tirou da playlist', vid)
    if era_nosso:
        yt.call('PUT', 'videos', {'part': 'status'},
                {'id': vid, 'status': {'privacyStatus': 'private'}})
        print('vídeo antigo virou privado (não foi apagado)')
    else:
        print('vídeo antigo é do canal, não foi tocado')


def sincroniza():
    """Deixa a playlist igual ao manifesto: tira o que sobrou, põe na ordem certa.

    Não sobe nada. Serve para terminar uma troca que a rede interrompeu.
    """
    m = carrega()
    pl = m['playlists']['basica']
    quer = {a['video_id_na_playlist']: a for a in m['aulas'] if a.get('video_id_na_playlist')}

    for item_id, _, vid, titulo in itens(pl):
        if vid not in quer:
            yt.call('DELETE', 'playlistItems', {'id': item_id})
            print('sobrando, tirei:', vid, '|', titulo[:50])

    ordem = [a['video_id_na_playlist'] for a in sorted(m['aulas'], key=lambda a: a['numero'])
             if a.get('video_id_na_playlist')]
    for alvo, vid in enumerate(ordem):
        for item_id, pos, v, _ in itens(pl):
            if v == vid and pos != alvo:
                yt.call('PUT', 'playlistItems', {'part': 'snippet'}, {
                    'id': item_id,
                    'snippet': {'playlistId': pl, 'position': alvo,
                                'resourceId': {'kind': 'youtube#video', 'videoId': vid}}})
                print('movi', vid, 'de', pos, 'para', alvo)
    estado()


def estado():
    m = carrega()
    pl = m['playlists']['basica']
    atuais = {vid: (pos, tit) for _, pos, vid, tit in itens(pl)}
    print('playlist básica %s — %d vídeos\n' % (pl, len(atuais)))
    for a in sorted(m['aulas'], key=lambda a: a['numero']):
        vid = a.get('video_id_na_playlist') or a.get('video_id')
        marca = 'pos %d' % atuais[vid][0] if vid in atuais else '  —  '
        print('%2d  %-7s %-12s %-11s %s' % (a['numero'], marca, a['status'],
                                            vid or '', a['titulo_curto']))


def troca(numero, caminho):
    m = carrega()
    aula = next((a for a in m['aulas'] if a['numero'] == numero), None)
    if aula is None:
        sys.exit('aula %d não está no manifesto' % numero)
    if not os.path.isfile(caminho):
        sys.exit('arquivo não encontrado: %s' % caminho)

    pl = m['playlists']['basica']
    antigo = aula.get('video_id_na_playlist')
    nosso = aula.get('publicado_por_este_script', False)

    novo = sobe(caminho, aula)
    print('subiu', novo, '· não listado')

    pos = posicao_de(m, numero)
    yt.call('POST', 'playlistItems', {'part': 'snippet'}, {
        'snippet': {'playlistId': pl, 'position': pos,
                    'resourceId': {'kind': 'youtube#video', 'videoId': novo}}})
    print('entrou na posição', pos)

    # o manifesto é gravado ANTES da limpeza: se a rede cair no meio,
    # `--sincroniza` termina o serviço sem subir nada de novo.
    aula['video_id_na_playlist'] = novo
    aula['video_id'] = novo
    aula['publicado_por_este_script'] = True
    aula['status'] = 'publicado'
    aula['substituiu'] = antigo
    salva(m)
    print('manifesto atualizado')

    if antigo:
        tira(m, antigo, nosso)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--estado':
        estado()
    elif len(sys.argv) == 2 and sys.argv[1] == '--sincroniza':
        sincroniza()
    elif len(sys.argv) == 3:
        troca(int(sys.argv[1]), os.path.expanduser(sys.argv[2]))
    else:
        sys.exit(__doc__)
