#!/usr/bin/env python3
"""Publica o vídeo de bastidores da Imersão (24/10) como Reel e como Short.

Sem flag só imprime o plano. `--ig` publica o Reel em @tiopstecnologia,
`--yt` sobe o Short no canal Itamar Rocha (público na hora, ou agendado
com `--yt-em "2026-10-28 12:00"` em horário de Brasília).

O vídeo vai como foi editado, sem recodificar. A capa do Reel é o quadro
de 9,5 s (Itamar na frente do telão da Imersão), via `thumb_offset`.
O que for publicado fica em `publicado.json`.
"""
import argparse, datetime, json, os, subprocess, sys, time, urllib.error, urllib.request

import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.join(AQUI, 'imersao-bastidores-24out.mov')
SAIDA = os.path.join(AQUI, 'publicado.json')
CAPA_MS = 9500

sys.path.insert(0, os.path.expanduser('~/.claude/skills/instagram-graph-publisher/scripts'))
sys.path.insert(0, os.path.expanduser('~/git/gestao-redes-sociais/scripts/trilha'))

LEGENDA_IG = """Foi assim a primeira Imersão IA para Marketplaces 🤖

Sábado, 24/10, em São Paulo: um dia inteiro com sellers de notebook aberto, montando agentes de IA para a própria operação. IA que sai da conversa e entra na operação.

Obrigado a todo mundo que veio. Quer ir na próxima? Comenta IMERSÃO que eu te aviso quando abrir."""

HASHTAGS_IG = ('#inteligenciaartificial #marketplaces #ecommerce #agentesdeia '
               '#sellers #mercadolivre #shopee #tiops #eventosp')

TITULO_YT = 'Como foi a Imersão IA para Marketplaces 🤖'

DESC_YT = """Bastidores da primeira Imersão IA para Marketplaces da Tiops, sábado, 24/10, em São Paulo: um dia inteiro com sellers montando agentes de IA para a própria operação.

Quer ir na próxima? Comenta aqui que eu aviso quando abrir.

#Shorts #InteligenciaArtificial #Marketplaces #Ecommerce"""

TAGS_YT = ['imersão ia', 'ia para marketplaces', 'agentes de ia',
           'inteligência artificial', 'ecommerce', 'mercado livre', 'shopee',
           'sellers', 'tiops', 'evento sp']


def confere():
    """Limites que já quebraram upload antes (ver memória do YouTube)."""
    tags = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS_YT) + len(TAGS_YT) - 1
    assert tags <= 500, 'tags com %d caracteres' % tags
    assert len(TITULO_YT) <= 100
    assert '<' not in DESC_YT and '>' not in DESC_YT
    assert len(LEGENDA_IG) <= 2200
    return tags


def registra(chave, dado):
    feito = json.load(open(SAIDA)) if os.path.exists(SAIDA) else {}
    feito[chave] = dado
    json.dump(feito, open(SAIDA, 'w'), indent=1, ensure_ascii=False)


def instagram():
    from instagram_publish import load_config, upload_to_s3, publish, API_VERSION
    ig, token = load_config('tiopstecnologia')
    base = 'https://graph.facebook.com/%s/%s' % (API_VERSION, ig)
    url = upload_to_s3(VIDEO, 'tiops-public-assets-1785392019')
    r = requests.post(base + '/media', data={
        'access_token': token, 'media_type': 'REELS', 'video_url': url,
        'caption': LEGENDA_IG, 'share_to_feed': 'true',
        'thumb_offset': str(CAPA_MS)}).json()
    if 'id' not in r:
        sys.exit('container recusado: %s' % r)
    cid = r['id']
    for _ in range(60):  # HEVC às vezes passa de 1 min
        time.sleep(5)
        st = requests.get('https://graph.facebook.com/%s/%s' % (API_VERSION, cid),
                          params={'fields': 'status_code,status', 'access_token': token}).json()
        if st.get('status_code') == 'FINISHED':
            break
        if st.get('status_code') == 'ERROR':
            sys.exit('processamento falhou: %s' % st)
    else:
        sys.exit('Instagram não terminou de processar em 5 min')
    mid = publish(base, token, cid)
    link = requests.get('https://graph.facebook.com/%s/%s' % (API_VERSION, mid),
                        params={'fields': 'permalink', 'access_token': token}).json().get('permalink')
    requests.post('https://graph.facebook.com/%s/%s/comments' % (API_VERSION, mid),
                  data={'message': HASHTAGS_IG, 'access_token': token})
    registra('instagram', {'id': mid, 'url': link,
                           'em': datetime.datetime.now().isoformat(timespec='seconds')})
    print('Reel publicado:', link)


def youtube(publica_em=None):
    import yt
    yt.refresh()
    tam = os.path.getsize(VIDEO)
    status = {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
    if publica_em:
        status = {'privacyStatus': 'private', 'publishAt': publica_em,
                  'selfDeclaredMadeForKids': False}
    corpo = {'snippet': {'title': TITULO_YT, 'description': DESC_YT, 'tags': TAGS_YT,
                         'categoryId': '28', 'defaultLanguage': 'pt-BR',
                         'defaultAudioLanguage': 'pt-BR'},
             'status': status}
    req = urllib.request.Request(
        'https://www.googleapis.com/upload/youtube/v3/videos'
        '?uploadType=resumable&part=snippet,status',
        data=json.dumps(corpo).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + yt._tok()['access_token'],
                 'Content-Type': 'application/json; charset=UTF-8',
                 'X-Upload-Content-Length': str(tam),
                 'X-Upload-Content-Type': 'video/quicktime'})
    sessao = urllib.request.urlopen(req).headers['Location']
    with open(VIDEO, 'rb') as f:
        req = urllib.request.Request(sessao, data=f, method='PUT',
                                     headers={'Content-Length': str(tam)})
        d = json.loads(urllib.request.urlopen(req).read())
    link = 'https://youtube.com/shorts/' + d['id']
    registra('youtube', {'id': d['id'], 'url': link, 'publicaEm': publica_em or 'agora',
                         'em': datetime.datetime.now().isoformat(timespec='seconds')})
    print('Short enviado:', link, '(agendado %s)' % publica_em if publica_em else '')


def utc(brt):
    d = datetime.datetime.strptime(brt, '%Y-%m-%d %H:%M')
    return (d + datetime.timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M:%SZ')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--ig', action='store_true')
    p.add_argument('--yt', action='store_true')
    p.add_argument('--yt-em', help='agenda o Short: "AAAA-MM-DD HH:MM" em Brasília')
    a = p.parse_args()
    n = confere()
    if not (a.ig or a.yt):
        print('PLANO (nada publicado)')
        print('vídeo:', VIDEO, '%.1f MB' % (os.path.getsize(VIDEO) / 1e6))
        print('\n--- Reel @tiopstecnologia (capa em %.1f s)\n%s\n\n1º comentário: %s'
              % (CAPA_MS / 1000, LEGENDA_IG, HASHTAGS_IG))
        print('\n--- Short canal Itamar Rocha\ntítulo: %s\n\n%s\n\ntags (%d/500): %s'
              % (TITULO_YT, DESC_YT, n, ', '.join(TAGS_YT)))
        sys.exit()
    if a.ig:
        instagram()
    if a.yt:
        youtube(utc(a.yt_em) if a.yt_em else None)
