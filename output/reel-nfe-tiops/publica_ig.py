#!/usr/bin/env python3
"""Publica um Reel no @tiopstecnologia (mesmo caminho da fila-imersao).

  python3 publica_ig.py <video.mp4> <legenda.md> <capa_ms> <saida.json>

A legenda é o texto de legenda.md entre o título (# ...) e a linha "---";
depois da linha "---", o bloco "Primeiro comentário" vira o comentário fixado logo após publicar.
"""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.expanduser('~/.claude/skills/instagram-graph-publisher/scripts'))
import requests
from instagram_publish import load_config, upload_to_s3, publish, API_VERSION

BUCKET = 'tiops-public-assets-1785392019'


def textos(md):
    corpo, _, resto = open(md).read().partition('\n---\n')
    legenda = '\n'.join(l for l in corpo.splitlines() if not l.startswith('# ')).strip()
    com = []
    for bloco in resto.strip().split('\n\n'):
        linhas = bloco.splitlines()
        if linhas and linhas[0].lower().startswith('primeiro comentário'):
            com = linhas[1:]
    return legenda, '\n'.join(com).strip()


def main(video, md, capa_ms, saida):
    legenda, comentario = textos(md)
    assert len(legenda) <= 2200 and legenda.count('#') <= 30
    ig, token = load_config('tiopstecnologia')
    base = 'https://graph.facebook.com/%s/%s' % (API_VERSION, ig)
    url = upload_to_s3(video, BUCKET, prefix='temp/cortes')
    try:
        r = requests.post(base + '/media', data={
            'access_token': token, 'media_type': 'REELS', 'video_url': url, 'caption': legenda,
            'share_to_feed': 'true', 'thumb_offset': str(capa_ms)}).json()
        if 'id' not in r:
            raise RuntimeError('container recusado: %s' % r)
        for _ in range(60):
            time.sleep(5)
            s = requests.get('https://graph.facebook.com/%s/%s' % (API_VERSION, r['id']),
                             params={'fields': 'status_code,status', 'access_token': token}).json()
            if s.get('status_code') == 'FINISHED':
                break
            if s.get('status_code') == 'ERROR':
                raise RuntimeError('processamento falhou: %s' % s)
        else:
            raise RuntimeError('Instagram não processou em 5 min')
        mid = publish(base, token, r['id'])
        link = requests.get('https://graph.facebook.com/%s/%s' % (API_VERSION, mid),
                            params={'fields': 'permalink,timestamp', 'access_token': token}).json()
        res = {'id': mid, 'url': link.get('permalink'), 'quando': link.get('timestamp')}
        if comentario:
            c = requests.post('https://graph.facebook.com/%s/%s/comments' % (API_VERSION, mid),
                              data={'message': comentario, 'access_token': token}).json()
            res['comentario'] = c.get('id')
        json.dump(res, open(saida, 'w'), indent=1, ensure_ascii=False)
        print(res)
    finally:
        subprocess.run(['aws', 's3', 'rm', 's3://%s/temp/cortes/%s' % (BUCKET, os.path.basename(video)),
                        '--region', 'us-east-1'], check=False)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
