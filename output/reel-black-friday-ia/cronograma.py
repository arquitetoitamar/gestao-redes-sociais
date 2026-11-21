"""Cronograma do Reel: pausas inseridas, tempo de cada palavra (pelas regiões de fala entre silêncios) e cenas.
Saída: trab/cronograma.json (tempos já no relógio do vídeo final)."""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
# regiões de fala medidas com silencedetect (-35 dB, 0,18 s) no avatar.mp4
REG = [(0.317, 2.583), (3.157, 4.070), (4.2625, 5.0727), (5.3176, 5.9573), (6.711, 10.695), (11.134, 14.408),
       (14.730, 16.098), (16.350, 17.330), (17.612, 20.493), (20.718, 21.528), (22.093, 23.029), (23.408, 24.161),
       (24.558, 25.804), (26.248, 29.933)]
FRASES = ["Essa é a primeira Black Friday com IA.", "E quem usar errado", "vai vender muito...", "no prejuízo.",
          "Por isso eu montei um guia completo pra Mercado Livre, Shopee e TikTok Shop.",
          "São 26 prompts prontos pro Claude e pro ChatGPT,", "um calendário dia a dia", "até a Cyber Monday,",
          "e um simulador que mostra até onde dá pra dar desconto", "sem perder margem.", "A IA recomenda,", "você aprova,",
          "e ela executa na sua loja.", "Comenta BLACK aqui embaixo que eu te mando o guia completo no direct."]
# cortes no áudio (dentro de silêncios) e pausa inserida em cada um
PAUSAS = [(10.85, 0.35), (21.75, 0.30), (26.00, 0.45)]
FIM_SRC, CAUDA = 30.2, 0.8

def out(s):
    return s + sum(d for c, d in PAUSAS if s >= c)

pal = []
for (a, b), fr in zip(REG, FRASES):
    ws = fr.split(); tot = sum(len(w) + 1 for w in ws); t = a
    for w in ws:
        d = (b - a) * (len(w) + 1) / tot
        pal.append({'w': w, 's': round(out(t), 3), 'e': round(out(t + d), 3)}); t += d
dur = round(out(FIM_SRC) + CAUDA, 3)
cenas = [  # (tipo, início, fim) no relógio final
    ('avatar', 0, 6.45), ('broll:hero', 6.45, 11.25), ('broll:prompts', 11.25, 14.95), ('broll:calendario', 14.95, 18.0),
    ('broll:margem', 18.0, 22.7), ('avatar', 22.7, dur)]
json.dump({'duracao': dur, 'pausas': PAUSAS, 'palavras': pal, 'cenas': cenas,
           'cta': [round(out(26.248), 3), dur], 'transicao_cta': [round(out(25.85), 3), round(out(26.248), 3)]},
          open(os.path.join(AQUI, 'trab', 'cronograma.json'), 'w'), ensure_ascii=False, indent=1)
print('duração', dur, '| palavras', len(pal), '| CTA', round(out(26.248), 2), '| prejuízo', [w for w in pal if 'prejuízo' in w['w']])
