"""Motions do vídeo MoreLogin: cada peça é HTML + GSAP, renderizada quadro a quadro em PNG com transparência.

uso: python3 motions.py [nome ...]   (sem nome = todas)  -> trab/mot/<nome>/f_00000.png
O Chrome do sistema roda headless (channel="chrome"); a timeline do GSAP fica pausada e cada quadro é um seek.
"""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, 'trab', 'mot')
FPS = 30
LINK = 'morelogin.com/register?from=AAF7cYpPRan2'

BASE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=block" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<style>
:root{--mag:#e400ff;--azul:#2433ff;--verde:#19e6a0;--tinta:#0d0b2b;}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;background:transparent;overflow:hidden;
  font-family:'Plus Jakarta Sans',-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
.grad{background:linear-gradient(100deg,var(--mag),#8a1bff 45%,var(--azul))}
.pill{position:absolute;display:flex;align-items:center;gap:14px;border-radius:999px;color:#fff;font-weight:800}
.card{position:absolute;background:rgba(255,255,255,.96);border-radius:28px;box-shadow:0 24px 60px rgba(30,20,90,.28)}
.logo{width:46px;height:46px}
</style></head><body>__CORPO__
<script>
const tl = gsap.timeline({paused:true});
__TL__
window.DUR = tl.duration();
window.seek = t => { tl.seek(t, false); };
</script></body></html>"""

LOGO = """<svg class="logo" viewBox="0 0 64 64"><path d="M6 46V18l16 14 10-9 10 9 16-14v28l-16-14-10 9-10-9z" fill="none"/>
<path d="M6 44 L6 20 L22 34 L32 25" stroke="#19e6a0" stroke-width="9" fill="none" stroke-linejoin="round"/>
<path d="M32 25 L42 34 L58 20 L58 44" stroke="#5a7cff" stroke-width="9" fill="none" stroke-linejoin="round"/></svg>"""


def peca_intro():
    corpo = f"""
<div id="fundo" style="position:absolute;inset:0;background:radial-gradient(1200px 700px at 30% 40%,#2a1060,#0b0820 70%)"></div>
<div id="brilho" class="grad" style="position:absolute;width:1400px;height:1400px;border-radius:50%;filter:blur(160px);opacity:.35;left:900px;top:-300px"></div>
<div id="selo" class="pill" style="left:160px;top:250px;padding:12px 26px;font-size:26px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25)">PUBLICIDADE · PARCERIA MORELOGIN</div>
<div id="t1" style="position:absolute;left:160px;top:330px;color:#fff;font-weight:800;font-size:100px;line-height:1.04;letter-spacing:-2px">Sua IA operando várias contas.<br><span id="t2" style="background:linear-gradient(100deg,#ff5cf4,#7d8bff);-webkit-background-clip:text;color:transparent">Sem misturar nada.</span></div>
<div id="sub" style="position:absolute;left:164px;top:600px;color:#cfd2ff;font-size:38px;font-weight:500;max-width:1180px">Claude + MoreLogin: perfis isolados, celular em nuvem e automação para Shopee, Mercado Livre e redes sociais</div>
<div id="marca" class="pill grad" style="left:160px;top:760px;padding:16px 34px 16px 22px;font-size:44px">{LOGO}MoreLogin</div>
"""
    tl = """
tl.from('#brilho',{opacity:0,scale:.6,duration:1.2,ease:'power2.out'},0)
  .from('#selo',{y:30,opacity:0,duration:.5,ease:'power3.out'},.2)
  .from('#t1',{y:60,opacity:0,duration:.7,ease:'power3.out'},.35)
  .from('#t2',{backgroundPosition:'200% 0',opacity:0,duration:.6},.75)
  .from('#sub',{y:30,opacity:0,duration:.6,ease:'power3.out'},.9)
  .from('#marca',{scale:.6,opacity:0,duration:.6,ease:'back.out(2)'},1.15)
  .to('#brilho',{x:-200,y:120,duration:4,ease:'sine.inOut'},0)
  .to({}, {duration:.1}, 4.4)
  .to(['#selo','#t1','#sub','#marca'],{y:-40,opacity:0,stagger:.05,duration:.45,ease:'power2.in'},4.5)
  .to(['#fundo','#brilho'],{opacity:0,duration:.5},4.8);
"""
    return corpo, tl


def peca_nome():
    corpo = """
<div id="box" class="card" style="left:70px;top:860px;padding:22px 34px 22px 30px;display:flex;align-items:center;gap:20px">
 <div id="barra" class="grad" style="width:10px;height:74px;border-radius:6px"></div>
 <div><div id="n" style="font-size:40px;font-weight:800;color:#0d0b2b">Itamar Rocha</div>
 <div id="c" style="font-size:25px;font-weight:500;color:#5a5880;margin-top:2px">Arquiteto de Soluções · IA para marketplaces</div></div></div>"""
    tl = """
tl.from('#box',{x:-80,opacity:0,duration:.6,ease:'power3.out'},0)
  .from('#barra',{scaleY:0,transformOrigin:'50% 100%',duration:.5,ease:'power3.out'},.2)
  .from(['#n','#c'],{y:16,opacity:0,stagger:.1,duration:.45},.3)
  .to('#box',{x:-80,opacity:0,duration:.45,ease:'power2.in'},5.0);
"""
    return corpo, tl


def peca_capitulo(num, titulo):
    corpo = f"""
<div id="box" class="pill grad" style="left:60px;top:48px;padding:12px 30px 12px 12px;font-size:32px;box-shadow:0 14px 40px rgba(60,20,160,.35)">
 <div id="num" style="width:58px;height:58px;border-radius:50%;background:#fff;color:#5b1bff;display:flex;align-items:center;justify-content:center;font-size:30px">{num}</div>
 <span id="tt">{titulo}</span></div>"""
    tl = """
tl.from('#box',{y:-40,opacity:0,duration:.55,ease:'back.out(1.8)'},0)
  .from('#tt',{x:-20,opacity:0,duration:.4},.25)
  .to('#box',{y:-40,opacity:0,duration:.4,ease:'power2.in'},4.4);
"""
    return corpo, tl


def peca_destaque(titulo, texto, icone):
    corpo = f"""
<div id="box" class="card" style="right:70px;top:150px;width:560px;padding:34px 36px">
 <div style="display:flex;align-items:center;gap:16px">
  <div id="ic" class="grad" style="width:66px;height:66px;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:34px">{icone}</div>
  <div id="tt" style="font-size:38px;font-weight:800;color:#0d0b2b;line-height:1.1">{titulo}</div></div>
 <div id="tx" style="font-size:27px;color:#46446a;margin-top:18px;line-height:1.35;font-weight:500">{texto}</div>
 <div id="lin" class="grad" style="height:6px;border-radius:4px;margin-top:22px;width:100%"></div></div>"""
    tl = """
tl.from('#box',{x:120,opacity:0,duration:.6,ease:'power3.out'},0)
  .from('#ic',{scale:0,rotation:-90,duration:.5,ease:'back.out(2)'},.25)
  .from('#tt',{y:14,opacity:0,duration:.4},.35)
  .from('#tx',{y:14,opacity:0,duration:.4},.5)
  .from('#lin',{scaleX:0,transformOrigin:'0 50%',duration:6,ease:'none'},.6)
  .to('#box',{x:120,opacity:0,duration:.45,ease:'power2.in'},6.6);
"""
    return corpo, tl


def peca_cta():
    corpo = f"""
<div id="box" class="pill" style="left:50%;top:930px;transform:translateX(-50%);padding:14px 34px 14px 16px;font-size:30px;background:#0d0b2b;box-shadow:0 18px 50px rgba(20,10,60,.4);white-space:nowrap">
 <div id="pres" class="grad" style="width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px">🎁</div>
 <span><b style="color:#7dffd0">50 perfis grátis por 2 semanas</b> + <b style="color:#ff9cf6">15% OFF</b> · link na descrição</span></div>"""
    tl = """
tl.from('#box',{y:80,opacity:0,duration:.6,ease:'back.out(1.6)'},0)
  .fromTo('#pres',{rotation:-20},{rotation:20,duration:.25,repeat:5,yoyo:true,ease:'sine.inOut'},.5)
  .to('#box',{y:80,opacity:0,duration:.45,ease:'power2.in'},6.5);
"""
    return corpo, tl


def peca_final():
    corpo = f"""
<div id="fundo" style="position:absolute;inset:0;background:radial-gradient(1200px 700px at 70% 40%,#2a1060,#0b0820 70%)"></div>
<div id="t" style="position:absolute;left:0;right:0;top:250px;text-align:center;color:#fff;font-weight:800;font-size:84px;letter-spacing:-1px">Teste a MoreLogin pelo meu link</div>
<div id="of" style="position:absolute;left:0;right:0;top:380px;text-align:center;font-size:46px;font-weight:700;color:#7dffd0">50 perfis grátis por 2 semanas + 15% de desconto</div>
<div id="lk" class="pill grad" style="left:50%;top:500px;transform:translateX(-50%);padding:22px 44px 22px 26px;font-size:42px;white-space:nowrap">{LOGO}{LINK}</div>
<div id="ds" style="position:absolute;left:0;right:0;top:650px;text-align:center;color:#cfd2ff;font-size:34px;font-weight:500">O link também está fixado nos comentários</div>
<div id="pb" style="position:absolute;left:0;right:0;top:960px;text-align:center;color:#8d8fbf;font-size:24px">Publicidade · conteúdo patrocinado pela MoreLogin</div>"""
    tl = """
tl.from('#fundo',{opacity:0,duration:.5},0)
  .from('#t',{y:50,opacity:0,duration:.6,ease:'power3.out'},.2)
  .from('#of',{y:30,opacity:0,duration:.5},.5)
  .from('#lk',{scale:.7,opacity:0,duration:.6,ease:'back.out(1.8)'},.75)
  .from('#ds',{opacity:0,duration:.5},1.1)
  .from('#pb',{opacity:0,duration:.5},1.3)
  .to('#lk',{scale:1.04,duration:.6,repeat:7,yoyo:true,ease:'sine.inOut'},1.6)
  .to({}, {duration:.1}, 7.9);
"""
    return corpo, tl


def catalogo():
    pecas = {'intro': peca_intro(), 'nome': peca_nome(), 'cta': peca_cta(), 'final': peca_final()}
    plano = json.load(open(os.path.join(AQUI, 'plano_motions.json')))
    for c in plano.get('capitulos', []):
        pecas['cap%d' % c['num']] = peca_capitulo(c['num'], c['titulo'])
    for d in plano.get('destaques', []):
        pecas['dest_' + d['id']] = peca_destaque(d['titulo'], d['texto'], d['icone'])
    return pecas


RECORTE = {'nome': (40, 820, 900, 1060), 'cta': (300, 880, 1620, 1060)}


def recorte(nome):
    if nome.startswith('cap'):
        return (30, 20, 1100, 150)
    if nome.startswith('dest_'):
        return (1180, 110, 1880, 640)
    return RECORTE.get(nome)


def render(args):
    nome, corpo, tl = args
    from playwright.sync_api import sync_playwright
    pasta = os.path.join(SAIDA, nome)
    os.makedirs(pasta, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        pg = b.new_page(viewport={'width': 1920, 'height': 1080})
        pg.set_content(BASE.replace('__CORPO__', corpo).replace('__TL__', tl), wait_until='networkidle')
        pg.evaluate('document.fonts.ready')
        pg.wait_for_timeout(300)
        dur = pg.evaluate('window.DUR')
        n = int(round(dur * FPS))
        for i in range(n):
            pg.evaluate(f'window.seek({i / FPS})')
            c = recorte(nome)
            kw = {'clip': {'x': c[0], 'y': c[1], 'width': c[2] - c[0], 'height': c[3] - c[1]}} if c else {}
            pg.screenshot(path=os.path.join(pasta, 'f_%05d.png' % i), omit_background=True, **kw)
        json.dump({'x': (c or (0, 0))[0], 'y': (c or (0, 0))[1]}, open(os.path.join(pasta, 'pos.json'), 'w'))
        b.close()
    return nome, n


if __name__ == '__main__':
    pecas = catalogo()
    nomes = sys.argv[1:] or list(pecas)
    with ProcessPoolExecutor(3) as ex:
        for nome, n in ex.map(render, [(k, *pecas[k]) for k in nomes]):
            print(nome, n, 'quadros', flush=True)
