#!/usr/bin/env python3
"""Sobe a trilha de Claude: um vídeo por vez, apagando o arquivo após confirmar.

    python3 subir_claude.py            sobe tudo que ainda falta
    python3 subir_claude.py --estado   mostra o que já está no ar
"""
import json, os, sys, urllib.error, urllib.request

import claude_trilha as ct
import yt

PLAYLIST_CLAUDE = None   # criada na primeira execução e guardada no estado
PL_CONNECT = 'PLW3upCIZHed4'


def garante_playlist(e):
    if e.get('playlist'):
        return e['playlist']
    r = yt.call('POST', 'playlists', {'part': 'snippet,status'}, {
        'snippet': {'title': 'Claude — Treinamento',
                    'description': ('Formação geral no Claude: conversa, trabalho em conjunto, '
                                    'skills e conectores. É treinamento da ferramenta, separado '
                                    'da trilha do Marketplace Connect.\n\n'
                                    'Trilha do Marketplace Connect: '
                                    'https://www.youtube.com/playlist?list=' + PL_CONNECT),
                    'defaultLanguage': 'pt-BR'},
        'status': {'privacyStatus': 'unlisted'}})
    e['playlist'] = r['id']
    ct.salva(e)
    print('playlist criada:', r['id'])
    return r['id']


def sobe(caminho, titulo, descricao, tags):
    corpo = {'snippet': {'title': titulo, 'description': descricao, 'tags': tags,
                         'categoryId': '27', 'defaultLanguage': 'pt-BR',
                         'defaultAudioLanguage': 'pt-BR'},
             'status': {'privacyStatus': 'unlisted', 'selfDeclaredMadeForKids': False}}
    tam = os.path.getsize(caminho)
    cab = {'Content-Type': 'application/json; charset=UTF-8',
           'X-Upload-Content-Length': str(tam), 'X-Upload-Content-Type': 'video/*'}

    def abre():
        cab['Authorization'] = 'Bearer ' + json.load(open(yt.TOK))['access_token']
        return urllib.request.urlopen(urllib.request.Request(
            'https://www.googleapis.com/upload/youtube/v3/videos'
            '?uploadType=resumable&part=snippet,status',
            data=json.dumps(corpo).encode(), headers=cab, method='POST'))
    try:
        r = abre()
    except urllib.error.HTTPError as ex:
        if ex.code != 401:
            raise
        yt.refresh()
        r = abre()
    with open(caminho, 'rb') as f:
        v = json.load(urllib.request.urlopen(urllib.request.Request(
            r.headers['Location'], data=f.read(),
            headers={'Content-Type': 'video/*', 'Content-Length': str(tam)}, method='PUT')))
    yt.call('PUT', 'videos', {'part': 'snippet'}, {'id': v['id'], 'snippet': corpo['snippet']})
    return v['id']


def main():
    e = ct.estado()
    pl = garante_playlist(e)
    link = 'https://www.youtube.com/playlist?list=' + pl

    for nome, n, curto, tags in ct.PLANO:
        reg = e.setdefault(nome, {})
        if reg.get('video_id'):
            print('  no ar    %02d  %s' % (n, reg['video_id']))
            continue
        caminho = os.path.join(ct.AREA, '%02d_%s' % (n, nome))
        if not os.path.exists(caminho):
            print('  sem arquivo %02d  %s' % (n, nome))
            continue

        vid = sobe(caminho, ct.titulo(n, curto),
                   ct.descricao(n, curto, link), ['claude', 'treinamento'] + tags)
        yt.call('POST', 'playlistItems', {'part': 'snippet'}, {
            'snippet': {'playlistId': pl, 'position': n - 1,
                        'resourceId': {'kind': 'youtube#video', 'videoId': vid}}})
        reg.update({'video_id': vid, 'numero': n, 'titulo': ct.titulo(n, curto)})
        ct.salva(e)
        print('  subiu    %02d  %s  %s' % (n, vid, ct.titulo(n, curto)))

        # só apaga depois do id em mãos e do item na playlist
        os.remove(caminho)
        print('           apagado o local (%.0f MB liberados)' % (os.path.getsize(caminho) / 1e6
                                                                  if os.path.exists(caminho) else 0))

    print('\nplaylist:', link)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--estado':
        e = ct.estado()
        for nome, n, curto, _ in ct.PLANO:
            r = e.get(nome, {})
            print('%02d %-12s %s' % (n, r.get('video_id') or '—', ct.titulo(n, curto)))
        print('\nplaylist:', e.get('playlist') or '—')
    else:
        main()
