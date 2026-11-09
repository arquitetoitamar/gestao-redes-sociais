"""Sobe o vídeo editado "Afiliado Shopee no ChatGPT" no YouTube, público, com capa, capítulos e tags.
uso: python3 sobe_youtube.py <final.mp4> [agora|AAAA-MM-DDTHH:MM:SSZ]"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = sys.argv[1]
QUANDO = sys.argv[2] if len(sys.argv) > 2 else 'agora'
CAP = open(os.path.join(AQUI, 'capitulos.txt')).read().strip()

TITULO = 'AFILIADO SHOPEE com IA: o ChatGPT acha os produtos, gera o link e o vídeo (passo a passo 2026)'
DESC = f"""Afiliado Shopee com inteligência artificial, passo a passo: conecte sua conta de Afiliados Shopee no ChatGPT (ou no Claude) e peça em português os produtos com maior comissão, o seu link de afiliado, o texto para grupo de achadinhos e até o vídeo do produto.

🔗 Marketplace Connect (crie sua conta e conecte a Shopee Afiliados): https://l.tiops.com.br/shopee-afiliados?o=youtube
🔌 Endereço do conector Afiliados Shopee: https://mcp.tiops.com.br/mcp/afiliados
(no ChatGPT: Plugins → Adicionar servidor MCP personalizado → cole o endereço; no Claude: Conectores → Adicionar conector personalizado)

O que você precisa:
• Conta no programa de Afiliados Shopee com acesso à API (App ID e Secret)
• ChatGPT (Plus ou Go) ou Claude
• Conta no Marketplace Connect

Capítulos:
{CAP}

Prompts usados no vídeo:
• Encontre os produtos com maior comissão
• Quero vender esse produto. Gere meu link de afiliado
• Gere uma descrição para um grupo de achadinhos com o link e o vídeo
• Gere um vídeo do produto com base nas imagens e na descrição
• Gere o roteiro para criar o vídeo no Flow
• Consulte minhas comissões

Os dados vêm da sua própria conta de afiliado, não de uma busca na internet. Comissões e ofertas mudam conforme a Shopee. Os vídeos de produto mostrados foram gerados com IA.

Sou o Itamar, fundador da Tiops e professor de IA na FIAP. Aqui no canal eu mostro como usar IA de verdade para vender em marketplace.

#afiliadoshopee #shopeeafiliados #chatgpt #claude #inteligenciaartificial"""

TAGS = ['afiliado shopee', 'shopee afiliados', 'afiliado shopee com ia', 'ia para afiliados shopee', 'como ser afiliado shopee 2026',
        'link de afiliado shopee', 'afiliado shopee chatgpt', 'chatgpt shopee', 'claude afiliado shopee', 'shopee video afiliado com ia',
        'afiliado shopee passo a passo', 'achadinhos shopee', 'afiliado shopee do zero', 'marketplace connect', 'conector mcp',
        'inteligencia artificial', 'chatgpt', 'claude', 'tiops']
# limite do YouTube: 500 caracteres, tag com espaço conta +2 (aspas)
tam = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1
assert tam <= 500, tam
assert '<' not in DESC and '>' not in DESC and len(TITULO) <= 100 and len(DESC) <= 5000, (len(TITULO), len(DESC))

status = {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}
if QUANDO != 'agora':
    status.update(privacyStatus='private', publishAt=QUANDO)
corpo = {'snippet': {'title': TITULO, 'description': DESC, 'tags': TAGS, 'categoryId': '27',
                     'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
         'status': status,
         'recordingDetails': {'recordingDate': '2026-11-09T00:00:00Z'}}
tok = yt.refresh()
tam_arq = os.path.getsize(ARQ)
req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status,recordingDetails',
                             data=json.dumps(corpo).encode(), method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                      'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam_arq)})
loc = urllib.request.urlopen(req).headers['Location']
with open(ARQ, 'rb') as f:
    up = urllib.request.Request(loc, data=f.read(), method='PUT', headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4'})
v = json.load(urllib.request.urlopen(up, timeout=1800))
vid = v['id']; print('video', vid, v['status'])
try:
    th = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + vid,
                                data=open(os.path.join(AQUI, 'capa_a.jpg'), 'rb').read(), method='POST',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'})
    urllib.request.urlopen(th); capa = 'ok'
except urllib.error.HTTPError as e:
    capa = 'falhou %s %s' % (e.code, e.read().decode()[:200])
print('capa', capa)
json.dump({'id': vid, 'url': 'https://youtu.be/' + vid, 'quando': QUANDO, 'capa': capa, 'titulo': TITULO},
          open(os.path.join(AQUI, 'youtube_publicado.json'), 'w'), indent=1, ensure_ascii=False)
