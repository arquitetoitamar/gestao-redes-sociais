#!/usr/bin/env python3
"""Carrossel "Claude dentro do Mercado Livre" (8 slides 1080x1350) para o @tiopstecnologia.

Formato inspirado no carrossel do @ignaciooleo (capa + o que faz + CTA "comenta PALAVRA"),
com texto e visual próprios, em português e sobre o que o Marketplace Connect faz de fato.

  python3 gera.py          gera html/slide-XX.html e slides/slide-XX.png + sheet.png
"""
import os
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(AQUI, 'html')
OUT = os.path.join(AQUI, 'slides')
TOTAL = 8

CSS = """
:root{--ink:#14161F;--cinza:#5B6170;--ml:#FFE600;--mlazul:#2D3277;--claude:#D97757;--verde:#18A957;--creme:#FFF8E8}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:-apple-system,"SF Pro Display","Helvetica Neue",Arial,sans-serif;color:var(--ink);
 background:radial-gradient(1100px 900px at 75% 18%,#FFF1C2 0%,rgba(255,241,194,0) 60%),var(--creme);
 padding:84px 76px 0;display:flex;flex-direction:column;position:relative}
.cont{position:absolute;top:44px;right:60px;font-size:24px;font-weight:800;color:#9AA0AC;letter-spacing:1px}
.cont b{color:var(--claude)}
h1{font-size:84px;font-weight:900;line-height:1.03;letter-spacing:-2.5px}
h1.m{font-size:76px}
.hl{background:linear-gradient(transparent 10%,var(--ml) 10%,var(--ml) 90%,transparent 90%);padding:0 10px;border-radius:12px;
 -webkit-box-decoration-break:clone;box-decoration-break:clone}
.sub{font-size:36px;line-height:1.3;font-weight:600;color:#2A2E3A;margin-top:26px}
.sp{flex:1}
.card{background:#fff;border-radius:30px;box-shadow:0 14px 40px rgba(60,40,0,.10);padding:34px 38px}
.rod{height:96px;margin:0 -76px;padding:0 60px;display:flex;align-items:center;gap:16px;font-size:24px;font-weight:800;color:var(--cinza)}
.rod img{height:50px}
.rod .dir{margin-left:auto;color:var(--ink)}
.tag{display:inline-block;background:#F2443A;color:#fff;font-weight:900;font-size:28px;letter-spacing:2px;padding:12px 30px;border-radius:999px;margin-bottom:30px}
.bolha{background:#fff;border-radius:28px 28px 28px 8px;padding:24px 30px;font-size:30px;font-weight:600;box-shadow:0 10px 30px rgba(60,40,0,.10);display:inline-block}
.bolha.eu{background:var(--ink);color:#fff;border-radius:28px 28px 8px 28px}
.ck{display:flex;align-items:center;gap:18px;font-size:36px;font-weight:700;margin:18px 0}
.ck i{width:48px;height:48px;border-radius:50%;background:var(--verde);display:inline-flex;align-items:center;justify-content:center;flex:none}
.ck i:after{content:"";width:14px;height:8px;border:4px solid #fff;border-top:0;border-right:0;transform:rotate(-45deg) translate(1px,-2px)}
.chip{display:inline-flex;align-items:center;gap:12px;background:#fff;border-radius:999px;padding:20px 30px;font-size:32px;font-weight:800;box-shadow:0 6px 18px rgba(60,40,0,.08)}
.logo-ml{width:200px;height:auto;border-radius:34px;box-shadow:0 16px 40px rgba(200,170,0,.35)}
.logo-cl{width:200px;height:200px;border-radius:44px;object-fit:cover;box-shadow:0 16px 40px rgba(217,119,87,.35)}
.rodape-txt{font-size:34px;font-weight:800;text-align:center;line-height:1.3;margin:26px 0 8px}
.raio{position:absolute;width:46px;height:9px;border-radius:9px;background:var(--claude);opacity:.9}
"""

RAIOS = """<div class='raio' style='top:205px;left:40px;transform:rotate(30deg)'></div>
<div class='raio' style='top:250px;left:28px;transform:rotate(0deg)'></div>
<div class='raio' style='top:170px;right:70px;transform:rotate(-35deg)'></div>"""


def rodape(n):
    return (f"<div class='rod'><img src='../assets/tiops-robo.png'>@tiopstecnologia"
            f"<span class='dir'>{'Deslize para ver mais →' if n == 1 else 'Marketplace Connect'}</span></div>")


def pagina(n, corpo):
    cont = '' if n == 1 else f"<div class='cont'><b>{n:02d}</b> / {TOTAL:02d}</div>"
    return (f"<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body>{cont}{corpo}{rodape(n)}</body></html>")


S = {}

S[1] = f"""{RAIOS}
<div style='text-align:center'><span class='tag'>NOVIDADE</span></div>
<h1 style='text-align:center'>Coloquei o Claude <span class='hl'>dentro do meu</span> Mercado Livre.</h1>
<p class='sub' style='text-align:center'>Ele lê vendas, anúncios e concorrentes.<br>E faz o trabalho chato junto com você.</p>
<div class='sp'></div>
<div style='position:relative;height:420px;display:flex;align-items:center;justify-content:center;gap:56px'>
  <div style='position:absolute;width:520px;height:520px;border-radius:50%;background:radial-gradient(circle,#FFE36E 0%,rgba(255,227,110,0) 70%)'></div>
  <img class='logo-cl' src='../assets/claude.png' style='position:relative;transform:rotate(-8deg)'>
  <div style='position:relative;font-size:110px;font-weight:900;color:var(--ink)'>+</div>
  <img class='logo-ml' src='../assets/ml.png' style='position:relative;transform:rotate(8deg)'>
</div>
<div style='text-align:center;margin-bottom:34px'><span class='bolha eu'>“Quais anúncios vão ficar sem estoque esta semana?”</span></div>
"""

S[2] = """
<h1 class='m'>Você pergunta em português. <span class='hl'>Ele responde com os seus números.</span></h1>
<div class='sp'></div>
<div style='text-align:right'><span class='bolha eu' style='font-size:34px'>Quais foram meus 5 mais vendidos em outubro?</span></div>
<div style='height:22px'></div>
<div class='card'>
  <div style='display:flex;align-items:center;gap:16px;margin-bottom:18px'>
    <img src='../assets/claude.png' style='width:64px;height:64px;border-radius:16px'>
    <b style='font-size:36px'>Seus mais vendidos</b>
    <img src='../assets/ml.png' style='height:72px;margin-left:auto;border-radius:14px'>
  </div>
  <div style='display:grid;grid-template-columns:56px 86px 1fr 250px;row-gap:28px;align-items:center;font-size:36px;font-weight:700'>
    <span>1</span><span style='font-size:44px'>🎧</span><span>Fone sem fio</span><div style='height:22px;border-radius:11px;background:var(--ml);width:100%'></div>
    <span>2</span><span style='font-size:44px'>🍟</span><span>Fritadeira elétrica</span><div style='height:22px;border-radius:11px;background:var(--ml);width:82%'></div>
    <span>3</span><span style='font-size:44px'>👟</span><span>Tênis de corrida</span><div style='height:22px;border-radius:11px;background:var(--ml);width:68%'></div>
    <span>4</span><span style='font-size:44px'>🥤</span><span>Garrafa térmica</span><div style='height:22px;border-radius:11px;background:var(--ml);width:55%'></div>
    <span>5</span><span style='font-size:44px'>⌚</span><span>Relógio inteligente</span><div style='height:22px;border-radius:11px;background:var(--ml);width:41%'></div>
  </div>
</div>
<div class='sp'></div>
<p class='rodape-txt'>Vendas, visitas, pedidos e anúncios<br><span class='hl'>numa conversa só.</span></p>
"""

S[3] = """
<h1 class='m'>Mostra quanto <span class='hl'>sobra de verdade</span> em cada venda.</h1>
<div class='sp'></div>
<div class='card'>
  <div style='font-size:32px;font-weight:800;color:var(--cinza);margin-bottom:28px'>De onde sai o dinheiro de uma venda</div>
  <div style='display:grid;grid-template-columns:370px 1fr;row-gap:30px;align-items:center;font-size:34px;font-weight:700'>
    <span>Preço de venda</span><div style='height:40px;border-radius:12px;background:var(--mlazul);width:100%'></div>
    <span>Tarifa do Mercado Livre</span><div style='height:40px;border-radius:12px;background:#F2443A;width:24%;margin-left:0'></div>
    <span>Frete</span><div style='height:40px;border-radius:12px;background:#F2443A;width:14%'></div>
    <span>Imposto</span><div style='height:40px;border-radius:12px;background:#F2443A;width:10%'></div>
    <span>Custo do produto</span><div style='height:40px;border-radius:12px;background:#F2443A;width:30%'></div>
    <b style='font-size:38px;color:var(--verde)'>O que sobra</b><div style='height:40px;border-radius:12px;background:var(--verde);width:22%'></div>
  </div>
</div>
<div style='height:30px'></div>
<div style='display:flex;gap:18px;justify-content:center'>
  <span class='chip'>📦 Por produto</span><span class='chip'>🧾 Por pedido</span><span class='chip'>📅 Por período</span>
</div>
<div class='sp'></div>
<p class='rodape-txt' style='font-size:30px;font-weight:700;color:var(--cinza)'>Com o custo do produto cadastrado, a conta fecha sozinha.</p>
"""

S[4] = """
<h1 class='m'>Olha a <span class='hl'>concorrência</span> por você.</h1>
<div class='sp'></div>
<div class='card' style='padding:36px 34px'>
  <div style='display:grid;grid-template-columns:240px 1fr 1fr 1fr;gap:34px 14px;align-items:center;font-size:32px;font-weight:700;text-align:center'>
    <span></span><b style='background:var(--ml);border-radius:14px;padding:10px'>Você</b><b style='color:var(--cinza)'>Loja A</b><b style='color:var(--cinza)'>Loja B</b>
    <span style='text-align:left'>💲 Preço</span><span>Acima</span><span>Mais barato</span><span>Na média</span>
    <span style='text-align:left'>📝 Anúncio</span><span>3 fotos</span><span>Título completo</span><span>8 fotos</span>
    <span style='text-align:left'>⭐ Avaliações</span><span>★★★★☆</span><span>★★★★★</span><span>★★★☆☆</span>
  </div>
</div>
<div style='height:44px'></div>
<div class='ck'><i></i>Onde o seu preço está fora do mercado</div>
<div class='ck'><i></i>Que tipo de anúncio vende mais na categoria</div>
<div class='ck'><i></i>O que os compradores elogiam e reclamam</div>
<div class='sp'></div>
<p class='rodape-txt'>E aponta <span class='hl'>onde você está perdendo venda.</span></p>
"""

S[5] = """
<h1 class='m'>Ajusta preço, estoque e anúncio <span class='hl'>em lote.</span></h1>
<div class='sp'></div>
<div style='display:flex;flex-wrap:wrap;gap:16px'>
  <span class='chip'>💲 Preço</span><span class='chip'>📦 Estoque</span><span class='chip'>📝 Título e descrição</span>
  <span class='chip'>🖼️ Fotos</span><span class='chip'>🏷️ Promoções</span>
</div>
<div style='height:34px'></div>
<div class='card' style='padding:28px 34px'>
  <div style='display:grid;grid-template-columns:80px 1fr 270px;row-gap:28px;align-items:center;font-size:34px;font-weight:700'>
    <span style='font-size:42px'>🎧</span><span>Fone sem fio · preço</span><span style='color:var(--verde)'>✓ aprovado</span>
    <span style='font-size:42px'>🍟</span><span>Fritadeira · estoque</span><span style='color:var(--verde)'>✓ aprovado</span>
    <span style='font-size:42px'>👟</span><span>Tênis · título</span><span style='color:var(--verde)'>✓ aprovado</span>
    <span style='font-size:42px'>🥤</span><span>Garrafa · promoção</span><span style='color:#C77A00'>aguardando você</span>
  </div>
</div>
<div class='sp'></div>
<div class='card' style='background:var(--ink);color:#fff;text-align:center;margin-bottom:34px'>
  <div style='font-size:34px;font-weight:800;line-height:1.3'>Antes de mudar qualquer coisa,<br>ele te mostra e <span style='color:var(--ml)'>espera o seu OK.</span></div>
</div>
"""

S[6] = """
<h1 class='m'>Funciona no Claude e no ChatGPT. <span class='hl'>Sem código.</span></h1>
<div class='sp'></div>
<div style='display:flex;gap:40px;align-items:center;justify-content:center'>
  <img src='../assets/claude.png' style='width:150px;height:150px;border-radius:36px'>
  <img src='../assets/chatgpt.png' style='height:110px'>
</div>
<div style='height:38px'></div>
<div class='card' style='padding:30px 36px'>
  <div style='display:grid;grid-template-columns:90px 1fr;row-gap:40px;align-items:center'>
    <b style='width:72px;height:72px;border-radius:50%;background:var(--ml);display:flex;align-items:center;justify-content:center;font-size:38px'>1</b>
    <div><b style='font-size:40px'>Autorize a sua conta</b><div style='font-size:31px;color:var(--cinza);margin-top:6px'>Login oficial do Mercado Livre, um clique.</div></div>
    <b style='width:72px;height:72px;border-radius:50%;background:var(--ml);display:flex;align-items:center;justify-content:center;font-size:38px'>2</b>
    <div><b style='font-size:40px'>Cole o conector</b><div style='font-size:31px;color:var(--cinza);margin-top:6px'>No Claude ou no ChatGPT, em Conectores.</div></div>
    <b style='width:72px;height:72px;border-radius:50%;background:var(--ml);display:flex;align-items:center;justify-content:center;font-size:38px'>3</b>
    <div><b style='font-size:40px'>Peça em português</b><div style='font-size:31px;color:var(--cinza);margin-top:6px'>“Me mostra o que vendeu mais esta semana.”</div></div>
  </div>
</div>
<div class='sp'></div>
<p class='rodape-txt'>Uns <span class='hl'>2 minutos</span> por loja.</p>
"""

S[7] = """
<h1 class='m'>E não é só o <span class='hl'>Mercado Livre.</span></h1>
<p class='sub'>A mesma conversa cuida das suas outras lojas e do seu ERP.</p>
<div class='sp'></div>
<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:22px'>
  <div class='card' style='display:flex;align-items:center;justify-content:center;height:250px'><img src='../assets/ml.png' style='height:170px;border-radius:20px'></div>
  <div class='card' style='display:flex;align-items:center;justify-content:center;height:250px'><img src='../assets/shopee.png' style='height:160px'></div>
  <div class='card' style='display:flex;align-items:center;justify-content:center;height:250px'><img src='../assets/amazon.png' style='height:130px'></div>
</div>
<div style='height:26px'></div>
<div style='display:flex;flex-wrap:wrap;gap:16px;justify-content:center'>
  <span class='chip'>TikTok Shop</span><span class='chip'>Magalu</span><span class='chip'>Shein</span>
  <span class='chip'>Bling</span><span class='chip'>Olist</span>
</div>
<div class='sp'></div>
<p class='rodape-txt'>Um lugar só para <span class='hl'>perguntar e agir.</span></p>
"""

S[8] = f"""{RAIOS}
<h1 class='m' style='text-align:center'>Quer o link e o <span class='hl'>passo a passo?</span></h1>
<div class='sp'></div>
<div style='position:relative;background:var(--ml);border-radius:60px;padding:56px 40px 60px;text-align:center;box-shadow:0 20px 50px rgba(200,170,0,.35)'>
  <div style='display:inline-block;background:var(--ink);color:#fff;font-size:46px;font-weight:900;padding:12px 40px;border-radius:999px'>Comenta</div>
  <div style='font-size:230px;font-weight:900;letter-spacing:-6px;line-height:1;margin:18px 0 6px'>MELI</div>
  <div style='font-size:44px;font-weight:800'>que eu te mando no direct.</div>
  <div style='position:absolute;left:90px;bottom:-34px;width:0;height:0;border-left:40px solid transparent;border-right:40px solid transparent;border-top:44px solid var(--ml)'></div>
</div>
<div class='sp'></div>
<div style='display:flex;gap:30px;align-items:center;justify-content:center;margin-bottom:30px'>
  <img src='../assets/claude.png' style='width:96px;height:96px;border-radius:24px'>
  <span style='font-size:60px;font-weight:900'>+</span>
  <img src='../assets/ml.png' style='height:96px;border-radius:18px'>
</div>
"""


def main():
    os.makedirs(HTML, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    for n, corpo in S.items():
        open(os.path.join(HTML, f'slide-{n:02d}.html'), 'w').write(pagina(n, corpo))
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for n in S:
            pg.goto('file://' + os.path.join(HTML, f'slide-{n:02d}.html'))
            pg.wait_for_timeout(300)
            pg.screenshot(path=os.path.join(OUT, f'slide-{n:02d}.png'))
        b.close()
    from PIL import Image
    ims = [Image.open(os.path.join(OUT, f'slide-{n:02d}.png')).convert('RGB') for n in S]
    w, h = 360, 450
    sheet = Image.new('RGB', (w * 4 + 50, h * 2 + 30), (40, 40, 40))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((w, h)), (10 + (i % 4) * (w + 10), 10 + (i // 4) * (h + 10)))
    sheet.save(os.path.join(AQUI, 'sheet.png'))
    print('ok', len(ims), 'slides')


if __name__ == '__main__':
    main()
