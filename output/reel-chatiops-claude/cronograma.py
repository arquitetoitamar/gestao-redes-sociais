"""Cronograma do Reel Chatiops + Claude a partir dos tempos por palavra.
Usa trab/voz.words.json (HeyGen) se existir; senão trab/estimado.words.json (só para storyboard)."""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__)); T = lambda *p: os.path.join(AQUI, 'trab', *p)
arq = T('voz.words.json') if os.path.exists(T('voz.words.json')) else T('estimado.words.json')
w = json.load(open(arq)); w = w.get('words', w) if isinstance(w, dict) else w
P = [{'w': x.get('text', x.get('w')), 's': x.get('start', x.get('s')), 'e': x.get('end', x.get('e'))} for x in w]
def at(p, n=1, depois=0.0):
    h = [x for x in P if x['w'].lower().strip('.,?!:…').startswith(p) and x['s'] >= depois]; return h[n - 1]['s']
M = {'c2': at('o', 1, 2), 'c3': at('são'), 'c4': at('primeiro'), 'conect': at('qr'), 'c5': at('segundo'), 'cria': at('cria'),
     'c6': at('terceiro'), 'base': at('base'), 'madrugada': at('madrugada'), 'c7': at('quando'), 'c8': at('depois'),
     'prompts': [at('lista'), at('quem'), at('dispara')], 'c9': at('o', 1, at('campanha'))}
dur = round(P[-1]['e'] + 0.9, 2)
json.dump({'duracao': dur, 'palavras': P, 'marcas': M}, open(T('cronograma.json'), 'w'), ensure_ascii=False, indent=1)
print(os.path.basename(arq), 'duração', dur, M)
