"""Kit de divulgação da Imersão IA para Marketplaces (BUCC Workspaces Pinheiros, 24/10).
Gera carrossel 4:5 (5 telas), story 9:16 e imagem horizontal 1200x628 a partir de HTML."""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
A = "file://" + os.path.join(HERE, "assets")
FONT = "file:///Users/itamar/git/gestao-redes-sociais/output/reel-explica-marketplace-connect/assets/Inter.ttf"

CSS = """
@font-face { font-family: Inter; src: url('%(font)s'); font-weight: 100 900; }
* { margin:0; padding:0; box-sizing:border-box; }
:root { --navy:#061a4d; --navy2:#0b2a72; --cyan:#25c4ea; --blue:#1d5fe0; --yellow:#f7c600; --green:#1fa64a; --ink:#0a1633; }
body { font-family: Inter, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; color:#fff; background: var(--navy); overflow:hidden; }
.abs { position:absolute; }
.photo { position:absolute; background-size:cover; background-repeat:no-repeat; }
.label { font-size:26px; font-weight:800; letter-spacing:.24em; text-transform:uppercase; color:var(--cyan); }
.title { font-weight:900; letter-spacing:-.045em; line-height:.95; text-transform:uppercase; }
.pill { display:inline-flex; align-items:center; gap:12px; border-radius:999px; padding:14px 26px; font-weight:800; font-size:28px; letter-spacing:.04em; white-space:nowrap; }
.p-white { background:#fff; color:var(--navy); }
.p-cyan { background:var(--cyan); color:var(--navy); }
.p-yellow { background:var(--yellow); color:var(--navy); }
.p-line { border:2px solid rgba(255,255,255,.35); color:#fff; font-weight:700; letter-spacing:0; }
.logo { position:absolute; background:#fff; border-radius:22px; padding:10px; box-shadow:0 14px 40px rgba(0,0,0,.35); }
.logo img { display:block; }
.br { display:flex; gap:8px; } .br i { display:block; height:8px; width:70px; border-radius:4px; }
.br .g { background:var(--green);} .br .y { background:var(--yellow);} .br .b { background:var(--blue);}
.glow { position:absolute; inset:0; background: radial-gradient(60%% 40%% at 80%% 15%%, rgba(37,196,234,.22), transparent 70%%), radial-gradient(50%% 35%% at 10%% 90%%, rgba(29,95,224,.35), transparent 70%%); }
""" % {"font": FONT}

def page(w, h, body):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS} body{{width:{w}px;height:{h}px;}}</style></head><body><div style='position:relative;width:{w}px;height:{h}px;overflow:hidden'>{body}</div></body></html>"

FACH = f"{A}/fachada.jpg"
SALA = f"{A}/bucc-unidade-pinheiros-sala-de-reuniao-skeleton.jpg"
AUD = f"{A}/bucc-unidade-pinheiros-treinamentos-e-workshops-01.jpg"
LOGO = f"{A}/logo_tiops.png"
ROSTO = f"{A}/itamar_rosto.jpg"

S1 = page(1080, 1350, f"""
<div class='photo' style='left:0;top:0;width:1080px;height:900px;background-image:url({FACH});background-position:58% 40%'></div>
<div class='abs' style='left:0;top:380px;width:1080px;height:560px;background:linear-gradient(180deg,rgba(6,26,77,0) 0%,rgba(6,26,77,.75) 55%,#061a4d 100%)'></div>
<div class='abs' style='left:0;top:900px;width:1080px;height:450px;background:#061a4d'></div>
<div class='logo' style='left:56px;top:56px'><img src='{LOGO}' style='width:150px'></div>
<div class='abs' style='right:56px;top:66px'><span class='pill p-yellow'>VAGAS LIMITADAS</span></div>
<div class='abs label' style='left:70px;top:735px'>Imersão presencial · Tiops</div>
<div class='abs title' style='left:64px;top:785px;font-size:118px'>IA para<br>marketplaces</div>
<div class='abs' style='left:70px;top:1035px;display:flex;gap:16px'><span class='pill p-white'>SÁB · 24 OUT · 9H–16H</span><span class='pill p-cyan'>BUCC · PINHEIROS</span></div>
<div class='abs' style='left:70px;top:1140px;display:flex;gap:14px;flex-wrap:wrap;width:960px'>
  <span class='pill p-line'>🤝 Networking com sellers</span><span class='pill p-line'>🤖 IA na prática com especialista</span></div>
<div class='abs br' style='left:70px;top:1285px'><i class='g'></i><i class='y'></i><i class='b'></i></div>
""")

S2 = page(1080, 1350, f"""
<div class='photo' style='left:0;top:0;width:1080px;height:760px;background-image:url({SALA});background-position:50% 60%'></div>
<div class='abs' style='left:0;top:560px;width:1080px;height:220px;background:linear-gradient(180deg,rgba(6,26,77,0),#061a4d)'></div>
<div class='glow' style='top:760px'></div>
<div class='abs' style='right:56px;top:600px;width:330px;height:220px;border-radius:22px;border:6px solid #fff;box-shadow:0 20px 50px rgba(0,0,0,.45);background:url({FACH}) 55% 45%/cover'></div>
<div class='abs label' style='left:70px;top:820px'>O lugar</div>
<div class='abs' style='left:68px;top:868px;font-size:70px;font-weight:900;letter-spacing:-.04em;line-height:1'>BUCC Workspaces,<br><span style='color:var(--cyan)'>em Pinheiros</span></div>
<div class='abs' style='left:70px;top:1050px;width:940px;font-size:34px;line-height:1.4;color:#dbe7ff;font-weight:500'>Um espaço elegante, a poucas quadras da Vila Madalena, para um dia inteiro de prática e conversa entre sellers.</div>
<div class='abs' style='left:70px;top:1215px'><span class='pill p-line' style='font-size:28px'>📍 Av. Pedroso de Morais, 2160 · São Paulo</span></div>
""")

def speaker(top, img_html, name, sub, tag):
    return f"""<div class='abs' style='left:60px;right:60px;top:{top}px;height:250px;border-radius:30px;background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.13);display:flex;align-items:center;gap:34px;padding:0 36px'>
      {img_html}
      <div><div style='font-size:22px;font-weight:800;letter-spacing:.2em;color:var(--cyan)'>{tag}</div>
      <div style='font-size:52px;font-weight:900;letter-spacing:-.03em;margin-top:6px'>{name}</div>
      <div style='font-size:29px;color:#dbe7ff;margin-top:8px;line-height:1.3;font-weight:500'>{sub}</div></div></div>"""

AV = "width:170px;height:170px;border-radius:50%;flex:none;border:5px solid var(--cyan);"
S3 = page(1080, 1350, f"""
<div class='glow'></div>
<div class='logo' style='right:56px;top:56px;padding:8px;border-radius:18px'><img src='{LOGO}' style='width:100px'></div>
<div class='abs label' style='left:70px;top:90px'>Quem vai estar lá</div>
<div class='abs' style='left:66px;top:140px;font-size:84px;font-weight:900;letter-spacing:-.045em;line-height:.98'>Gente que faz,<br><span style='color:var(--cyan)'>não só fala.</span></div>
{speaker(390, f"<div style='{AV}background:url({ROSTO}) center/cover'></div>", "Itamar Rocha", "Professor de IA na FIAP<br>Fundador da Tiops", "ESPECIALISTA EM IA")}
{speaker(670, f"<div style='{AV}background:linear-gradient(135deg,#1d5fe0,#25c4ea);display:grid;place-items:center;font-size:80px'>🚀</div>", "Empreendedor", "Bastidores de quem constrói<br>e faz um negócio crescer", "PALESTRANTE CONVIDADO")}
{speaker(950, f"<div style='{AV}background:linear-gradient(135deg,#f7c600,#ff9f1c);display:grid;place-items:center;font-size:80px'>🛒</div>", "Seller da Lucrei", "Cresceu junto com a Tiops<br>e conta como usa IA na operação", "CASE REAL")}
<div class='abs br' style='left:70px;top:1270px'><i class='g'></i><i class='y'></i><i class='b'></i></div>
""")

ITENS = ["Criar seus primeiros agentes de IA", "Aplicações reais para marketplaces", "Oportunidades de automação na sua operação",
         "Case real de um seller que cresceu com IA", "Networking com sellers e empreendedores"]
rows = "".join(f"""<div style='display:flex;align-items:center;gap:26px;padding:26px 0;border-top:2px solid #e3eaf7'>
  <span style='width:58px;height:58px;border-radius:50%;background:var(--green);color:#fff;display:grid;place-items:center;font-size:32px;font-weight:900;flex:none'>✓</span>
  <span style='font-size:40px;font-weight:700;letter-spacing:-.015em;color:var(--ink)'>{t}</span></div>""" for t in ITENS)
S4 = page(1080, 1350, f"""
<div class='abs' style='inset:0;background:radial-gradient(120% 80% at 50% 30%,#fff 0%,#eef4ff 60%,#d9e5fb 100%)'></div>
<div class='photo' style='left:0;top:0;width:1080px;height:330px;background-image:url({AUD});background-position:50% 55%'></div>
<div class='abs' style='left:0;top:150px;width:1080px;height:190px;background:linear-gradient(180deg,rgba(238,244,255,0),#f4f7ff)'></div>
<div class='abs label' style='left:70px;top:350px;color:#1aa0c6'>O que você vai viver</div>
<div class='abs' style='left:66px;top:398px;font-size:80px;font-weight:900;letter-spacing:-.045em;line-height:1;color:var(--navy)'>Um dia inteiro<br>de prática.</div>
<div class='abs' style='left:70px;right:70px;top:600px'>{rows}</div>
""")

S5 = page(1080, 1350, f"""
<div class='photo' style='inset:0;background-image:url({FACH});background-position:55% 50%;filter:saturate(1.05)'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(6,26,77,.55) 0%,rgba(6,26,77,.88) 45%,#061a4d 100%)'></div>
<div class='logo' style='left:50%;transform:translateX(-50%);top:70px'><img src='{LOGO}' style='width:150px'></div>
<div class='abs' style='left:0;right:0;top:330px;text-align:center'><span class='pill p-yellow' style='font-size:30px'>VAGAS LIMITADAS</span></div>
<div class='abs label' style='left:0;right:0;top:440px;text-align:center;font-size:30px'>Sábado</div>
<div class='abs' style='left:0;right:0;top:480px;text-align:center;font-size:260px;font-weight:900;letter-spacing:-.06em;line-height:1;background:linear-gradient(180deg,#fff,#9fe6f7);-webkit-background-clip:text;color:transparent'>24.10</div>
<div class='abs' style='left:0;right:0;top:760px;text-align:center;font-size:48px;font-weight:800'>9h às 16h</div>
<div class='abs' style='left:340px;width:400px;top:850px;height:3px;background:rgba(255,255,255,.25)'></div>
<div class='abs' style='left:0;right:0;top:890px;text-align:center;font-size:40px;font-weight:800'>BUCC Workspaces · Pinheiros</div>
<div class='abs' style='left:0;right:0;top:945px;text-align:center;font-size:30px;color:#dbe7ff'>Av. Pedroso de Morais, 2160 · São Paulo</div>
<div class='abs' style='left:0;right:0;top:1060px;text-align:center'><span class='pill p-white' style='font-size:36px;padding:22px 40px'>Inscrições: l.tiops.com.br/imersao</span></div>
<div class='abs' style='left:0;right:0;top:1180px;text-align:center;font-size:28px;color:rgba(219,231,255,.75);font-weight:600'>Link na bio · Imersão IA para Marketplaces</div>
""")

STORY = page(1080, 1920, f"""
<div class='photo' style='left:0;top:0;width:1080px;height:1150px;background-image:url({FACH});background-position:57% 45%'></div>
<div class='abs' style='left:0;top:600px;width:1080px;height:560px;background:linear-gradient(180deg,rgba(6,26,77,0) 0%,rgba(6,26,77,.8) 60%,#061a4d 100%)'></div>
<div class='abs' style='left:0;top:1150px;width:1080px;height:770px;background:#061a4d'></div>
<div class='logo' style='left:60px;top:230px'><img src='{LOGO}' style='width:150px'></div>
<div class='abs' style='right:60px;top:240px'><span class='pill p-yellow'>VAGAS LIMITADAS</span></div>
<div class='abs label' style='left:70px;top:900px'>Imersão presencial · Tiops</div>
<div class='abs title' style='left:64px;top:950px;font-size:128px'>IA para<br>marketplaces</div>
<div class='abs' style='left:70px;top:1215px;display:flex;gap:16px;flex-wrap:wrap;width:950px'><span class='pill p-white'>SÁB · 24 OUT · 9H–16H</span><span class='pill p-cyan'>BUCC · PINHEIROS</span></div>
<div class='abs' style='left:70px;top:1320px;display:flex;flex-direction:column;gap:14px'>
  <span class='pill p-line' style='align-self:flex-start'>🤝 Networking com sellers</span>
  <span class='pill p-line' style='align-self:flex-start'>🤖 IA na prática com especialista</span>
  <span class='pill p-line' style='align-self:flex-start'>🛒 Case real de seller + palestra com empreendedor</span></div>
<div class='abs' style='left:0;right:0;top:1580px;text-align:center;font-size:32px;font-weight:700;color:#dbe7ff'>Toque no link para garantir sua vaga ↓</div>
""")

WIDE = page(1200, 628, f"""
<div class='photo' style='left:0;top:0;width:690px;height:628px;background-image:url({FACH});background-position:55% 50%'></div>
<div class='abs' style='left:520px;top:0;width:200px;height:628px;background:linear-gradient(90deg,rgba(6,26,77,0),#061a4d)'></div>
<div class='abs' style='left:690px;top:0;width:510px;height:628px;background:#061a4d'></div>
<div class='logo' style='left:36px;top:36px;padding:6px;border-radius:14px'><img src='{LOGO}' style='width:96px'></div>
<div class='abs label' style='left:720px;top:70px;font-size:18px'>Imersão presencial</div>
<div class='abs title' style='left:716px;top:104px;font-size:60px'>IA para<br>marketplaces</div>
<div class='abs' style='left:720px;top:250px;font-size:30px;font-weight:800'>Sábado, 24/10 · 9h às 16h</div>
<div class='abs' style='left:720px;top:296px;font-size:24px;color:#dbe7ff;line-height:1.35'>BUCC Workspaces · Pinheiros<br>Av. Pedroso de Morais, 2160</div>
<div class='abs' style='left:720px;top:400px;font-size:22px;color:#dbe7ff;line-height:1.5'>🤝 Networking com sellers<br>🤖 IA na prática com especialista<br>🛒 Case real + palestra com empreendedor</div>
<div class='abs' style='left:720px;top:530px'><span class='pill p-yellow' style='font-size:22px;padding:10px 20px'>l.tiops.com.br/imersao</span></div>
""")


WHATS = page(1080, 1080, f"""
<div class='photo' style='left:0;top:0;width:1080px;height:560px;background-image:url({FACH});background-position:57% 42%'></div>
<div class='abs' style='left:0;top:300px;width:1080px;height:280px;background:linear-gradient(180deg,rgba(6,26,77,0),#061a4d)'></div>
<div class='abs' style='left:0;top:560px;width:1080px;height:520px;background:#061a4d'></div>
<div class='logo' style='left:44px;top:44px;padding:8px;border-radius:18px'><img src='{LOGO}' style='width:118px'></div>
<div class='abs' style='right:44px;top:52px'><span class='pill p-yellow' style='font-size:26px'>VAGAS LIMITADAS</span></div>
<div class='abs label' style='left:60px;top:470px;font-size:24px'>Imersão presencial · Tiops</div>
<div class='abs title' style='left:56px;top:512px;font-size:104px'>IA para<br>marketplaces</div>
<div class='abs' style='left:60px;top:735px;display:flex;gap:14px'><span class='pill p-white' style='font-size:30px'>SÁBADO · 24/10 · 9H ÀS 16H</span></div>
<div class='abs' style='left:60px;top:815px;font-size:32px;font-weight:700'>📍 BUCC Workspaces · Pinheiros, SP</div>
<div class='abs' style='left:60px;top:870px;font-size:28px;color:#dbe7ff;line-height:1.45;font-weight:500'>Agentes de IA na prática · case real de seller · networking</div>
<div class='abs' style='left:60px;top:950px'><span class='pill p-cyan' style='font-size:32px;padding:16px 30px'>Inscrições: l.tiops.com.br/imersao</span></div>
""")

PIECES = [("whatsapp_1x1.jpg", 1080, 1080, WHATS), ("carrossel_1_capa.jpg", 1080, 1350, S1), ("carrossel_2_lugar.jpg", 1080, 1350, S2), ("carrossel_3_quem.jpg", 1080, 1350, S3),
          ("carrossel_4_programa.jpg", 1080, 1350, S4), ("carrossel_5_inscricao.jpg", 1080, 1350, S5),
          ("story_9x16.jpg", 1080, 1920, STORY), ("horizontal_1200x628.jpg", 1200, 628, WIDE)]

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "pecas"), exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for fn, w, h, html in PIECES:
            path = os.path.join(HERE, "build", fn.replace(".jpg", ".html"))
            open(path, "w").write(html)
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg.goto("file://" + path); pg.wait_for_timeout(700)
            pg.screenshot(path=os.path.join(HERE, "pecas", fn), type="jpeg", quality=93)
            pg.close()
        b.close()
    print("ok")
