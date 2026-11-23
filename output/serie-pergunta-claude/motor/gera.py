"""Gera um episódio da série "Pergunta pro Claude" a partir de episodios/NN-slug.json.
uso: python3 motor/gera.py episodios/03-fotos.json [--sem-voz]
Saída: ep-NN-slug/videos/ep-NN.mp4, ep-NN-slug/legenda_ig.md, ep-NN-slug/trab/folha.jpg
Códigos de saída: 0 ok · 3 HeyGen sem saldo/erro de voz · 4 narração fora do padrão (âncoras) · 5 duração fora de 25-60 s

Padrão obrigatório da narração (as cenas se ancoram nessas palavras):
  <gancho e problema> ... "Faz assim." "Primeiro:" ... "Segundo:" ... "Terceiro:" ... "Quarto:" ...
  "Agora, fazer essa conta em <N> anúncios ..." "Eu pergunto pro Claude, ligado no ... pelo Marketplace Connect:"
  <pergunta terminando em ?> "Ele ..." "Comenta CONNECT que eu te mando o link no direct."
"""
import json, os, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.abspath(os.path.join(RAIZ, '../..'))
VOZ = 'c463ef5bf11146d49bf754fa1e515401'
FPS = 30


def sh(*a, **k):
    return subprocess.run(list(a), check=True, **k)


def marcas(P, ep):
    def idx(pred, depois=0.0):
        for i, x in enumerate(P):
            if x['s'] >= depois and pred(x['w'].lower().strip('.,?!:…"“”')):
                return i
        raise SystemExit(4)
    t = lambda i: P[i]['s']
    c2 = t(idx(lambda w: w == 'faz'))
    passos = [t(idx(lambda w, p=p: w == p, c2)) for p in ('primeiro', 'segundo', 'terceiro', 'quarto')]
    c3 = t(idx(lambda w: w == 'agora', passos[3]))
    chat = t(idx(lambda w: w == 'eu', c3))
    mc = t(idx(lambda w: w == 'pelo', chat))
    i_conn = idx(lambda w: w == 'connect', mc)
    d0 = P[i_conn + 1]['s']
    i_q = next(i for i in range(i_conn + 1, len(P)) if P[i]['w'].endswith('?'))
    d1 = P[i_q]['e'] + 0.3
    ele = t(idx(lambda w: w == 'ele', d1 - 0.3))
    cta = t(idx(lambda w: w == 'comenta', ele))
    dp = ep['chat'].get('destaque_palavra')
    dest = t(idx(lambda w: w.startswith(dp.lower()), ele)) if dp else ele + 1.6
    M = {'c2': c2, 'passos': passos, 'c3': c3, 'vezes': c3 + 1.0, 'chat': chat, 'mc': mc, 'digita0': d0, 'digita1': d1,
         'ele': ele, 'lista': ele + 0.6, 'destaque': dest, 'cta': cta}
    conta = ep['c2'].get('conta')
    if conta:
        M['conta'] = t(idx(lambda w: w.startswith(conta['palavra_inicio'].lower()), passos[1]))
        M['resultado'] = t(idx(lambda w: w.startswith(conta['palavra_resultado'].lower()), M['conta']))
    return M


def faixa(args):
    html, tempos, nomes = args
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.set_content(html, wait_until='networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(400)
        for tt, n in zip(tempos, nomes):
            pg.evaluate('t=>window.seek(t)', tt); pg.screenshot(path=n, type='jpeg', quality=92)
        b.close()
    return len(tempos)


def main():
    arq = sys.argv[1]; sem_voz = '--sem-voz' in sys.argv
    ep = json.load(open(arq, encoding='utf-8'))
    pasta = os.path.join(RAIZ, 'ep-%02d-%s' % (ep['num'], ep['slug'])); T = lambda *p: os.path.join(pasta, 'trab', *p)
    os.makedirs(T('mot'), exist_ok=True); os.makedirs(os.path.join(pasta, 'videos'), exist_ok=True)
    open(os.path.join(pasta, 'narracao.txt'), 'w', encoding='utf-8').write(ep['narracao'].strip() + '\n')
    # 1) voz (HeyGen, voz clonada do Itamar)
    if not os.path.exists(T('voz.words.json')):
        if sem_voz:
            raise SystemExit('sem voz gerada e --sem-voz pedido')
        env = dict(os.environ)
        for l in open(os.path.join(REPO, '.env'), encoding='utf-8'):
            if l.startswith('HEYGEN_API_KEY='):
                env['HEYGEN_API_KEY'] = l.split('=', 1)[1].strip().strip('"')
        r = subprocess.run(['node', os.path.join(REPO, '.agents/skills/media-use/audio/scripts/heygen-tts.mjs'),
                            os.path.join(pasta, 'narracao.txt'), '-o', T('voz.wav'), '--words', T('voz.words.json'), '--voice', VOZ],
                           env=env, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(T('voz.words.json')):
            print('ERRO HEYGEN:', (r.stderr or r.stdout)[-600:]); sys.exit(3)
    w = json.load(open(T('voz.words.json'))); w = w.get('words', w) if isinstance(w, dict) else w
    P = [{'w': x['text'], 's': x['start'], 'e': x['end']} for x in w]
    dur = round(P[-1]['e'] + 0.9, 2)
    if not 25 <= dur <= 60:
        print('duração fora do padrão', dur); sys.exit(5)
    M = marcas(P, ep)
    crono = {'duracao': dur, 'palavras': P, 'marcas': M}
    json.dump(crono, open(T('cronograma.json'), 'w'), ensure_ascii=False, indent=1)
    # 2) animação
    html = open(os.path.join(RAIZ, 'motor', 'template.html'), encoding='utf-8').read()
    html = html.replace('__CRONO__', json.dumps(crono, ensure_ascii=False)).replace('__EP__', json.dumps(ep, ensure_ascii=False))
    open(T('motion.html'), 'w', encoding='utf-8').write(html)
    n = int(round(dur * FPS)); k = 4; idx = list(range(n)); partes = [idx[i::k] for i in range(k)]
    jobs = [(html, [i / FPS for i in pt], [T('mot', 'm_%05d.jpg' % i) for i in pt]) for pt in partes]
    with ProcessPoolExecutor(k) as ex:
        print('quadros', sum(ex.map(faixa, jobs)))
    # 3) áudio (voz + sala + trilha + efeitos)
    sh(sys.executable, os.path.join(RAIZ, 'motor', 'audio.py'), pasta)
    # 4) montagem
    final = os.path.join(pasta, 'videos', 'ep-%02d.mp4' % ep['num'])
    sh('ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', T('mot', 'm_%05d.jpg'), '-i', T('audio_final.wav'), '-map', '0:v', '-map', '1:a',
       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7',
       '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final)
    # 5) folha de conferência (1 quadro por cena)
    from PIL import Image
    ts = [1.8, M['passos'][3] + 0.8, M['vezes'] + 0.6, M['digita1'] - 0.5, M['destaque'] + 0.6, M['cta'] + 1.0]
    ims = [Image.open(T('mot', 'm_%05d.jpg' % min(n - 1, int(x * FPS)))).resize((270, 480)) for x in ts]
    folha = Image.new('RGB', (270 * len(ims), 480)); [folha.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
    folha.save(T('folha.jpg'), quality=86)
    open(os.path.join(pasta, 'legenda_ig.md'), 'w', encoding='utf-8').write(
        '# Pergunta pro Claude #%d — %s\n\n%s\n' % (ep['num'], ep['slug'], ep['legenda_ig'].strip()))
    print('ok', final, dur, 's')


if __name__ == '__main__':
    main()
