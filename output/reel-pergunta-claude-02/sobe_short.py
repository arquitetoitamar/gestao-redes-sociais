"""Sobe o Reel #2 como Short no YouTube (público agora, ou privado agendado).
uso: python3 sobe_short.py [AAAA-MM-DDTHH:MM]"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt
AQUI = os.path.dirname(os.path.abspath(__file__))
TITULO = 'Reposição do Full no Mercado Livre em 4 passos (e com IA) #shorts'
DESC = """Seu produto acabou no Full e o anúncio caiu? Reposição do Full em 4 passos:
1. Venda por dia dos últimos 10 dias.
2. Multiplica por 30: é o que precisa estar no Full.
3. Desconta o que já está lá e o que está a caminho.
4. Começa pelo produto que está subindo.

Com o Marketplace Connect, o Claude ou o ChatGPT lê vendas e estoque do seu Mercado Livre e devolve a lista de envio pronta. Nada muda na loja sem o seu OK.

Saiba mais: https://l.tiops.com.br/comece?o=youtube-shorts
No Instagram, comenta CONNECT no @tiopstecnologia que eu te mando o link.

(valores de exemplo)
#mercadolivre #mercadolivrefull #ia"""
TAGS = ['reposicao full', 'mercado livre full', 'estoque full mercado livre', 'mercado livre', 'claude', 'chatgpt',
        'marketplace connect', 'ia para ecommerce', 'vender no mercado livre']
quando = sys.argv[1] if len(sys.argv) > 1 else None
arq = os.path.join(AQUI, 'videos', 'reel_pergunta_claude_02.mp4')
assert len(TITULO) <= 100 and '<' not in DESC and '>' not in DESC and sum(len(t) + (2 if ' ' in t else 0) + 1 for t in TAGS) < 480
corpo = {'snippet': {'title': TITULO, 'description': DESC, 'tags': TAGS, 'categoryId': '28',
                     'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
         'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}}
if quando:
    corpo['status'].update(privacyStatus='private', publishAt=quando + ':00-03:00')
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
print('video', v['id'], v['status'].get('privacyStatus'), v['status'].get('publishAt'), v['status'].get('uploadStatus'))
json.dump({'short': {'id': v['id'], 'url': 'https://youtube.com/shorts/' + v['id'], 'titulo': TITULO, 'publica_em': v['status'].get('publishAt')}},
          open(os.path.join(AQUI, 'publicados.json'), 'w'), indent=1, ensure_ascii=False)
