"""Sobe um Short público no YouTube, agora.
uso: python3 sobe_short.py pausa-ml-shopee | publica-anuncio"""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
RODAPE = """
Saiba mais: https://l.tiops.com.br/connect-saiba-mais?o=shorts
Conector: https://mcp.tiops.com.br/mcp
Como conectar o Gemini (vídeo completo): https://youtu.be/rirx1DWcSuk?t=908
"""
SHORTS = {
    'pausa-ml-shopee': dict(
        titulo='Pausar anúncio no Mercado Livre e na Shopee com uma frase #shorts',
        desc='Uma frase no chat e o anúncio sem estoque sai do ar nos dois canais, sem abrir painel nenhum. '
             'O Marketplace Connect liga o ChatGPT, o Claude e o Gemini às suas lojas.\n' + RODAPE +
             '\n#mercadolivre #shopee #ia',
        tags=['pausar anuncio mercado livre', 'shopee', 'mercado livre', 'chatgpt', 'claude', 'gemini',
              'servidor mcp', 'marketplace connect', 'ia para ecommerce']),
    'publica-anuncio': dict(
        titulo='A IA publica seu anúncio no marketplace por você #shorts',
        desc='Do pedido no chat ao anúncio ativo: o Marketplace Connect liga o ChatGPT, o Claude e o Gemini às suas lojas.\n'
             + RODAPE + '\n#mercadolivre #shopee #chatgpt',
        tags=['anuncio com ia', 'mercado livre', 'shopee', 'chatgpt', 'claude', 'gemini',
              'servidor mcp', 'marketplace connect', 'ia para ecommerce']),
}

chave = sys.argv[1]
s = SHORTS[chave]
arq = os.path.join(AQUI, 'final', chave + '-short.mp4')
assert len(s['titulo']) <= 100 and '<' not in s['desc'] and '>' not in s['desc']
corpo = {'snippet': {'title': s['titulo'], 'description': s['desc'], 'tags': s['tags'], 'categoryId': '28',
                     'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
         'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}
tok = yt.refresh()
tam = os.path.getsize(arq)
req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
                             data=json.dumps(corpo).encode(), method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                      'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam)})
loc = urllib.request.urlopen(req).headers['Location']
with open(arq, 'rb') as f:
    up = urllib.request.Request(loc, data=f.read(), method='PUT',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4', 'Content-Length': str(tam)})
    v = json.load(urllib.request.urlopen(up, timeout=1800))
print('video', v['id'], v['status'].get('privacyStatus'), v['status'].get('uploadStatus'))
reg = os.path.join(AQUI, 'publicados.json')
dados = json.load(open(reg)) if os.path.exists(reg) else {}
dados['short-' + chave] = {'id': v['id'], 'url': 'https://youtube.com/shorts/' + v['id'], 'titulo': s['titulo']}
json.dump(dados, open(reg, 'w'), indent=1, ensure_ascii=False)
