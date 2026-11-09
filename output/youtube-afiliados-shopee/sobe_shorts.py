"""Agenda os 3 Shorts do vídeo Afiliado Shopee (publishAt), 48 h entre eles, às 18h de Brasília.
uso: python3 sobe_shorts.py <pasta_com_shortN.mp4> [1 2 3]"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = sys.argv[1]
QUAIS = [int(x) for x in sys.argv[2:]] or [1, 2, 3]
BASE = """Passo a passo completo: https://youtu.be/Mg7mIiimaOw

🔗 Marketplace Connect: https://l.tiops.com.br/shopee-afiliados?o=shorts
🔌 Conector Afiliados Shopee: https://mcp.tiops.com.br/mcp/afiliados

{extra}

{tags}"""
SHORTS = {
    1: dict(quando='2026-11-10T21:00:00Z', ia=False,
            titulo='AFILIADO SHOPEE: a IA acha o produto com MAIOR comissão pra você #afiliadoshopee #shopee #chatgpt',
            extra='O ChatGPT consulta a sua conta de Afiliados Shopee e traz os produtos com maior percentual de comissão. Comissões e ofertas mudam conforme a Shopee.',
            hashtags='#afiliadoshopee #shopeeafiliados #chatgpt #ia'),
    2: dict(quando='2026-11-12T21:00:00Z', ia=False,
            titulo='AFILIADO SHOPEE: link de afiliado em SEGUNDOS com IA no ChatGPT #afiliadoshopee #shopee #ia',
            extra='Peça em português e o ChatGPT gera o seu link de afiliado da Shopee, um por um ou em massa.',
            hashtags='#afiliadoshopee #linkdeafiliado #chatgpt #ia'),
    3: dict(quando='2026-11-14T21:00:00Z', ia=True,
            titulo='AFILIADO SHOPEE: vídeo do produto feito pela IA (Shopee Vídeo) #shopeevideo #afiliadoshopee #ia',
            extra='O ChatGPT gera o vídeo do produto a partir das imagens e da descrição da oferta. O vídeo mostrado foi gerado com IA.',
            hashtags='#shopeevideo #afiliadoshopee #videocomia #ia'),
}
TAGS = ['afiliado shopee', 'shopee afiliados', 'afiliado shopee com ia', 'afiliado shopee passo a passo', 'como vender na shopee',
        'link de afiliado shopee', 'shopee video afiliado', 'video com ia para shopee', 'chatgpt shopee', 'afiliado shopee chatgpt', 'shorts']
res = {}
if os.path.exists(os.path.join(AQUI, 'shorts_publicados.json')):
    res = json.load(open(os.path.join(AQUI, 'shorts_publicados.json')))
tok = yt.refresh()
for n in QUAIS:
    c = SHORTS[n]; arq = os.path.join(PASTA, 'short%d.mp4' % n)
    desc = BASE.format(extra=c['extra'], tags=c['hashtags'])
    assert len(c['titulo']) <= 100 and '<' not in desc and '>' not in desc, len(c['titulo'])
    corpo = {'snippet': {'title': c['titulo'], 'description': desc, 'tags': TAGS, 'categoryId': '27',
                         'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
             'status': {'privacyStatus': 'private', 'publishAt': c['quando'], 'selfDeclaredMadeForKids': False,
                        'containsSyntheticMedia': c['ia']}}
    try:
        req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                                     data=json.dumps(corpo).encode(), method='POST',
                                     headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                              'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(os.path.getsize(arq))})
        loc = urllib.request.urlopen(req).headers['Location']
        up = urllib.request.Request(loc, data=open(arq, 'rb').read(), method='PUT', headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4'})
        v = json.load(urllib.request.urlopen(up, timeout=600))
        res[str(n)] = {'id': v['id'], 'url': 'https://youtube.com/shorts/' + v['id'], 'publica_em': c['quando'], 'titulo': c['titulo']}
        print('short', n, v['id'], v['status'].get('publishAt'))
    except urllib.error.HTTPError as e:
        print('short', n, 'falhou', e.code, e.read().decode()[:300]); break
json.dump(res, open(os.path.join(AQUI, 'shorts_publicados.json'), 'w'), indent=1, ensure_ascii=False)
