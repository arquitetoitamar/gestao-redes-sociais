"""Sobe "Vídeo de produto com IA" no YouTube, público, com capa, capítulos, links e tags.
Palavras do autocompletar do YouTube (10/11/2026): video de produto com ia, como fazer video para mercado livre,
clip mercado livre, video ugc com ia, google flow video.
uso: python3 sobe_youtube.py <final.mp4> <capa.jpg> [agora|AAAA-MM-DDTHH:MM:SSZ]"""
import json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ, CAPA = sys.argv[1], sys.argv[2]
QUANDO = sys.argv[3] if len(sys.argv) > 3 else 'agora'
CAP = open(os.path.join(AQUI, 'capitulos.txt')).read().strip()

TITULO = 'VÍDEO DE PRODUTO COM IA para Mercado Livre e Shopee: Passo a Passo (Google Flow, ChatGPT e Gemini)'
DESC = f"""Vídeo de produto com IA, passo a passo: como fazer o vídeo (clip) do seu anúncio do Mercado Livre, da Shopee ou do TikTok Shop com o Google Flow, o ChatGPT e o Gemini, fiel ao produto. E como puxar as fotos, a descrição e a ficha técnica direto do anúncio com o Marketplace Connect.

🔗 Marketplace Connect (crie sua conta): https://l.tiops.com.br/video-produto?o=youtube
🔌 Conector do Marketplace Connect: https://mcp.tiops.com.br/mcp
(no Gemini: Personalizar → Conectores → Personalizado; no ChatGPT e no Claude: conector personalizado → cole o endereço)
🎬 Google Flow: https://flow.google.com

O que você precisa:
• Fotos do produto (2 ângulos; 8 ângulos deixam o vídeo mais fiel)
• Descrição e ficha técnica do anúncio
• Storyboard e prompt
• Uma IA que gera vídeo: Google Flow, ChatGPT ou Gemini

Capítulos:
{CAP}

Prompts usados no vídeo:
• /storyboard (com a foto do produto anexada)
• Gere um prompt para o vídeo UGC do produto no formato 9:16
• Gere o vídeo usando o ChatGPT e o storyboard acima
• Busque o anúncio da furadeira na conta de teste: imagens e descrição
• /storyboard deste produto
• Gere um vídeo UGC para este produto
O /storyboard é um comando que configurei no meu ChatGPT. Sem ele, peça: "Crie um storyboard de vídeo UGC vertical 9:16, de 15 segundos, para este produto, com as cenas e o texto de cada uma."

Prompt-modelo para o Flow (adapte ao seu produto):
Crie um vídeo UGC vertical 9:16 de 15 segundos. Use a foto anexada como referência fiel do produto: mesma cor, formato e detalhes. Uma pessoa apresenta o produto para a câmera, em ambiente natural, falando português do Brasil. 0 a 3 s: gancho segurando o produto. 3 a 7 s: close nos detalhes. 7 a 11 s: produto em uso. 11 a 15 s: volta para a câmera e convida a ver o anúncio. Luz natural, câmera de celular na mão, sem texto na tela.

Os vídeos de produto mostrados foram gerados com IA. O anúncio usado na demonstração é de uma conta de teste.

Sou o Itamar, fundador da Tiops e professor de IA na FIAP. Aqui no canal eu mostro como usar IA de verdade para vender em marketplace.

#videocomia #mercadolivre #shopee #googleflow #chatgpt"""

TAGS = ['video de produto com ia', 'fazer video de produto com ia', 'como fazer video de produto com ia', 'gerar video de produto com ia',
        'video para anuncio mercado livre', 'como fazer video para mercado livre', 'clip mercado livre', 'como fazer clip mercado livre',
        'video ugc com ia', 'como fazer video ugc com ia', 'google flow video', 'google flow tutorial', 'video com ia',
        'chatgpt video', 'gemini video', 'video para shopee', 'mercado livre', 'marketplace connect', 'inteligencia artificial']
tam = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1
assert tam <= 500, tam
assert '<' not in DESC and '>' not in DESC and len(TITULO) <= 100 and len(DESC) <= 5000, (len(TITULO), len(DESC))
print('título %d, descrição %d, tags %d caracteres' % (len(TITULO), len(DESC), tam))
if '--teste' in sys.argv:
    print(TITULO); print(DESC); sys.exit()

status = {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'containsSyntheticMedia': True}
if QUANDO != 'agora':
    status.update(privacyStatus='private', publishAt=QUANDO)
corpo = {'snippet': {'title': TITULO, 'description': DESC, 'tags': TAGS, 'categoryId': '27',
                     'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'},
         'status': status,
         'recordingDetails': {'recordingDate': '2026-11-10T00:00:00Z'}}
tok = yt.refresh()
tam_arq = os.path.getsize(ARQ)
req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status,recordingDetails',
                             data=json.dumps(corpo).encode(), method='POST',
                             headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                      'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(tam_arq)})
loc = urllib.request.urlopen(req).headers['Location']
with open(ARQ, 'rb') as f:
    up = urllib.request.Request(loc, data=f, method='PUT', headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4',
                                                                   'Content-Length': str(tam_arq)})
    v = json.load(urllib.request.urlopen(up, timeout=3600))
vid = v['id']; print('video', vid, v['status'])
try:
    th = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + vid,
                                data=open(CAPA, 'rb').read(), method='POST',
                                headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'})
    urllib.request.urlopen(th); capa = 'ok'
except urllib.error.HTTPError as e:
    capa = 'falhou %s %s' % (e.code, e.read().decode()[:200])
print('capa', capa)
json.dump({'id': vid, 'url': 'https://youtu.be/' + vid, 'quando': QUANDO, 'capa': capa, 'titulo': TITULO},
          open(os.path.join(AQUI, 'youtube_publicado.json'), 'w'), indent=1, ensure_ascii=False)
