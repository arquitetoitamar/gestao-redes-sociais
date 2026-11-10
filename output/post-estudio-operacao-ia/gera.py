#!/usr/bin/env python3
"""Carrossel "Estúdio de Operação com IA" (6 slides 1080x1350) para o @tiopstecnologia.

Base: imagem enviada pelo Itamar em 10/11/2026 (original.webp). Em original-corrigida.png:
"Gerendo" virou "Gerando" e saiu a nota "4,8 (2.341 avaliações)" do anúncio de exemplo
(número inventado num anúncio recém-publicado). Os recortes dos painéis ficam em assets/.

  python3 gera.py          gera html/, slides/ (PNG), slides-jpg/ (para o agendador) e sheet.png
"""
import os
from PIL import Image
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
HTML, OUT, JPG = (os.path.join(AQUI, d) for d in ('html', 'slides', 'slides-jpg'))
TOTAL = 6

CSS = """
:root{--bg:#060B1C;--azul:#1F6BFF;--ciano:#3CCBFF;--verde:#22C55E;--cinza:#9AA7C2;--card:#0F1A36}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:-apple-system,"SF Pro Display","Helvetica Neue",Arial,sans-serif;color:#fff;
 background:radial-gradient(900px 700px at 85% 8%,rgba(31,107,255,.40) 0%,rgba(31,107,255,0) 65%),
            radial-gradient(800px 600px at 0% 100%,rgba(60,203,255,.16) 0%,rgba(60,203,255,0) 60%),var(--bg);
 padding:84px 72px 0;display:flex;flex-direction:column;position:relative}
.cont{position:absolute;top:44px;right:60px;font-size:24px;font-weight:800;color:#5E6B8A;letter-spacing:1px}
.cont b{color:var(--ciano)}
h1{font-size:80px;font-weight:900;line-height:1.04;letter-spacing:-2.4px}
h1.m{font-size:70px}
.hl{color:var(--ciano)}
.sub{font-size:34px;line-height:1.32;font-weight:600;color:#C9D3EA;margin-top:24px}
.sp{flex:1}
.tag{display:inline-block;border:2px solid var(--ciano);color:var(--ciano);font-weight:900;font-size:24px;letter-spacing:3px;
 padding:12px 26px;border-radius:999px;margin-bottom:30px}
.passo{display:inline-flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:18px;background:var(--azul);
 font-size:38px;font-weight:900;margin-bottom:26px;box-shadow:0 0 40px rgba(31,107,255,.6)}
.foto{display:block;margin:0 auto;border-radius:28px;border:2px solid rgba(60,203,255,.45);
 box-shadow:0 0 0 8px rgba(60,203,255,.06),0 30px 70px rgba(0,0,0,.55),0 0 80px rgba(31,107,255,.35)}
.rod{height:96px;margin:0 -72px;padding:0 60px;display:flex;align-items:center;gap:16px;font-size:24px;font-weight:800;color:var(--cinza)}
.rod img{height:50px}
.rod .dir{margin-left:auto;color:#fff}
.rodape-txt{font-size:36px;font-weight:800;text-align:center;line-height:1.3;margin:30px 0 10px}
.pr{display:grid;grid-template-columns:76px 1fr;gap:22px;align-items:center;background:var(--card);border:1px solid rgba(60,203,255,.18);
 border-radius:26px;padding:30px 30px;margin-bottom:22px}
.pr b.n{width:64px;height:64px;border-radius:50%;background:var(--azul);display:flex;align-items:center;justify-content:center;font-size:34px}
.pr .t{font-size:38px;font-weight:800;line-height:1.15}
.pr .d{font-size:30px;color:var(--cinza);margin-top:8px;line-height:1.3;font-weight:600}
.chip{display:inline-flex;align-items:center;gap:14px;background:var(--card);border:1px solid rgba(60,203,255,.25);border-radius:999px;
 padding:16px 28px;font-size:30px;font-weight:800}
.chip img{height:44px;width:44px;border-radius:10px}
"""


def rodape(n):
    return (f"<div class='rod'><img src='../assets/tiops-robo.png'>@tiopstecnologia"
            f"<span class='dir'>{'Deslize para ver →' if n == 1 else 'Marketplace Connect'}</span></div>")


def pagina(n, corpo):
    cont = '' if n == 1 else f"<div class='cont'><b>{n:02d}</b> / {TOTAL:02d}</div>"
    return (f"<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body>{cont}{corpo}{rodape(n)}</body></html>")


S = {}

S[1] = """
<div style='text-align:center'><span class='tag'>ESTÚDIO DE OPERAÇÃO COM IA</span></div>
<h1 style='text-align:center'>Do pedido em português ao <span class='hl'>anúncio publicado.</span></h1>
<p class='sub' style='text-align:center'>A IA prepara. Você revisa.<br>O Marketplace Connect publica.</p>
<div class='sp'></div>
<img class='foto' src='../assets/inteira.png' style='width:1000px;margin:0 -32px'>
<div class='sp'></div>
"""

S[2] = """
<span class='passo'>1</span>
<h1 class='m'>Você pede. <span class='hl'>A IA prepara.</span></h1>
<p class='sub'>No ChatGPT, no Claude ou no Copiloto.</p>
<div class='sp'></div>
<img class='foto' src='../assets/esq.png' style='width:800px'>
<div class='sp'></div>
<p class='rodape-txt'>Título, descrição, atributos, preço e imagens<br><span class='hl'>num pedido só.</span></p>
"""

S[3] = """
<span class='passo'>2</span>
<h1 class='m'>O Marketplace Connect <span class='hl'>confere tudo.</span></h1>
<div class='sp'></div>
<img class='foto' src='../assets/meio.png' style='width:610px'>
<div class='sp'></div>
<p class='rodape-txt'>Catálogo, ficha técnica, preço, estoque<br>e as <span class='hl'>regras de cada canal.</span></p>
"""

S[4] = """
<span class='passo'>3</span>
<h1 class='m'>Você revisa.<br><span class='hl'>O anúncio vai ao ar.</span></h1>
<div class='sp'></div>
<img class='foto' src='../assets/dir.png' style='width:610px'>
<div class='sp'></div>
<p class='rodape-txt'>Mercado Livre, Shopee, TikTok Shop,<br>Amazon, Magalu <span class='hl'>e outros canais.</span></p>
"""

S[5] = """
<h1 class='m'>5 boas práticas de<br><span class='hl'>IA no marketplace</span></h1>
<div style='height:34px'></div>
<div class='pr'><b class='n'>1</b><div><div class='t'>Siga as regras de cada canal</div><div class='d'>Título, descrição, imagens, atributos e políticas.</div></div></div>
<div class='pr'><b class='n'>2</b><div><div class='t'>Informação verdadeira, sem exagero</div><div class='d'>Nada de promessa que o produto não cumpre.</div></div></div>
<div class='pr'><b class='n'>3</b><div><div class='t'>Respeite a propriedade intelectual</div><div class='d'>Só imagem, marca e conteúdo autorizados.</div></div></div>
<div class='pr'><b class='n'>4</b><div><div class='t'>A IA prepara, você revisa</div><div class='d'>Validação humana antes de publicar.</div></div></div>
<div class='pr'><b class='n'>5</b><div><div class='t'>Acompanhe e ajuste sempre</div><div class='d'>Preço, estoque, concorrência e reputação.</div></div></div>
<div class='sp'></div>
<p class='rodape-txt' style='margin-top:0'>📌 Salva para consultar depois.</p>
"""

S[6] = """
<h1 style='text-align:center'>Quer montar o seu <span class='hl'>estúdio de operação?</span></h1>
<div class='sp'></div>
<div style='text-align:center;background:linear-gradient(135deg,#1F6BFF,#0B3FB8);border-radius:36px;padding:56px 40px;
 box-shadow:0 0 90px rgba(31,107,255,.55)'>
  <div style='font-size:44px;font-weight:800'>Comenta</div>
  <div style='font-size:150px;font-weight:900;letter-spacing:4px;line-height:1.1'>CONNECT</div>
  <div style='font-size:38px;font-weight:700;line-height:1.3;margin-top:10px'>que eu te mando o link<br>e o passo a passo no direct.</div>
</div>
<div style='height:44px'></div>
<div style='display:flex;gap:18px;justify-content:center'>
  <span class='chip'><img src='../assets/ic-chatgpt.png'>ChatGPT</span>
  <span class='chip'><img src='../assets/ic-claude.png'>Claude</span>
</div>
<div class='sp'></div>
<p class='rodape-txt' style='color:var(--cinza);font-size:30px'>Saiba mais em marketplaces.tiops.com.br</p>
"""


def main():
    for d in (HTML, OUT, JPG):
        os.makedirs(d, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for n in range(1, TOTAL + 1):
            arq = os.path.join(HTML, f'slide-{n:02d}.html')
            open(arq, 'w').write(pagina(n, S[n]))
            pg.goto('file://' + arq)
            pg.wait_for_timeout(250)
            png = os.path.join(OUT, f'slide-{n:02d}.png')
            pg.screenshot(path=png)
            Image.open(png).convert('RGB').save(os.path.join(JPG, f'slide-{n:02d}.jpg'), quality=93)
        b.close()
    # folha de contato para revisar
    ims = [Image.open(os.path.join(OUT, f'slide-{n:02d}.png')).resize((360, 450)) for n in range(1, TOTAL + 1)]
    sheet = Image.new('RGB', (360 * 3 + 40, 450 * 2 + 30), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im, (10 + (i % 3) * 370, 10 + (i // 3) * 460))
    sheet.save(os.path.join(AQUI, 'sheet.png'))
    print('ok', TOTAL, 'slides')


if __name__ == '__main__':
    main()
