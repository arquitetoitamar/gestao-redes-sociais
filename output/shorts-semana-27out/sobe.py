#!/usr/bin/env python3
"""Agenda os Shorts da semana no YouTube.

Cada vídeo sobe como `private` com `publishAt`: o YouTube guarda e torna
público sozinho na hora marcada. Horários da agenda são de Brasília
(UTC-3), convertidos aqui.

Upload em blocos de 8 MB com retomada — um PUT único já estourou em
broken pipe neste canal. O que já subiu fica em `.agendados.json`, então
rodar de novo não duplica nada.
"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.expanduser('~/git/gestao-redes-sociais/scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from agenda import AGENDA, confere

BLOCO = 8 * 1024 * 1024          # múltiplo de 256 KB, exigência do protocolo
FEITO = os.path.join(AQUI, '.agendados.json')
BRT = 3                          # Brasília está 3 h atrás do UTC


def feitos():
    return json.load(open(FEITO)) if os.path.exists(FEITO) else {}


def quando(dia, hora):
    """'2026-10-27' + '08:00' em Brasília -> instante UTC em RFC3339."""
    import datetime
    h, m = (int(x) for x in hora.split(':'))
    d = datetime.datetime.strptime(dia, '%Y-%m-%d').replace(hour=h, minute=m)
    return (d + datetime.timedelta(hours=BRT)).strftime('%Y-%m-%dT%H:%M:%SZ')


def abre_sessao(arq, titulo, desc, tags, publica_em):
    yt.refresh()
    tam = os.path.getsize(arq)
    corpo = {
        'snippet': {'title': titulo, 'description': desc, 'tags': tags,
                    'categoryId': '28', 'defaultLanguage': 'pt-BR',
                    'defaultAudioLanguage': 'pt-BR'},
        # privacyStatus TEM de ser private: com qualquer outro o YouTube
        # ignora o publishAt e solta o vídeo na hora.
        'status': {'privacyStatus': 'private', 'publishAt': publica_em,
                   'selfDeclaredMadeForKids': False},
    }
    req = urllib.request.Request(
        'https://www.googleapis.com/upload/youtube/v3/videos'
        '?uploadType=resumable&part=snippet,status',
        data=json.dumps(corpo).encode(),
        headers={'Authorization': 'Bearer ' + yt._tok()['access_token'],
                 'Content-Type': 'application/json; charset=UTF-8',
                 'X-Upload-Content-Length': str(tam),
                 'X-Upload-Content-Type': 'video/mp4'},
        method='POST')
    return urllib.request.urlopen(req).headers['Location'], tam


def envia(url, arq, tam):
    enviado = 0
    with open(arq, 'rb') as f:
        while enviado < tam:
            f.seek(enviado)
            pedaco = f.read(BLOCO)
            fim = enviado + len(pedaco) - 1
            req = urllib.request.Request(
                url, data=pedaco, method='PUT',
                headers={'Content-Length': str(len(pedaco)),
                         'Content-Range': 'bytes %d-%d/%d' % (enviado, fim, tam)})
            try:
                return json.loads(urllib.request.urlopen(req).read())
            except urllib.error.HTTPError as e:
                if e.code != 308:
                    raise
                faixa = e.headers.get('Range')
                enviado = int(faixa.split('-')[1]) + 1 if faixa else fim + 1
    raise RuntimeError('acabou o arquivo sem o YouTube fechar o vídeo')


def main():
    confere()
    pronto = feitos()
    for dia, hora, arq, titulo, desc, tags in AGENDA:
        chave = '%s %s' % (dia, hora)
        if chave in pronto:
            print('ja agendado  %s  %s' % (chave, pronto[chave]['id']))
            continue
        publica_em = quando(dia, hora)
        url, tam = abre_sessao(arq, titulo, desc, tags, publica_em)
        d = envia(url, arq, tam)
        pronto[chave] = {'id': d['id'], 'titulo': titulo,
                         'publicaEm': publica_em,
                         'url': 'https://youtube.com/shorts/' + d['id']}
        json.dump(pronto, open(FEITO, 'w'), indent=1, ensure_ascii=False)
        print('%s  %s  %s' % (chave, d['id'], titulo))
    return pronto


if __name__ == '__main__':
    main()
