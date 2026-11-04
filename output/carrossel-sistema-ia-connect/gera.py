#!/usr/bin/env python3
"""Carrossel "Monte seu sistema de IA para marketplace" (10 slides 1080x1350) para o @tiopstecnologia.

Pedido do Itamar em 04/11/2026: um post no formato do carrossel do @ignaciooleo ("Armá tu sistema de IA
para Mercado Libre"), adaptado ao Marketplace Connect, em português e com identidade própria.
Identidade daqui: planta de engenharia (azul-marinho, grade técnica, rótulos em fonte mono), não o papel
bege com fita adesiva do original.

  python3 gera.py          gera html/, slides/ (PNG), slides-jpg/ (JPEG para o Instagram) e sheet.png
"""
import os
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(AQUI, 'html')
OUT = os.path.join(AQUI, 'slides')
JPG = os.path.join(AQUI, 'slides-jpg')
TOTAL = 10

CSS = """
:root{--bg:#0B1D33;--bg2:#10294A;--linha:rgba(120,190,255,.10);--ciano:#6CC6FF;--ml:#FFE600;--claude:#E58A66;
 --verde:#3DDC84;--branco:#F4F7FB;--cinza:#9FB0C6;--ink:#0B1D33}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:-apple-system,"SF Pro Display","Helvetica Neue",Arial,sans-serif;color:var(--branco);
 background:
  linear-gradient(var(--linha) 1px,transparent 1px) 0 0/54px 54px,
  linear-gradient(90deg,var(--linha) 1px,transparent 1px) 0 0/54px 54px,
  radial-gradient(900px 700px at 80% 10%,#16406E 0%,rgba(22,64,110,0) 70%),var(--bg);
 padding:120px 72px 0;display:flex;flex-direction:column;position:relative}
.mono{font-family:"SF Mono",Menlo,Consolas,monospace}
.topo{position:absolute;top:44px;left:72px;right:72px;display:flex;align-items:center;justify-content:space-between;
 font-family:"SF Mono",Menlo,monospace;font-size:22px;letter-spacing:3px;color:var(--ciano);font-weight:600}
.topo .n{color:var(--branco)} .topo .n b{color:var(--ml)}
.topo:after{content:"";position:absolute;left:0;right:0;bottom:-16px;height:1px;background:rgba(108,198,255,.35)}
.etq{display:inline-block;font-family:"SF Mono",Menlo,monospace;font-size:24px;font-weight:700;letter-spacing:3px;color:var(--ink);
 background:var(--ciano);padding:10px 22px;border-radius:8px;margin-bottom:26px}
h1{font-size:86px;font-weight:900;line-height:1.02;letter-spacing:-2.5px}
h1.m{font-size:78px}
.y{color:var(--ml)}
.c{color:var(--claude)}
.sub{font-size:34px;line-height:1.32;font-weight:500;color:#D5DEEA;margin-top:24px}
.sp{flex:1}
.caixa{border:2px solid rgba(108,198,255,.45);background:rgba(16,41,74,.75);border-radius:22px;position:relative}
.caixa:before,.caixa:after{content:"";position:absolute;width:18px;height:18px;border:3px solid var(--ciano)}
.caixa:before{top:-3px;left:-3px;border-right:0;border-bottom:0;border-radius:6px 0 0 0}
.caixa:after{bottom:-3px;right:-3px;border-left:0;border-top:0;border-radius:0 0 6px 0}
.card{background:var(--branco);color:var(--ink);border-radius:24px;box-shadow:0 18px 50px rgba(0,0,0,.35)}
.rot{font-family:"SF Mono",Menlo,monospace;font-size:22px;letter-spacing:2px;color:var(--ciano);font-weight:700}
.rod{height:100px;margin:0 -72px;padding:0 60px;display:flex;align-items:center;gap:16px;font-size:24px;font-weight:800;
 color:var(--cinza);border-top:1px solid rgba(108,198,255,.25);background:rgba(8,22,40,.6)}
.rod img{height:48px}
.rod .dir{margin-left:auto;color:var(--branco)}
.bolha{display:inline-block;background:var(--branco);color:var(--ink);border-radius:26px 26px 8px 26px;padding:22px 30px;font-size:31px;font-weight:700;box-shadow:0 12px 30px rgba(0,0,0,.3)}
.prompt{font-family:"SF Mono",Menlo,monospace;background:#061325;border:2px solid rgba(108,198,255,.4);border-radius:18px;padding:22px 26px;font-size:28px;color:var(--branco)}
.prompt .p{color:var(--ml);margin-right:12px}
.num{width:64px;height:64px;border-radius:50%;border:3px solid var(--ml);color:var(--ml);font-weight:900;font-size:34px;
 display:flex;align-items:center;justify-content:center;flex:none}
.chip{display:inline-flex;align-items:center;gap:12px;background:rgba(244,247,251,.08);border:2px solid rgba(244,247,251,.25);border-radius:999px;
 padding:14px 26px;font-size:28px;font-weight:700}
.ok{display:inline-flex;align-items:center;gap:14px;background:var(--ml);color:var(--ink);font-weight:900;font-size:32px;padding:18px 32px;border-radius:16px}
.passo{font-family:"SF Mono",Menlo,monospace;font-size:28px;font-weight:700;letter-spacing:4px;color:var(--claude);margin-bottom:10px}
.lista{display:grid;row-gap:22px}
.li{display:flex;align-items:center;gap:20px;font-size:32px;font-weight:600;color:#E4EAF2}
.li i{width:16px;height:16px;border-radius:4px;background:var(--ml);flex:none;transform:rotate(45deg)}
.tag{font-size:22px;font-weight:800;padding:6px 14px;border-radius:8px}
.alta{background:#FFD9D2;color:#B3261E}.media{background:#FFF1B8;color:#7A5B00}.baixa{background:#DDF5E6;color:#1E7A45}
"""


def topo(n):
    return (f"<div class='topo'><span>◧ PLANTA DO SISTEMA</span>"
            f"<span class='n'><b>{n:02d}</b> / {TOTAL:02d}</span></div>")


def rodape(n):
    dir_ = 'Deslize para ver a planta →' if n == 1 else 'Marketplace Connect'
    return (f"<div class='rod'><img src='../assets/tiops-robo.png'>@tiopstecnologia"
            f"<span class='dir'>{dir_}</span></div>")


def pagina(n, corpo):
    return (f"<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body>{topo(n)}{corpo}{rodape(n)}</body></html>")


S = {}

# 1 · capa
S[1] = """
<div><span class='etq'>SEM CÓDIGO · EM PORTUGUÊS</span></div>
<h1>Monte o seu próprio <span class='y'>sistema de IA</span> para vender em marketplace.</h1>
<p class='sub'>Claude + Marketplace Connect + as suas regras.</p>
<div class='sp'></div>
<div style='position:relative;height:470px'>
  <svg width='936' height='470' style='position:absolute;left:0;top:0'>
    <g stroke='#6CC6FF' stroke-width='3' stroke-dasharray='10 9' fill='none' opacity='.8'>
      <path d='M190 85 C 260 85, 270 235, 330 235'/><path d='M190 235 L 330 235'/><path d='M190 385 C 260 385, 270 235, 330 235'/>
      <path d='M560 235 L 640 235'/>
      <path d='M790 235 C 820 235, 810 95, 846 95'/><path d='M790 235 L 846 235'/><path d='M790 235 C 820 235, 810 375, 846 375'/>
    </g>
  </svg>
  <div class='card' style='position:absolute;left:0;top:30px;width:190px;height:110px;display:flex;align-items:center;justify-content:center'><img src='../assets/ml.png' style='height:80px'></div>
  <div class='card' style='position:absolute;left:0;top:180px;width:190px;height:110px;display:flex;align-items:center;justify-content:center'><img src='../assets/shopee.png' style='height:82px'></div>
  <div class='card' style='position:absolute;left:0;top:330px;width:190px;height:110px;display:flex;align-items:center;justify-content:center'><img src='../assets/amazon.png' style='height:66px'></div>
  <div class='caixa' style='position:absolute;left:330px;top:150px;width:230px;height:170px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center'>
    <img src='../assets/tiops-robo.png' style='height:64px'>
    <b style='font-size:27px;line-height:1.1'>Marketplace<br>Connect</b>
  </div>
  <div style='position:absolute;left:640px;top:160px;width:150px;height:150px;border-radius:36px;overflow:hidden;box-shadow:0 0 0 6px rgba(229,138,102,.35),0 20px 50px rgba(0,0,0,.4)'><img src='../assets/claude.png' style='width:150px;height:150px'></div>
  <div class='chip' style='position:absolute;right:-30px;top:66px;padding:12px 20px;font-size:25px'>🧠 Memória</div>
  <div class='chip' style='position:absolute;right:-6px;top:206px;padding:12px 20px;font-size:25px'>⚙️ Skills</div>
  <div class='chip' style='position:absolute;right:-12px;top:346px;padding:12px 20px;font-size:25px'>📊 Painel</div>
</div>
<div class='sp'></div>
<div style='text-align:right;margin-bottom:34px'><span class='bolha'>“Quais anúncios acabam o estoque esta semana?”</span></div>
"""

# 2 · a dor
S[2] = """
<h1 class='m'>A sua operação inteira <span class='y'>num lugar só.</span></h1>
<div style='height:46px'></div>
<div class='lista'>
  <div class='li'><i></i>Vendas, margem e custos</div>
  <div class='li'><i></i>Anúncios, estoque e promoções</div>
  <div class='li'><i></i>Perguntas, concorrência e oportunidades</div>
</div>
<div class='sp'></div>
<div class='prompt' style='font-size:26px'><span class='p'>›</span>Como foram as vendas da semana em cada canal?</div>
<div style='height:16px'></div>
<div class='card' style='padding:24px 30px'>
  <div style='display:grid;grid-template-columns:230px 1fr;row-gap:16px;align-items:center;font-size:27px;font-weight:700'>
    <span>Mercado Livre</span><div style='height:22px;border-radius:11px;background:#F2C200;width:92%'></div>
    <span>Shopee</span><div style='height:22px;border-radius:11px;background:#EE4D2D;width:61%'></div>
    <span>Amazon</span><div style='height:22px;border-radius:11px;background:#232F3E;width:38%'></div>
  </div>
</div>
<div class='sp'></div>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:46px'>
  <div class='caixa' style='padding:34px 32px;border-color:rgba(255,255,255,.2);background:rgba(255,255,255,.04)'>
    <div class='rot' style='color:var(--cinza)'>ANTES</div>
    <div style='font-size:38px;font-weight:800;margin-top:14px;line-height:1.2;color:#C7D2E0'>Abrir 4 painéis e cruzar planilhas.</div>
    <div style='margin-top:22px;font-size:60px'>🗂️</div>
  </div>
  <div class='caixa' style='padding:34px 32px;background:rgba(255,230,0,.10);border-color:var(--ml)'>
    <div class='rot' style='color:var(--ml)'>AGORA</div>
    <div style='font-size:38px;font-weight:800;margin-top:14px;line-height:1.2'>Pedir em português e revisar.</div>
    <div style='margin-top:22px;font-size:60px'>💬</div>
  </div>
</div>
"""

# 3 · como cada pedido funciona
S[3] = """
<h1 class='m'>Como funciona <span class='y'>cada pedido.</span></h1>
<div style='height:40px'></div>
<div style='display:grid;row-gap:26px'>
  <div style='display:flex;gap:24px;align-items:center'><div class='num'>1</div><div style='font-size:32px;line-height:1.3'><b>Você pede</b> em português, como numa conversa.</div></div>
  <div style='display:flex;gap:24px;align-items:center'><div class='num'>2</div><div style='font-size:32px;line-height:1.3'><b>O Claude busca</b> os dados da loja pelo Connect.</div></div>
  <div style='display:flex;gap:24px;align-items:center'><div class='num'>3</div><div style='font-size:32px;line-height:1.3'><b>Ele responde</b> e propõe o que fazer primeiro.</div></div>
</div>
<div class='sp'></div>
<div class='prompt'><span class='p'>›</span>Quais anúncios precisam de reposição?</div>
<div style='height:20px'></div>
<div class='card' style='padding:28px 32px'>
  <div style='font-size:30px;font-weight:900;margin-bottom:18px'>📦 Reposição, por prioridade</div>
  <div style='display:grid;grid-template-columns:44px 1fr 250px 110px;row-gap:18px;align-items:center;font-size:28px;font-weight:600'>
    <b>1</b><span>Fone sem fio</span><span style='color:#5B6B80'>acaba em 3 dias</span><span class='tag alta'>Alta</span>
    <b>2</b><span>Garrafa térmica</span><span style='color:#5B6B80'>acaba em 6 dias</span><span class='tag alta'>Alta</span>
    <b>3</b><span>Fritadeira elétrica</span><span style='color:#5B6B80'>acaba em 12 dias</span><span class='tag media'>Média</span>
    <b>4</b><span>Tênis de corrida</span><span style='color:#5B6B80'>acaba em 20 dias</span><span class='tag baixa'>Baixa</span>
  </div>
</div>
<div style='height:26px'></div>
<div style='text-align:center;margin-bottom:34px'><span class='ok'>✓ Nada muda na loja sem o seu OK</span></div>
"""

# 4 · as cinco peças
LINHAS = [
    ("<img src='../assets/claude.png' style='width:64px;height:64px;border-radius:16px'>", 'Claude', 'o cérebro', 'Entende o pedido, pensa e executa.'),
    ("<img src='../assets/tiops-robo.png' style='height:52px'>", 'Marketplace Connect', 'os dados', 'Liga o Claude às suas lojas e ao seu ERP.'),
    ("<span style='font-size:50px'>🧠</span>", 'Projeto', 'a memória', 'Suas regras e o contexto do negócio.'),
    ("<span style='font-size:50px'>⚙️</span>", 'Skills', 'as tarefas', 'O passo a passo que você escreve uma vez.'),
    ("<span style='font-size:50px'>📊</span>", 'Painel', 'a visão', 'As prioridades do dia numa tela.'),
]
_tab = ''.join(
    f"<div style='display:flex;align-items:center;gap:24px;padding:22px 26px;{'border-top:1px solid rgba(108,198,255,.25);' if i else ''}'>"
    f"<div style='width:76px;display:flex;justify-content:center'>{ic}</div>"
    f"<div style='flex:1'><div style='font-size:34px;font-weight:900'>{nome} <span class='mono' style='font-size:24px;color:var(--claude);font-weight:700'>· {papel}</span></div>"
    f"<div style='font-size:27px;color:#C7D2E0;margin-top:6px'>{desc}</div></div></div>"
    for i, (ic, nome, papel, desc) in enumerate(LINHAS))
S[4] = f"""
<h1 class='m'>As <span class='y'>5 peças</span> do sistema.</h1>
<div style='height:40px'></div>
<div class='caixa' style='padding:6px 0'>{_tab}</div>
<div class='sp'></div>
<div style='display:flex;align-items:center;gap:22px;margin-bottom:44px'>
  <div class='rot' style='font-size:26px;line-height:1.5;flex:1'>ENTENDE · LEMBRA ·<br>EXECUTA · MOSTRA</div>
  <div style='font-size:32px;font-weight:800;text-align:right;line-height:1.3'>Você não programa nada.<br><span class='y'>Monta conversando.</span></div>
</div>
"""

# 5 · passo 1
S[5] = """
<div class='passo'>PASSO 1</div>
<h1 class='m'>Conecte as <span class='y'>suas lojas.</span></h1>
<div style='height:40px'></div>
<div class='caixa' style='padding:34px 34px'>
  <div style='display:grid;row-gap:34px'>
    <div style='display:flex;gap:24px;align-items:center'><div class='num'>1</div><div><b style='font-size:36px'>Autorize a sua conta</b><div style='font-size:28px;color:#C7D2E0;margin-top:4px'>Login oficial do marketplace, um clique.</div></div></div>
    <div style='display:flex;gap:24px;align-items:center'><div class='num'>2</div><div><b style='font-size:36px'>Cole o conector no Claude</b><div style='font-size:28px;color:#C7D2E0;margin-top:4px'>Configurações → Conectores.</div></div></div>
    <div style='display:flex;gap:24px;align-items:center'><div class='num'>3</div><div><b style='font-size:36px'>Pergunte em português</b><div style='font-size:28px;color:#C7D2E0;margin-top:4px'>“Me mostra o que mais vendeu esta semana.”</div></div></div>
  </div>
</div>
<div class='sp'></div>
<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:20px'>
  <div class='card' style='height:150px;display:flex;align-items:center;justify-content:center'><img src='../assets/ml.png' style='height:104px'></div>
  <div class='card' style='height:150px;display:flex;align-items:center;justify-content:center'><img src='../assets/shopee.png' style='height:108px'></div>
  <div class='card' style='height:150px;display:flex;align-items:center;justify-content:center'><img src='../assets/amazon.png' style='height:84px'></div>
</div>
<div style='height:20px'></div>
<div style='display:flex;gap:14px;flex-wrap:wrap;justify-content:center'>
  <span class='chip'>Magalu</span><span class='chip'>TikTok Shop</span><span class='chip'>Shein</span><span class='chip'>Bling</span><span class='chip'>Olist</span>
</div>
<div class='sp'></div>
<p style='text-align:center;font-size:30px;font-weight:700;color:#C7D2E0;margin-bottom:36px'>Uns <span class='y'>2 minutos</span> por loja. Funciona também no ChatGPT.</p>
"""

# 6 · passo 2
ARQS = [
    ('regras.md', 'Margem mínima de 15%. Nunca baixar preço sem me mostrar.'),
    ('custos.md', 'Imposto, frete e embalagem de cada produto.'),
    ('atendimento.md', 'Responder o cliente com “você”, curto e educado.'),
    ('decisoes.md', 'O que já testei, o que deu certo e por quê.'),
]
_arqs = ''.join(
    f"<div style='display:flex;gap:20px;align-items:flex-start;padding:20px 0;{'border-top:1px solid #DCE3EC;' if i else ''}'>"
    f"<span style='font-size:34px'>📄</span><div><div class='mono' style='font-size:26px;font-weight:800;color:#1B4F8A'>{a}</div>"
    f"<div style='font-size:28px;margin-top:4px;color:#24364D'>{t}</div></div></div>"
    for i, (a, t) in enumerate(ARQS))
S[6] = f"""
<div class='passo'>PASSO 2</div>
<h1 class='m'>Dê <span class='y'>memória</span> ao sistema.</h1>
<p class='sub'>Crie um Projeto no Claude e escreva o que ele precisa saber da sua loja.</p>
<div class='sp'></div>
<div class='card' style='padding:26px 34px 14px'>
  <div style='display:flex;align-items:center;gap:14px;font-size:30px;font-weight:900;padding-bottom:10px;border-bottom:3px solid var(--ink)'>📁 Projeto: Minha loja</div>
  {_arqs}
</div>
<div class='sp'></div>
<div style='display:flex;align-items:center;gap:20px;margin-bottom:44px'>
  <span style='font-size:56px'>🧠</span>
  <div style='font-size:34px;font-weight:800;line-height:1.3'>Toda conversa do projeto já começa <span class='y'>sabendo disso.</span></div>
</div>
"""

# 7 · passo 3
SKILLS = [
    ('margem-baixa', 'Lista os anúncios abaixo do piso e sugere o preço.'),
    ('promocao', 'Simula o desconto antes de entrar na campanha.'),
    ('reposicao', 'Avisa o que acaba nos próximos 7 dias.'),
]
_sk = ''.join(
    f"<div style='display:flex;align-items:center;gap:20px;border:2px solid rgba(108,198,255,.4);border-radius:16px;padding:20px 24px;margin-top:16px'>"
    f"<span class='mono' style='font-size:27px;color:var(--ml);font-weight:800;min-width:250px'>📄 {n}</span>"
    f"<span style='font-size:28px;color:#E4EAF2;line-height:1.3'>{t}</span></div>"
    for n, t in SKILLS)
S[7] = f"""
<div class='passo'>PASSO 3</div>
<h1 class='m'>Ensine as suas <span class='y'>skills.</span></h1>
<p class='sub'>Uma skill é um passo a passo que você escreve uma vez. Depois, é só pedir.</p>
<div class='sp'></div>
<div style='background:#061325;border:2px solid rgba(108,198,255,.4);border-radius:24px;padding:26px 30px 32px'>
  <div style='display:flex;gap:10px;margin-bottom:14px'><i style='width:16px;height:16px;border-radius:50%;background:#FF6159'></i><i style='width:16px;height:16px;border-radius:50%;background:#FFBD2E'></i><i style='width:16px;height:16px;border-radius:50%;background:#28C941'></i>
  <span class='mono' style='margin-left:16px;font-size:22px;color:var(--cinza)'>minhas-skills/</span></div>
  {_sk}
</div>
<div style='height:30px'></div>
<div style='text-align:right'><span class='bolha'>“Roda a reposição de hoje.”</span></div>
<div style='height:16px'></div>
<div class='card' style='padding:22px 28px;font-size:28px;font-weight:600;line-height:1.35'>
  📦 <b>Fone sem fio</b> e <b>Garrafa térmica</b> acabam até sexta. Quer ver quanto repor de cada um?
</div>
<div class='sp'></div>
<div style='display:flex;justify-content:center;gap:18px;margin-bottom:44px'>
  <span class='chip'>✍️ Escreve uma vez</span><span class='chip' style='border-color:var(--ml);color:var(--ml)'>🔁 Usa todo dia</span>
</div>
"""

# 8 · passo 4
TILES = [
    ('💰', 'Margem', '3 anúncios abaixo do piso', '#FFD9D2', '#B3261E'),
    ('📦', 'Estoque', '2 acabam esta semana', '#FFF1B8', '#7A5B00'),
    ('💬', 'Perguntas', '5 esperando resposta', '#DCEBFF', '#1B4F8A'),
    ('🏷️', 'Promoções', '1 vale a pena entrar', '#DDF5E6', '#1E7A45'),
]
_tiles = ''.join(
    f"<div style='background:{bg};border-radius:20px;padding:24px 24px'>"
    f"<div style='font-size:42px'>{ic}</div><div style='font-size:32px;font-weight:900;margin-top:8px;color:var(--ink)'>{t}</div>"
    f"<div style='font-size:26px;font-weight:700;color:{cor};margin-top:6px;line-height:1.25'>{d}</div></div>"
    for ic, t, d, bg, cor in TILES)
S[8] = f"""
<div class='passo'>PASSO 4</div>
<h1 class='m'>Peça o seu <span class='y'>painel.</span></h1>
<div style='height:30px'></div>
<div class='prompt'><span class='p'>›</span>Monte um painel com as prioridades de hoje.</div>
<div class='sp'></div>
<div class='card' style='padding:30px 30px'>
  <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:22px'>
    <b style='font-size:36px'>Prioridades de hoje</b>
    <span class='mono' style='font-size:22px;color:#5B6B80'>ML · Shopee · Amazon</span>
  </div>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:18px'>{_tiles}</div>
</div>
<div class='sp'></div>
<p style='font-size:34px;font-weight:800;text-align:center;line-height:1.3;margin-bottom:40px'>Abra de manhã e saiba<br><span class='y'>por onde começar.</span></p>
"""

# 9 · passo 5
S[9] = """
<div class='passo'>PASSO 5</div>
<h1 class='m'>Encontre <span class='y'>oportunidades.</span></h1>
<p class='sub'>Ele compara os seus anúncios com o mercado e diz o que ajustar.</p>
<div class='sp'></div>
<div class='card' style='padding:28px 30px'>
  <div style='display:grid;grid-template-columns:230px 1fr 1fr;gap:22px 16px;align-items:center;font-size:28px;font-weight:700;text-align:center'>
    <span></span><b style='background:var(--ml);border-radius:12px;padding:10px'>Seu anúncio</b><b style='color:#5B6B80'>Mais vendido</b>
    <span style='text-align:left'>💲 Preço</span><span>Acima da média</span><span>Na média</span>
    <span style='text-align:left'>🖼️ Fotos</span><span>3</span><span>8</span>
    <span style='text-align:left'>🔎 Título</span><span>Sem termos em alta</span><span>Com termos em alta</span>
    <span style='text-align:left'>⭐ Qualidade</span><span style='color:#B3261E'>Falta ficha técnica</span><span style='color:#1E7A45'>Completo</span>
  </div>
</div>
<div style='height:34px'></div>
<div class='lista'>
  <div class='li'><i></i>Termos em alta na sua categoria</div>
  <div class='li'><i></i>Visitas × vendas de cada anúncio</div>
  <div class='li'><i></i>Onde o seu preço está fora do mercado</div>
</div>
<div class='sp'></div>
<p class='rot' style='text-align:center;font-size:26px;margin-bottom:40px'>PRIMEIRO ELE MOSTRA. VOCÊ DECIDE.</p>
"""

# 10 · CTA
S[10] = """
<h1 style='text-align:center'>Quer montar <span class='y'>o seu?</span></h1>
<div class='sp'></div>
<div class='caixa' style='padding:56px 40px 60px;text-align:center;border-color:var(--ml);background:rgba(255,230,0,.08)'>
  <div style='display:inline-block;background:var(--ml);color:var(--ink);font-size:44px;font-weight:900;padding:12px 40px;border-radius:12px'>Comenta</div>
  <div style='font-size:170px;font-weight:900;letter-spacing:-5px;line-height:1;margin:26px 0 14px'>CONNECT</div>
  <div style='font-size:40px;font-weight:700;line-height:1.3'>que eu te mando o link e o<br>passo a passo no direct.</div>
</div>
<div class='sp'></div>
<div style='display:flex;gap:30px;align-items:center;justify-content:center'>
  <img src='../assets/claude.png' style='width:100px;height:100px;border-radius:24px'>
  <span style='font-size:56px;font-weight:900'>+</span>
  <div class='caixa' style='padding:18px 26px;display:flex;align-items:center;gap:14px'><img src='../assets/tiops-robo.png' style='height:56px'><b style='font-size:30px'>Marketplace Connect</b></div>
</div>
<div style='height:40px'></div>
<p style='text-align:center;font-size:30px;font-weight:700;color:#C7D2E0;margin-bottom:40px'>🔖 Salve para montar com calma depois.</p>
"""


def main():
    for d in (HTML, OUT, JPG):
        os.makedirs(d, exist_ok=True)
    for n, corpo in S.items():
        open(os.path.join(HTML, f'slide-{n:02d}.html'), 'w').write(pagina(n, corpo))
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for n in S:
            pg.goto('file://' + os.path.join(HTML, f'slide-{n:02d}.html'))
            pg.wait_for_timeout(300)
            # avisa se algum conteúdo empurrou o rodapé para baixo da borda
            fim = pg.evaluate("document.querySelector('.rod').getBoundingClientRect().bottom")
            if fim > 1351:
                print('ATENÇÃO: slide', n, 'estourou, rodapé termina em', fim)
            pg.screenshot(path=os.path.join(OUT, f'slide-{n:02d}.png'))
        b.close()
    from PIL import Image
    ims = []
    for n in S:
        im = Image.open(os.path.join(OUT, f'slide-{n:02d}.png')).convert('RGB')
        im.save(os.path.join(JPG, f'slide-{n:02d}.jpg'), quality=92)
        ims.append(im)
    w, h = 324, 405
    sheet = Image.new('RGB', (w * 5 + 60, h * 2 + 30), (30, 30, 30))
    for i, im in enumerate(ims):
        sheet.paste(im.resize((w, h)), (10 + (i % 5) * (w + 10), 10 + (i // 5) * (h + 10)))
    sheet.save(os.path.join(AQUI, 'sheet.png'))
    print('ok', len(ims), 'slides')


if __name__ == '__main__':
    main()
