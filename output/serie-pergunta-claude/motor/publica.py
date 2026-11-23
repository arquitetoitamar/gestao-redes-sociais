"""Agenda um episódio pronto: Reel no Instagram @tiopstecnologia (EventBridge -> Lambda) e Short no YouTube (privado com publishAt),
os dois no mesmo horário (data/hora do episódio, horário de Brasília).
uso: python3 motor/publica.py episodios/03-fotos.json
Grava ep-NN-slug/publicado.json com o id do agendamento, a URL de prévia (S3, vale até a publicação) e o id do Short."""
import json, os, subprocess, sys, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.abspath(os.path.join(RAIZ, '../..'))
sys.path.insert(0, os.path.join(REPO, 'scripts/trilha'))
BUCKET = 'tiops-public-assets-1785392019'

ep = json.load(open(sys.argv[1], encoding='utf-8'))
pasta = os.path.join(RAIZ, 'ep-%02d-%s' % (ep['num'], ep['slug']))
video = os.path.join(pasta, 'videos', 'ep-%02d.mp4' % ep['num'])
leg = os.path.join(pasta, 'legenda_ig.md')
assert os.path.exists(video) and os.path.exists(leg), 'gere o episódio antes (motor/gera.py)'
quando = '%s %s' % (ep['data'], ep.get('hora', '18:00'))
pid = 'serie-pc-%02d-%s' % (ep['num'], ep['data'].replace('-', ''))

# 1) Instagram (agendador da AWS; não depende do Mac na hora)
r = subprocess.run([sys.executable, os.path.join(REPO, 'scripts/ig-agendado/agenda.py'), 'agenda', pid, 'reel', video, leg, quando, '1500'],
                   capture_output=True, text=True)
print(r.stdout[-400:], r.stderr[-300:] if r.returncode else '')
if r.returncode != 0 or 'agendado:' not in r.stdout:
    sys.exit('falhou o agendamento do Instagram')

# 2) YouTube Short (privado, publica sozinho no mesmo horário)
import yt
legenda = ep['legenda_ig'].strip()
corpo_desc = legenda.replace('💬 Comenta CONNECT que eu te mando o link no direct.',
                             'Saiba mais: https://l.tiops.com.br/comece?o=youtube-shorts\nNo Instagram, comenta CONNECT no @tiopstecnologia que eu te mando o link.')
corpo_desc = corpo_desc.replace('<', '').replace('>', '')
s = ep.get('short', {})
titulo = s.get('titulo') or (ep['slug'].replace('-', ' ').capitalize() + ' #shorts')
assert len(titulo) <= 100
corpo = {'snippet': {'title': titulo, 'description': corpo_desc[:4900], 'tags': s.get('tags', ['mercado livre', 'marketplace connect', 'claude', 'chatgpt']),
                     'categoryId': '28', 'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
         'status': {'privacyStatus': 'private', 'publishAt': '%sT%s:00-03:00' % (ep['data'], ep.get('hora', '18:00')),
                    'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}
tok = yt.refresh(); tam = os.path.getsize(video)
req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                             data=json.dumps(corpo).encode(), method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                      'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam)})
loc = urllib.request.urlopen(req).headers['Location']
with open(video, 'rb') as f:
    up = urllib.request.Request(loc, data=f.read(), method='PUT',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4', 'Content-Length': str(tam)})
    v = json.load(urllib.request.urlopen(up, timeout=1800))
print('short', v['id'], v['status'].get('privacyStatus'), v['status'].get('publishAt'))

reg = {'ig_agendamento': 'ig-' + pid, 'ig_quando': quando + ' BRT',
       'previa': 'https://%s.s3.amazonaws.com/temp/agendados/%s.mp4' % (BUCKET, pid),
       'short': {'id': v['id'], 'url': 'https://youtube.com/shorts/' + v['id'], 'publica_em': v['status'].get('publishAt')},
       'cancelar': 'python3 scripts/ig-agendado/agenda.py cancela %s  +  apagar o Short %s no YouTube Studio' % (pid, v['id'])}
json.dump(reg, open(os.path.join(pasta, 'publicado.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(reg, ensure_ascii=False, indent=1))
