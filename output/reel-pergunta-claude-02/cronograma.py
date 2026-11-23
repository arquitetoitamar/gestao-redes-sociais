"""Cronograma do Reel #2 a partir dos tempos por palavra -> trab/cronograma.json"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__)); T = lambda *p: os.path.join(AQUI, 'trab', *p)
w = json.load(open(T('voz.words.json'))); w = w.get('words', w) if isinstance(w, dict) else w
P = [{'w': x['text'], 's': x['start'], 'e': x['end']} for x in w]
def at(p, n=1, depois=0.0):
    h = [x for x in P if x['w'].lower().strip('.,?!:…').startswith(p) and x['s'] >= depois]; return h[n - 1]['s']
M = {'c2': at('faz'), 'passos': [at('primeiro'), at('segundo'), at('terceiro'), at('quarto')], 'vendeu': at('vendeu', 2),
     'noventa': at('noventa'), 'c3': at('agora'), 'oitenta': at('oitenta'), 'chat': at('eu', 1, 26.5), 'mc': at('pelo', 1, 28),
     'digita0': at('quanto', 1, 30), 'digita1': at('dias', 2) + 0.6, 'ele': at('ele'), 'lista': at('lista'), 'subindo': at('subindo', 2),
     'cta': at('comenta')}
dur = round(P[-1]['e'] + 0.9, 2)
json.dump({'duracao': dur, 'palavras': P, 'marcas': M}, open(T('cronograma.json'), 'w'), ensure_ascii=False, indent=1)
print('duração', dur, M)
