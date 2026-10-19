#!/usr/bin/env python3
"""Refaz a trilha de Claude com áudio nivelado e capa própria.

Um por vez: baixa do Drive, normaliza para -14 LUFS, sobe não listado, põe a
capa, encaixa na playlist, aposenta a versão antiga e apaga o arquivo local.
"""
import json, os, subprocess, sys, urllib.error, urllib.request

import claude_trilha as ct
import drive, yt

CAPAS = os.path.expanduser('~/midia-tmp/claude/capas')
ALVO_LUFS = -14


def normaliza(entrada, saida):
    """Leva o áudio ao alvo do YouTube. Só nível: nada de denoise, EQ ou música."""
    subprocess.run(['ffmpeg', '-v', 'error', '-i', entrada,
                    '-c:v', 'copy', '-af', 'loudnorm=I=%d:TP=-1.5:LRA=11' % ALVO_LUFS,
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
                    saida, '-y'], check=True)


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


def capa(video_id, arquivo):
    dados = open(arquivo, 'rb').read()
    req = urllib.request.Request(
        'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + video_id,
        data=dados, method='POST',
        headers={'Authorization': 'Bearer ' + json.load(open(yt.TOK))['access_token'],
                 'Content-Type': 'image/png', 'Content-Length': str(len(dados))})
    urllib.request.urlopen(req)


def main():
    e = ct.estado()
    pl = e['playlist']
    link = 'https://www.youtube.com/playlist?list=' + pl
    mapa = ct.arquivos_do_drive()
    os.makedirs(ct.AREA, exist_ok=True)

    for nome, n, curto, tags in ct.PLANO:
        reg = e.setdefault(nome, {})
        if reg.get('nivelado'):
            print('  pronto   %02d  %s' % (n, reg['video_id']))
            continue

        bruto = os.path.join(ct.AREA, 'bruto_%02d' % n)
        tratado = os.path.join(ct.AREA, 'ok_%02d.mp4' % n)
        if not os.path.exists(bruto):
            f = mapa[ct._chave(nome)]
            print('  baixando %02d  %.0f MB' % (n, int(f.get('size', 0)) / 1e6))
            drive.baixar(f['id'], bruto)
        print('  nivelando %02d' % n)
        normaliza(bruto, tratado)
        os.remove(bruto)

        antigo = reg.get('video_id')
        vid = sobe(tratado, ct.titulo(n, curto),
                   ct.descricao(n, curto, link), ['claude', 'treinamento'] + tags)
        try:
            capa(vid, os.path.join(CAPAS, 'capa_%02d.png' % n))
            print('           capa posta')
        except Exception as ex:
            print('           capa falhou:', ex)
        yt.call('POST', 'playlistItems', {'part': 'snippet'}, {
            'snippet': {'playlistId': pl, 'position': n - 1,
                        'resourceId': {'kind': 'youtube#video', 'videoId': vid}}})
        reg.update({'video_id': vid, 'numero': n, 'titulo': ct.titulo(n, curto),
                    'nivelado': True, 'substituiu': antigo})
        ct.salva(e)
        print('  subiu    %02d  %s' % (n, vid))

        if antigo:
            for it in yt.call('GET', 'playlistItems',
                              {'part': 'snippet', 'playlistId': pl,
                               'maxResults': 50})['items']:
                if it['snippet']['resourceId']['videoId'] == antigo:
                    yt.call('DELETE', 'playlistItems', {'id': it['id']})
            yt.call('PUT', 'videos', {'part': 'status'},
                    {'id': antigo, 'status': {'privacyStatus': 'private'}})
            print('           antigo %s virou privado' % antigo)

        os.remove(tratado)

    print('\nplaylist:', link)


if __name__ == '__main__':
    main()
