"""Sobe o Reel Chatiops + Claude como Short (privado com publishAt). uso: python3 sobe_short.py AAAA-MM-DDTHH:MM"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt
AQUI = os.path.dirname(os.path.abspath(__file__))
TITULO = 'O Claude agora monta o atendimento do seu WhatsApp (Chatiops + MCP) #shorts'
leg = open(os.path.join(AQUI, 'legenda_ig.md'), encoding='utf-8').read().split('\n', 2)[2].strip()
DESC = leg.replace('💬 Comenta WHATSAPP que eu te mando o link e o passo a passo no direct.',
                   'Teste 90 dias grátis: https://l.tiops.com.br/chatiops-90dias?o=youtube-shorts\n'
                   'Como conectar no Claude: https://l.tiops.com.br/chatiops-mcp?o=youtube-shorts\n'
                   'No Instagram, comenta WHATSAPP no @tiopstecnologia que eu te mando o passo a passo.')
TAGS = ['whatsapp com ia', 'atendimento whatsapp', 'claude', 'mcp', 'chatiops', 'chatbot whatsapp', 'ia para atendimento', 'automacao whatsapp']
quando = sys.argv[1]
arq = os.path.join(AQUI, 'videos', 'reel_chatiops_claude.mp4')
assert len(TITULO) <= 100 and '<' not in DESC and '>' not in DESC
corpo = {'snippet': {'title': TITULO, 'description': DESC, 'tags': TAGS, 'categoryId': '28', 'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
         'status': {'privacyStatus': 'private', 'publishAt': quando + ':00-03:00', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}
tok = yt.refresh(); tam = os.path.getsize(arq)
req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                             data=json.dumps(corpo).encode(), method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                      'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam)})
loc = urllib.request.urlopen(req).headers['Location']
with open(arq, 'rb') as f:
    up = urllib.request.Request(loc, data=f.read(), method='PUT',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4', 'Content-Length': str(tam)})
    v = json.load(urllib.request.urlopen(up, timeout=1800))
print('short', v['id'], v['status'].get('privacyStatus'), v['status'].get('publishAt'))
json.dump({'ig_agendamento': 'ig-reel-chatiops-claude-20261126', 'ig_quando': '2026-11-26 16:00 BRT',
           'short': {'id': v['id'], 'url': 'https://youtube.com/shorts/' + v['id'], 'publica_em': v['status'].get('publishAt')}},
          open(os.path.join(AQUI, 'publicado.json'), 'w'), indent=1, ensure_ascii=False)
