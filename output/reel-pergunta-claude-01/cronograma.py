"""Cronograma do Reel a partir dos tempos por palavra da narração (trab/voz.words.json) -> trab/cronograma.json"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__)); T = lambda *p: os.path.join(AQUI, 'trab', *p)
w = json.load(open(T('voz.words.json'))); w = w.get('words', w) if isinstance(w, dict) else w
P = [{'w': x['text'], 's': x['start'], 'e': x['end']} for x in w]
def at(palavra, n=1, depois=0.0):
    hits = [p for p in P if p['w'].lower().strip('.,?!:…').startswith(palavra) and p['s'] >= depois]
    return hits[n - 1]['s']
M = {'naobaixa': at('não', 2), 'c2': at('a', 1, 4.5), 'itens': [at('visita', 2), at('pergunta'), at('foto'), at('vídeo'), at('ficha')],
     'porAnuncio': at('anúncio', 2), 'duzentos': at('duzentos'), 'naoda': at('não', 1, 13), 'chat': at('então'),
     'mc': at('pelo'), 'digita0': at('quais'), 'digita1': at('um', 1, 24) + 0.35, 'segundos': at('em', 1, 25), 'lista': at('lista'),
     'linhas': [at('esse', 1), at('esse', 2), at('esse', 3)], 'destaques': [at('sem', 1, 27), at('ficha', 2), at('pergunta', 2)],
     'nada': at('nada'), 'cta': at('comenta')}
dur = round(P[-1]['e'] + 0.9, 2)
json.dump({'duracao': dur, 'palavras': P, 'marcas': M}, open(T('cronograma.json'), 'w'), ensure_ascii=False, indent=1)
print('duração', dur, M)
