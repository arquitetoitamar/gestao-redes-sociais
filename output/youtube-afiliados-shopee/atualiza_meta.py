"""Atualiza título, descrição e tags do vídeo Mg7mIiimaOw no padrão dos primeiros colocados de "shopee afiliados"
(análise de 09/11/2026: título começa com AFILIADO SHOPEE + "Passo a Passo" + verbo VENDER; tags de cauda longa)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts/trilha'))
import yt

VID = 'Mg7mIiimaOw'
TITULO = 'AFILIADO SHOPEE com IA: Passo a Passo para VENDER com o ChatGPT (Links, Vídeos e Achadinhos 2026)'
TAGS = ['afiliado shopee', 'afiliado shopee passo a passo', 'como vender na shopee', 'shopee afiliados', 'afiliado shopee com ia',
        'afiliado shopee vale a pena', 'afiliado shopee como divulgar', 'link de afiliado shopee', 'como ser afiliado shopee',
        'como ser afiliado shopee 2026', 'shopee video afiliado', 'video com ia para shopee', 'afiliado shopee chatgpt',
        'chatgpt shopee', 'renda extra', 'como ganhar dinheiro na shopee', 'achadinhos shopee', 'google flow',
        'marketplace connect', 'inteligencia artificial']
tam = sum(len(t) + (2 if ' ' in t else 0) for t in TAGS) + len(TAGS) - 1
assert tam <= 500 and len(TITULO) <= 100, (tam, len(TITULO))

v = yt.call('GET', 'videos', {'part': 'snippet', 'id': VID})['items'][0]['snippet']
desc = v['description']
velho = desc.split('\n', 1)[0]
novo = ('AFILIADO SHOPEE com IA, passo a passo para vender com o ChatGPT: conecte sua conta de Afiliados Shopee no ChatGPT '
        '(ou no Claude) e peça em português os produtos com maior comissão, o seu link de afiliado, o texto para grupo de '
        'achadinhos e o vídeo do produto.')
desc = desc.replace(velho, novo, 1)
desc = desc.replace('#afiliadoshopee #shopeeafiliados #chatgpt #claude #inteligenciaartificial',
                    '#afiliadoshopee #shopeeafiliados #shopeevideo #chatgpt #inteligenciaartificial')
assert '<' not in desc and '>' not in desc and len(desc) <= 5000
corpo = {'id': VID, 'snippet': {'title': TITULO, 'description': desc, 'tags': TAGS, 'categoryId': v['categoryId'],
                                'defaultLanguage': 'pt-BR', 'defaultAudioLanguage': 'pt-BR'}}
r = yt.call('PUT', 'videos', {'part': 'snippet'}, corpo)
print('ok', r['snippet']['title'], len(r['snippet'].get('tags', [])), 'tags', tam, 'caracteres')
