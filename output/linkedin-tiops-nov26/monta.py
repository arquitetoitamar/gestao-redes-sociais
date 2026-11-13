#!/usr/bin/env python3
"""Peças da página TiOps Tecnologia no LinkedIn (calendário de 18/11 a 04/12/2026).

Reaproveita material já publicado no Instagram e troca o que só funciona lá:
- carrosséis viram documento PDF; sai o "@tiopstecnologia" do rodapé e o "Comenta CONNECT" do último slide;
- vídeos perdem o "Comente MADEIRA" / "Comenta NOTA" do fim (no LinkedIn não há ManyChat);
- os dois explicativos do Gemini ganham cartão final "Saiba mais".

  python3 monta.py           gera tudo em ./pecas
"""
import importlib.util, os, subprocess
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(AQUI)
PECAS = os.path.join(AQUI, 'pecas')
TRAB = os.path.join(AQUI, 'trab')
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
PRETO = '/System/Library/Fonts/Supplemental/Arial Black.ttf'
NEGRITO = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
os.makedirs(PECAS, exist_ok=True)
os.makedirs(TRAB, exist_ok=True)


def sh(*a):
    subprocess.run([FF, '-v', 'error', '-y', *a], check=True)


# ---------- documentos (carrosséis em PDF) ----------
CTA_ESTUDIO = (
    """  <div style='font-size:44px;font-weight:800'>Comenta</div>
  <div style='font-size:150px;font-weight:900;letter-spacing:4px;line-height:1.1'>CONNECT</div>
  <div style='font-size:38px;font-weight:700;line-height:1.3;margin-top:10px'>que eu te mando o link<br>e o passo a passo no direct.</div>""",
    """  <div style='font-size:132px;font-weight:900;line-height:1.1'>Saiba mais</div>
  <div style='font-size:46px;font-weight:800;line-height:1.3;margin-top:18px'>marketplaces.tiops.com.br</div>""")
CTA_SISTEMA = (
    """  <div style='display:inline-block;background:var(--ml);color:var(--ink);font-size:44px;font-weight:900;padding:12px 40px;border-radius:12px'>Comenta</div>
  <div style='font-size:170px;font-weight:900;letter-spacing:-5px;line-height:1;margin:26px 0 14px'>CONNECT</div>
  <div style='font-size:40px;font-weight:700;line-height:1.3'>que eu te mando o link e o<br>passo a passo no direct.</div>""",
    """  <div style='display:inline-block;background:var(--ml);color:var(--ink);font-size:44px;font-weight:900;padding:12px 40px;border-radius:12px'>Saiba mais</div>
  <div style='font-size:70px;font-weight:900;letter-spacing:-1px;line-height:1.1;margin:34px 0 18px'>marketplaces.tiops.com.br</div>
  <div style='font-size:40px;font-weight:700;line-height:1.3'>Funciona no Claude e no ChatGPT,<br>sem código e em português.</div>""")

DOCS = {
    # slide 1: a arte original tinha uma pessoa parecida com o Itamar ao lado dos monitores;
    # na página da TiOps entram só os 3 painéis (cartoes.py gera trab/heroi-estudio.png)
    'estudio-operacao-ia': dict(src='post-estudio-operacao-ia', n=6, cta=CTA_ESTUDIO,
                                troca={1: [("<img class='foto' src='file://%s/post-estudio-operacao-ia/assets/inteira.png' style='width:1000px;margin:0 -32px'>" % OUT,
                                            "<img src='file://%s/heroi-estudio.png' style='width:936px;display:block;margin:0 auto'>" % TRAB)]},
                                tira="<p class='rodape-txt' style='color:var(--cinza);font-size:30px'>Saiba mais em marketplaces.tiops.com.br</p>"),
    'sistema-ia-marketplace': dict(src='carrossel-sistema-ia-connect', n=10, cta=CTA_SISTEMA, tira=None),
}


def documento(nome, cfg):
    src = os.path.join(OUT, cfg['src'])
    pasta = os.path.join(TRAB, nome)
    os.makedirs(pasta, exist_ok=True)
    pngs = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')  # cache do Playwright some quando o disco enche
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for i in range(1, cfg['n'] + 1):
            h = open(os.path.join(src, 'html', 'slide-%02d.html' % i), encoding='utf-8').read()
            h = h.replace("'../assets/", "'file://%s/assets/" % src).replace('@tiopstecnologia', 'TiOps Tecnologia')
            for a, b_ in cfg.get('troca', {}).get(i, []):
                assert a in h, (nome, i, a[:40])
                h = h.replace(a, b_)
            if i == cfg['n']:
                assert cfg['cta'][0] in h, 'CTA do último slide mudou em %s' % cfg['src']
                h = h.replace(*cfg['cta'])
                if cfg['tira']:
                    assert cfg['tira'] in h
                    h = h.replace(cfg['tira'], '')
            assert 'Comenta' not in h and 'no direct' not in h and '@tiops' not in h, (nome, i)
            arq = os.path.join(pasta, 'slide-%02d.html' % i)
            open(arq, 'w', encoding='utf-8').write(h)
            pg.goto('file://' + arq)
            pg.wait_for_timeout(250)
            png = os.path.join(pasta, 'slide-%02d.png' % i)
            pg.screenshot(path=png)
            pngs.append(png)
        b.close()
    ims = [Image.open(x).convert('RGB') for x in pngs]
    pdf = os.path.join(PECAS, nome + '.pdf')
    ims[0].save(pdf, save_all=True, append_images=ims[1:], resolution=144)
    # folha para conferência
    w = 270
    folha = Image.new('RGB', (w * min(5, len(ims)), 338 * ((len(ims) + 4) // 5)), 'white')
    for k, im in enumerate(ims):
        folha.paste(im.resize((w, 338)), ((k % 5) * w, (k // 5) * 338))
    folha.save(os.path.join(TRAB, nome + '_folha.png'))
    return pdf


# ---------- vídeos ----------
def madeira():
    """Reel da MadeiraMadeira sem o 'Comente MADEIRA' final (corte de cena em 15,9 s)."""
    src = os.path.join(OUT, 'reel-madeiramadeira', 'reel_madeiramadeira.mp4')
    alvo = os.path.join(PECAS, 'madeiramadeira-linkedin.mp4')
    fim = 15.9
    sh('-i', src, '-t', '%.2f' % fim,
       '-vf', 'fade=t=out:st=%.2f:d=0.35' % (fim - 0.35),
       '-af', 'afade=t=out:st=%.2f:d=0.45' % (fim - 0.45),
       '-c:v', 'libx264', '-crf', '19', '-preset', 'slow', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', alvo)
    return alvo


def cartao_nfe(destino):
    """Cartão final no estilo do Reel da NF-e (fundo escuro quente, amarelo)."""
    L, A = 1080, 1920
    img = Image.new('RGB', (L, A))
    d = ImageDraw.Draw(img)
    for y in range(A):                       # mesmo degradê marrom -> preto do vídeo
        t = y / A
        d.line([(0, y), (L, y)], fill=(int(46 - 30 * t), int(32 - 20 * t), int(24 - 14 * t)))
    def centro(txt, f, y, cor):
        d.text(((L - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=cor)
    centro('SAIBA MAIS', ImageFont.truetype(PRETO, 112), 640, (255, 255, 255))
    f = ImageFont.truetype(PRETO, 70)
    txt = 'nfe.tiops.com.br'
    lw = d.textlength(txt, font=f)
    x0 = (L - lw) / 2 - 44
    d.rounded_rectangle((x0, 820, x0 + lw + 88, 960), radius=26, fill=(255, 209, 26))
    centro(txt, f, 845, (14, 26, 58))
    fb = ImageFont.truetype(NEGRITO, 46)
    centro('Claude, ChatGPT ou API do seu sistema', fb, 1010, (235, 235, 235))
    centro('Loja própria e marketplace', fb, 1075, (235, 235, 235))
    logo = Image.open(os.path.join(OUT, 'reel-nfe-claude', 'assets', 'logo-tiops.png')).convert('RGBA')
    logo.thumbnail((260, 160))
    cx = Image.new('RGBA', (logo.width + 60, logo.height + 40), (255, 255, 255, 255))
    cx.paste(logo, (30, 20), logo)
    img.paste(cx, ((L - cx.width) // 2, 1200))
    img.save(destino)


def nfe():
    """Reel da NF-e sem a fala 'Comenta NOTA' (n7 começa em 32,6 s): corta em 32,45 e fecha com cartão."""
    base = os.path.join(OUT, 'reel-nfe-claude')
    au = lambda f: os.path.join(base, 'audio', f)
    corte, card = 32.45, 2.6
    total = corte + card
    png = os.path.join(TRAB, 'cartao_nfe.png')
    cartao_nfe(png)
    narr = os.path.join(TRAB, 'nfe_narr.wav')
    mus = os.path.join(TRAB, 'nfe_mus.wav')
    pre = os.path.join(TRAB, 'nfe_pre.wav')
    mix = os.path.join(TRAB, 'nfe_mix.wav')
    # mesma receita de reel-nfe-claude/monta.py, sem a última fala
    sh('-i', au('narr_norm.wav'), '-af', 'atrim=0:%.2f,apad=whole_dur=%.2f' % (corte, total), '-ar', '48000', narr)
    sh('-i', os.path.join(OUT, 'reel-nfe-tiops', 'audio', 'musica.wav'), '-t', '%.2f' % (total + 0.2),
       '-af', 'afade=t=out:st=%.2f:d=2.2,loudnorm=I=-31:TP=-6:LRA=7' % (total - 2.0), '-ar', '48000', mus)
    sh('-i', mus, '-i', narr, '-filter_complex',
       '[0][1]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=350[m];[m][1]amix=inputs=2:normalize=0:duration=longest[a]',
       '-map', '[a]', pre)
    sh('-i', pre, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89:level=disabled', '-ar', '48000', mix)
    alvo = os.path.join(PECAS, 'emissor-nfe-claude-linkedin.mp4')
    sh('-i', os.path.join(base, 'reel_nfe_claude.mp4'), '-loop', '1', '-t', '%.2f' % card, '-i', png, '-i', mix,
       '-filter_complex',
       '[0:v]trim=0:%.2f,setpts=PTS-STARTPTS,fps=30,format=yuv420p[a];'
       '[1:v]scale=1080:1920,fps=30,format=yuv420p,fade=t=in:st=0:d=0.3[b];'
       '[a][b]concat=n=2:v=1:a=0[v]' % corte,
       '-map', '[v]', '-map', '2:a', '-t', '%.2f' % total,
       '-c:v', 'libx264', '-crf', '19', '-preset', 'slow', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', alvo)
    return alvo


def gemini():
    """Os dois explicativos do Gemini com cartão final de LinkedIn (reusa a base já montada)."""
    pasta = os.path.join(OUT, 'reels-gemini-ia-marketplace')
    spec = importlib.util.spec_from_file_location('rg', os.path.join(pasta, 'monta.py'))
    rg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rg)
    rg.CTA['linkedin'] = dict(pilula='Saiba mais', baixo='marketplaces.tiops.com.br')
    rg.FINAL = PECAS
    saidas = []
    for chave, cfg in rg.VIDEOS.items():
        b = os.path.join(pasta, 'trab', chave + '_base.mp4')
        n = os.path.join(pasta, 'trab', chave + '_norm.wav')
        if not (os.path.exists(b) and os.path.exists(n)):
            b, n = rg.base(chave, cfg), rg.audio(chave, cfg)
        saidas.append(rg.final(chave, cfg, b, n, 'linkedin'))
    return saidas


if __name__ == '__main__':
    for nome, cfg in DOCS.items():
        print(documento(nome, cfg))
    # madeira() e nfe() ficam só como registro: os vídeos têm rosto/voz do Itamar e não vão para a página da TiOps
    for s in gemini():
        print(s)
