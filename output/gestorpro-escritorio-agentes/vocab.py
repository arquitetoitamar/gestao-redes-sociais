#!/usr/bin/env python3
"""Vocabulário de rótulos do GestorPro para o desfoque (trab/vocab_ui.json).

Só entra texto que o app mostra: strings entre aspas/crases e texto de JSX do
front (sem comentários, sem nome de variável). Nomes de pessoa comuns, de
loja e de produto vistos na gravação ficam de fora de propósito.
"""
import glob, json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = '/Users/itamar/git/gestor-pro'
BLOQ = set('''viana lenço lenco lenços vestido cetim bandana feminino feminina multicolorido
claudia cláudia fernanda fernando alessandra bronstein carrato grande rocha appolonio
maria joao joão jose josé ana carlos pedro paulo lucas marcos rafael bruno felipe phellipe itamar juliana mariana
camila amanda bruna patricia patrícia ricardo rodrigo marcelo eduardo gabriel gustavo leonardo thiago tiago daniel
diego andre andré luiz luis luís antonio antônio francisco sandra adriana aline vanessa carla cristina renata
tatiana simone silva santos oliveira souza sousa lima pereira costa ferreira almeida ribeiro carvalho gomes
martins araujo araújo barbosa cardoso nascimento moreira cavalcanti mendes nunes teixeira dias freitas
rua avenida chácara chacara carapicuíba carapicuiba invernada lúcia lucia
azul branco branca rosa preto preta verde amarelo quadrado longo mini multi kit band cab cabe cabelo pescoço
ocasional porte custom det monte mundo blusa bolsa festa casamento estampada echarpe cachecol'''.split())


def main():
    arqs = glob.glob(APP + '/src/ui/*.jsx') + glob.glob(APP + '/src/ui/*.js') + \
        [APP + '/' + f for f in ('escritorio.html', 'app.jsx', 'components.jsx', 'tweaks-panel.jsx')]
    textos = []
    for f in arqs:
        s = open(f, encoding='utf-8', errors='ignore').read()
        s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
        s = re.sub(r'(?m)(^|[^:"\'])//.*$', r'\1', s)
        s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
        textos += re.findall(r'"([^"\\\n]{1,200})"', s)
        textos += re.findall(r"'([^'\\\n]{1,200})'", s)
        textos += re.findall(r'`([^`]{1,400})`', s)
        textos += re.findall(r'>([^<>{}\n]{1,200})<', s)
    ws = set()
    for t in textos:
        for w in re.findall(r'[A-Za-zÀ-ÿ]{2,}', t):
            ws.add(w.lower())
    # palavras que ele fala no vídeo (frases genéricas do chat do agente ficam legíveis)
    fala = os.path.join(AQUI, 'trab', 'vocab_fala.json')
    if os.path.exists(fala):
        ws |= set(json.load(open(fala)))
    ws -= BLOQ
    ws |= {'stampaholics', 'sublipaper'}          # lojas liberadas pelo Itamar (28/10)
    json.dump(sorted(ws), open(os.path.join(AQUI, 'trab', 'vocab_ui.json'), 'w'), ensure_ascii=False)
    print(len(ws), 'palavras;', 'len' in ws, 'mínimo' in ws, 'escritório' in ws, 'recomendações' in ws)


if __name__ == '__main__':
    main()
