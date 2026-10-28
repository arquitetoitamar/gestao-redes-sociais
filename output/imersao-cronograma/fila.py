#!/usr/bin/env python3
"""Fila de publicação da Imersão IA para Marketplaces (28/10 a 01/11/2026).

Uma peça por dia, Reel no @tiopstecnologia e Short no canal Itamar Rocha.

  python3 fila.py plano   mostra o calendário e os textos (não publica nada)
  python3 fila.py yt      sobe os Shorts como privados com publishAt (o YouTube
                          solta sozinho na hora, mesmo com o Mac desligado)
  python3 fila.py roda    publica os Reels que já passaram da hora e ainda não
                          saíram. É o que o launchd chama a cada 10 min
                          (com.tiops.fila-imersao); quando a fila acaba, ele se
                          remove sozinho.

O Instagram não tem agendamento pela API, por isso o Reel depende do Mac
ligado: se estiver dormindo na hora, sai quando acordar.
Estado em publicado.json (commitado), log em trab/fila.log.
"""
import datetime, json, os, subprocess, sys, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(AQUI)
ESTADO = os.path.join(AQUI, 'publicado.json')
ROTULO = 'com.tiops.fila-imersao'
sys.path.insert(0, os.path.expanduser('~/.claude/skills/instagram-graph-publisher/scripts'))
sys.path.insert(0, os.path.expanduser('~/git/gestao-redes-sociais/scripts/trilha'))

HASH = ('#inteligenciaartificial #marketplaces #ecommerce #agentesdeia '
        '#sellers #mercadolivre #shopee #tiops')

PECAS = [
    {
        'id': 'depoimento-phellipe',
        'video': os.path.join(OUT, 'reel-depoimento-phellipe', 'depoimento-phellipe.mp4'),
        'ig_em': '2026-10-28 19:00', 'yt_em': '2026-10-28 12:00', 'capa_ms': 40200,
        'legenda': """Ele achou meu vídeo quando tinha 24 visualizações. 🎥

O Phellipe é fabricante, vende em marketplace há anos e achava que a IA ia dominar a gente. Viu um vídeo meu, me ligou e fez a consultoria. Na primeira reunião, as contas dele já estavam conectadas.

No sábado ele contou essa história na Imersão IA para Marketplaces, na frente de todo mundo.

Obrigado, Phellipe. É nosso ouro. 🙌""",
        'hashtags': '#depoimento #fabricante ' + HASH,
        'titulo': 'Ele achou meu vídeo com 24 visualizações',
        'descricao': """O Phellipe é fabricante, vende em marketplace há anos e achava que a IA ia dominar a gente. Viu um vídeo meu quando ele tinha 24 visualizações, me ligou e fez a consultoria. Na primeira reunião, as contas dele já estavam conectadas.

Depoimento gravado na Imersão IA para Marketplaces da Tiops, 24/10, em São Paulo.

#Shorts #InteligenciaArtificial #Marketplaces #Ecommerce""",
        'tags': ['depoimento', 'ia para marketplaces', 'inteligência artificial', 'fabricante',
                 'ecommerce', 'mercado livre', 'shopee', 'sellers', 'tiops', 'imersão ia'],
    },
    {
        'id': 'personalizacao-ao-vivo',
        'video': os.path.join(AQUI, 'videos', 'edit-04.mov'),
        'ig_em': '2026-10-29 18:00', 'yt_em': '2026-10-29 12:00', 'capa_ms': 26500,
        'legenda': """Veio tanta gente na Imersão IA para Marketplaces que os brindes acabaram. 😅

A solução foi personalizar na hora: logo da Tiops em DTF têxtil, aplicada ao vivo nas bolsas, por uma hora seguida.

Obrigado, Jorge e equipe da Danzo Brindes, pela parceria! {PARCEIRO}""",
        'hashtags': '#dtftextil #personalizados #brindes ' + HASH,
        'titulo': 'Os brindes acabaram e eles personalizaram na hora',
        'descricao': """Veio tanta gente na Imersão IA para Marketplaces que os brindes acabaram. A solução foi personalizar na hora: logo da Tiops em DTF têxtil, aplicada ao vivo nas bolsas. Obrigado ao Jorge e à equipe da Danzo Brindes pela parceria.

Imersão IA para Marketplaces da Tiops, 24/10, em São Paulo.

#Shorts #DTF #Personalizados #Marketplaces""",
        'tags': ['dtf têxtil', 'personalizados', 'brindes', 'evento', 'ia para marketplaces',
                 'tiops', 'imersão ia', 'ecommerce'],
    },
    {
        'id': 'bastidores-plataforma',
        'video': os.path.join(AQUI, 'videos', 'edit-01.mov'),
        'ig_em': '2026-10-30 18:00', 'yt_em': '2026-10-30 12:00', 'capa_ms': 4100,
        'legenda': """Tiops, plataforma 100% brasileira de IA e automação para quem vende em marketplace. 🇧🇷

Bastidores da primeira Imersão IA para Marketplaces, 24/10, em São Paulo.""",
        'hashtags': HASH,
        'titulo': 'Plataforma 100% brasileira de IA para marketplaces 🇧🇷',
        'descricao': """Bastidores da primeira Imersão IA para Marketplaces da Tiops, 24/10, em São Paulo.

#Shorts #InteligenciaArtificial #Marketplaces""",
        'tags': ['tiops', 'ia para marketplaces', 'inteligência artificial', 'imersão ia',
                 'bastidores', 'ecommerce'],
    },
    {
        'id': 'prova-phellipe',
        'video': os.path.join(AQUI, 'videos', 'prova-phellipe.mp4'),
        'ig_em': '2026-10-31 18:00', 'yt_em': '2026-10-31 12:00', 'capa_ms': 21500,
        'legenda': """"Posso bater palmas?" 👏

Foi o Phellipe que pediu, no meio da Imersão IA para Marketplaces. Fabricante e seller, ele contou que na primeira reunião as contas dele já estavam conectadas, e que o ouro está em juntar empresários com a mesma dor.

A Imersão completa (3 horas) está no YouTube, de graça.
Comenta IMERSÃO que eu te mando o link na DM. 👇""",
        'hashtags': '#depoimento #provasocial ' + HASH,
        'titulo': '"Posso bater palmas?" O que um cliente falou na Imersão',
        'descricao': """A Imersão IA para Marketplaces completa (3 horas, de graça): https://youtu.be/7VVhSzlHfdI

O Phellipe é fabricante e seller. No meio da Imersão, pediu a palavra para agradecer: na primeira reunião da consultoria, as contas dele já estavam conectadas.

#Shorts #InteligenciaArtificial #Marketplaces #Ecommerce""",
        'tags': ['depoimento', 'prova social', 'ia para marketplaces', 'imersão ia',
                 'inteligência artificial', 'ecommerce', 'mercado livre', 'shopee', 'sellers', 'tiops'],
    },
]

PARCEIRO = ''  # @ da Danzo Brindes, quando o Itamar mandar (não achei a conta)


def texto(p):
    return p['legenda'].replace('{PARCEIRO}', PARCEIRO).rstrip()


def utc(brt):
    d = datetime.datetime.strptime(brt, '%Y-%m-%d %H:%M')
    return d + datetime.timedelta(hours=3)


def estado():
    return json.load(open(ESTADO)) if os.path.exists(ESTADO) else {}


def salva(st):
    json.dump(st, open(ESTADO, 'w'), indent=1, ensure_ascii=False)


def log(msg):
    os.makedirs(os.path.join(AQUI, 'trab'), exist_ok=True)
    with open(os.path.join(AQUI, 'trab', 'fila.log'), 'a') as f:
        f.write('%s %s\n' % (datetime.datetime.now().isoformat(timespec='seconds'), msg))
    print(msg)


def confere():
    for p in PECAS:
        n = sum(len(t) + (2 if ' ' in t else 0) for t in p['tags']) + len(p['tags']) - 1
        assert n <= 500 and len(p['titulo']) <= 100, p['id']
        assert '<' not in p['descricao'] and '>' not in p['descricao'], p['id']
        assert len(texto(p)) <= 2200 and os.path.exists(p['video']), p['id']


def reel(p):
    import requests
    from instagram_publish import load_config, upload_to_s3, publish, API_VERSION
    ig, token = load_config('tiopstecnologia')
    base = 'https://graph.facebook.com/%s/%s' % (API_VERSION, ig)
    url = upload_to_s3(p['video'], 'tiops-public-assets-1785392019')
    r = requests.post(base + '/media', data={
        'access_token': token, 'media_type': 'REELS', 'video_url': url, 'caption': texto(p),
        'share_to_feed': 'true', 'thumb_offset': str(p['capa_ms'])}).json()
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
                        params={'fields': 'permalink', 'access_token': token}).json().get('permalink')
    requests.post('https://graph.facebook.com/%s/%s/comments' % (API_VERSION, mid),
                  data={'message': p['hashtags'], 'access_token': token})
    return {'id': mid, 'url': link}


def short(p):
    import yt
    yt.refresh()
    tam = os.path.getsize(p['video'])
    corpo = {'snippet': {'title': p['titulo'], 'description': p['descricao'], 'tags': p['tags'],
                         'categoryId': '28', 'defaultLanguage': 'pt-BR',
                         'defaultAudioLanguage': 'pt-BR'},
             'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False,
                        'publishAt': utc(p['yt_em']).strftime('%Y-%m-%dT%H:%M:%SZ')}}
    tipo = 'video/mp4' if p['video'].endswith('.mp4') else 'video/quicktime'
    req = urllib.request.Request(
        'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
        data=json.dumps(corpo).encode(), method='POST',
        headers={'Authorization': 'Bearer ' + yt._tok()['access_token'],
                 'Content-Type': 'application/json; charset=UTF-8',
                 'X-Upload-Content-Length': str(tam), 'X-Upload-Content-Type': tipo})
    sessao = urllib.request.urlopen(req).headers['Location']
    with open(p['video'], 'rb') as f:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(
            sessao, data=f, method='PUT', headers={'Content-Length': str(tam)})).read())
    return {'id': d['id'], 'url': 'https://youtube.com/shorts/' + d['id'], 'publicaEm': p['yt_em']}


def cmd_plano():
    st = estado()
    for p in PECAS:
        s = st.get(p['id'], {})
        print('\n=== %s  Reel %s %s | Short %s %s' % (
            p['id'], p['ig_em'], '✓' if 'ig' in s else '', p['yt_em'], '✓' if 'yt' in s else ''))
        print(texto(p))
        print('1º comentário:', p['hashtags'])
        print('Short:', p['titulo'])


def cmd_yt():
    st = estado()
    for p in PECAS:
        if 'yt' in st.get(p['id'], {}):
            continue
        st.setdefault(p['id'], {})['yt'] = short(p)
        salva(st)
        log('short agendado %s %s' % (p['id'], st[p['id']]['yt']['url']))


def cmd_roda():
    st = estado()
    agora = datetime.datetime.utcnow()
    for p in PECAS:
        if 'ig' in st.get(p['id'], {}) or utc(p['ig_em']) > agora:
            continue
        try:
            st.setdefault(p['id'], {})['ig'] = dict(reel(p), em=datetime.datetime.now().isoformat(timespec='seconds'))
            salva(st)
            log('reel publicado %s %s' % (p['id'], st[p['id']]['ig']['url']))
            commit('fila-imersao: publica %s' % p['id'])
        except Exception as e:
            log('ERRO %s: %s' % (p['id'], e))
        break  # no máximo um Reel por rodada
    if all('ig' in st.get(p['id'], {}) for p in PECAS):
        log('fila terminou, removendo o agendamento')
        plist = os.path.expanduser('~/Library/LaunchAgents/%s.plist' % ROTULO)
        if os.path.exists(plist):
            os.remove(plist)
        subprocess.run(['launchctl', 'bootout', 'gui/%d/%s' % (os.getuid(), ROTULO)])


def commit(msg):
    repo = os.path.dirname(OUT)
    subprocess.run(['git', '-C', repo, 'add', os.path.relpath(ESTADO, repo)])
    subprocess.run(['git', '-C', repo, 'commit', '-q', '-m',
                    msg + '\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'])
    subprocess.run(['git', '-C', repo, 'push', '-q'])


if __name__ == '__main__':
    confere()
    {'plano': cmd_plano, 'yt': cmd_yt, 'roda': cmd_roda}[sys.argv[1]]()
