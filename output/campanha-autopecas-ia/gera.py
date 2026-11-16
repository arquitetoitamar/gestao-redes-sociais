#!/usr/bin/env python3
"""Campanha "Autopeças + IA" (GestorPro): carrossel do Instagram, documento do LinkedIn e cartões do Reel.

Visual da página gestorpro.tiops.com.br/ia-para-autopecas (papel, tinta, verde e âmbar; Fraunces + Inter + JetBrains Mono).
Fotos geradas no Higgsfield (img/hf-*.png). Tabela, veículos e prazos são fictícios, como na página.

  python3 gera.py            carrossel/slides/slide-XX.png + linkedin/autopecas-ia-tiops.pdf + reel/cards/*.png
  python3 gera.py carrossel  só o carrossel do Instagram
"""
import os
import sys
from playwright.sync_api import sync_playwright
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
TOTAL = 8
LINK = 'l.tiops.com.br/autopecas'

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Inter:wght@500;600;700;800;900&family=JetBrains+Mono:wght@600;700&display=swap');
:root{--paper:#f7f6f2;--ink:#131417;--ink2:#4a4f5a;--ink3:#7b8190;--line:#e5e3dc;--green:#0a8f60;--green2:#e4f4ec;
 --amber:#b45309;--amber2:#fdf1e2;--red:#c2410c;--red2:#fde8e1}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,system-ui,sans-serif;color:var(--ink)}
.slide{width:1080px;height:1350px;overflow:hidden;position:relative;background:var(--paper);padding:92px 80px 0;display:flex;flex-direction:column}
.serif{font-family:Fraunces,Georgia,serif}
.mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}
.cont{position:absolute;top:48px;right:64px;font:700 24px 'JetBrains Mono',monospace;color:var(--ink3)}
.cont b{color:var(--green)}
.kick{font:700 26px 'JetBrains Mono',monospace;letter-spacing:1px;color:var(--green);text-transform:uppercase;margin-bottom:22px}
.kick.amb{color:var(--amber)}
h1{font-family:Fraunces,Georgia,serif;font-weight:800;font-size:78px;line-height:1.04;letter-spacing:-1.5px}
h1.p{font-size:74px}
h1 em{font-style:normal;color:var(--green)}
h1 em.a{color:var(--amber)}
.sub{font-size:37px;line-height:1.38;font-weight:600;color:var(--ink2);margin-top:26px}
.sub b{color:var(--ink)}
.sp{flex:1}
.card{background:#fff;border:2px solid var(--line);border-radius:28px;padding:32px 36px;box-shadow:0 14px 40px rgba(20,20,23,.06)}
.rod{height:100px;margin:0 -80px;padding:0 64px;display:flex;align-items:center;gap:16px;font-size:24px;font-weight:800;color:var(--ink2);border-top:2px solid var(--line)}
.rod img{height:46px}
.rod .dir{margin-left:auto;font-family:Fraunces,Georgia,serif;font-size:30px;color:var(--ink)}
.rod .dir b{color:var(--green)}
.num{display:inline-flex;align-items:center;justify-content:center;width:100px;height:100px;border-radius:50%;background:var(--ink);color:#fff;
 font:800 48px Fraunces,Georgia,serif;margin-bottom:34px}
.li{display:flex;gap:22px;font-size:39px;line-height:1.36;font-weight:600;margin:30px 0;color:var(--ink2)}
.li b{color:var(--ink)}
.li i{flex:none;width:44px;height:44px;border-radius:50%;margin-top:4px;background:var(--green2);border:3px solid var(--green);position:relative}
.li i.x{background:var(--red2);border-color:var(--red)}
.l7 .li{font-size:35px;margin:20px 0}
.nota{font:600 26px/1.45 'JetBrains Mono',monospace;color:var(--ink3);margin-top:22px}
/* anúncio + tabela */
.an-l{font:700 22px 'JetBrains Mono',monospace;color:var(--ink3);letter-spacing:.5px}
.an-t{font-size:38px;font-weight:800;margin:10px 0 14px}
.an-d{font-size:30px;line-height:1.35;color:var(--ink2);background:var(--paper);border-radius:16px;padding:18px 22px}
.an-d mark{background:#fff3c4;color:var(--ink);font-weight:800;padding:0 6px;border-radius:6px}
table{width:100%;border-collapse:collapse;margin-top:20px;font-size:28px}
th{font:700 20px 'JetBrains Mono',monospace;color:var(--ink3);text-align:left;padding:12px 10px;border-bottom:2px solid var(--line);text-transform:uppercase}
td{padding:16px 10px;border-bottom:2px solid var(--line);font-weight:700}
td.ok{color:var(--green)}
td.no{color:var(--red)}
tr.no td{background:var(--red2)}
tr.no td:first-child{border-radius:12px 0 0 12px}
tr.no td:last-child{border-radius:0 12px 12px 0}
.pill{display:inline-flex;align-items:center;gap:10px;border-radius:999px;padding:10px 20px;font-weight:800;font-size:24px}
.pill.g{background:var(--green2);color:var(--green)}
.pill.a{background:var(--amber2);color:var(--amber)}
.pill.r{background:var(--red2);color:var(--red)}
.btn{display:inline-block;background:var(--green);color:#fff;font-weight:800;font-size:28px;padding:16px 30px;border-radius:14px}
.btn.o{background:#fff;color:var(--ink2);border:2px solid var(--line)}
.ag{display:flex;align-items:center;gap:18px;margin-bottom:16px}
.ag .av{width:64px;height:64px;border-radius:18px;display:flex;align-items:center;justify-content:center;font:800 26px 'JetBrains Mono',monospace;color:#fff;flex:none}
.ag .nm{font-size:30px;font-weight:800}
.ag .sb{font-size:22px;color:var(--ink3);font-weight:600}
"""


def rodape(n, ln):
    if ln:
        esq = "<img src='../../assets/tiops-icon.png'>TiOps Tecnologia"
    else:
        esq = "<img src='../../assets/tiops-robo.png'>@tiopstecnologia"
    dir_ = 'Deslize →' if n == 1 else 'Gestor<b>Pro</b>'
    return f"<div class='rod'>{esq}<span class='dir'>{dir_}</span></div>"


def cont(n):
    return f"<div class='cont'><b>{n:02d}</b> / {TOTAL:02d}</div>"


def anuncio(compacto=False):
    """Anúncio fictício: a descrição restringe, a tabela libera."""
    linhas = [('Hatch 1.0 aspirado', '2020', True), ('Hatch 1.0 turbo', '2020', False),
              ('Sedã 1.0 aspirado', '2021', True), ('Sedã 1.0 turbo', '2021', False)]
    tr = ''.join(f"<tr class='{'' if ok else 'no'}'><td>{v}</td><td>{a}</td><td class='ok'>listado</td>"
                 f"<td class='{'ok' if ok else 'no'}'>{'sim' if ok else 'não'}</td></tr>" for v, a, ok in linhas)
    return f"""<div class='card'>
 <div class='an-l'>ANÚNCIO · EXEMPLO ILUSTRATIVO</div>
 <div class='an-t'>Pastilha de freio dianteira</div>
 <div class='an-d'>Descrição: “Compatível <mark>somente com as versões 1.0 aspirado</mark>.”</div>
 <table><tr><th>Veículo</th><th>Ano</th><th>Tabela</th><th>Descrição permite?</th></tr>{tr}</table>
</div>"""


def curador():
    return """<div class='card'>
 <div class='ag'><div class='av' style='background:#7c3aed'>CC</div><div><div class='nm'>Curador de catálogo</div><div class='sb'>por que a reclamação aconteceu</div></div></div>
 <div class='an-d' style='font-size:28px'>A tabela libera <b>2 veículos</b> que a descrição exclui (1.0 turbo).</div>
 <div style='margin-top:22px;font-size:28px;font-weight:700;line-height:1.5'>
  Proposta:<br>→ Tirar 2 veículos da tabela <span style='color:var(--ink3);font-weight:600'>(aplicar no painel do canal)</span><br>
  → Título e 1ª linha: <b>“1.0 aspirado”</b></div>
 <div style='margin-top:24px;display:flex;gap:14px;align-items:center'><span class='btn'>Aprovar</span><span class='btn o'>Recusar</span>
  <span class='pill a' style='margin-left:auto'>fila de Anúncios</span></div>
</div>"""


def atendente():
    return """<div class='card'>
 <div class='ag'><div class='av' style='background:var(--green)'>AT</div><div><div class='nm'>Atendente · pós-venda</div><div class='sb'>leu a conversa inteira, na ordem</div></div>
  <span class='pill r' style='margin-left:auto'>prazo 1d 18h</span></div>
 <div class='an-d' style='font-size:28px'><b>Reclamação · Não serve no veículo</b><br>Rascunho da resposta pronto · aguardando aprovação</div>
 <div style='margin-top:20px;font-size:26px;font-weight:700;color:var(--ink2)'>Solução, decisão da loja:</div>
 <div style='margin-top:12px;display:flex;gap:12px'><span class='pill a'>Troca</span><span class='pill a'>Devolução</span><span class='pill a'>Reembolso parcial</span></div>
 <div style='margin-top:22px;display:flex;align-items:center;gap:14px;font-size:24px;font-weight:700;color:var(--green)'>
  ✓ Aprovado pela equipe de Pós-venda · antes, depois e motivo registrados <span class='btn o' style='margin-left:auto;font-size:22px;padding:10px 18px'>Desfazer</span></div>
</div>"""


def slides(ln=False):
    """Lista de (n, html interno da .slide). ln=True: versão da página TiOps no LinkedIn (sem @ do Itamar e sem 'comenta')."""
    s = []
    capa_bg = ("background:linear-gradient(180deg,rgba(10,12,16,.92) 0%,rgba(10,12,16,.78) 38%,rgba(10,12,16,.05) 62%),"
               "url('../../img/hf-capa-estoque.png') center/cover")
    s.append(f"""<div class='slide' style="{capa_bg};color:#fff">
 <div class='kick' style='color:#7ee2b8'>Autopeças no marketplace</div>
 <h1 style='font-size:84px'>Sua tabela de compatibilidade pode estar <em style='color:#ffd27a'>gerando reclamação</em></h1>
 <div class='sub' style='color:#e8e6df'>5 conferências para fazer <b style='color:#fff'>antes da Black Friday</b></div>
 <div class='sp'></div>
 <div class='rod' style='border-top:0;color:#e8e6df'>{rodape(1, ln)[17:].replace("<span class='dir'>", "<span class='dir' style='color:#fff'>")}
</div>""")
    s.append(f"""<div class='slide'>{cont(2)}
 <div class='kick amb'>Como nasce um “não serve no veículo”</div>
 <h1 class='p'>A descrição exclui.<br><em class='a'>A tabela libera.</em></h1>
 <div style='margin-top:36px'>{anuncio()}</div>
 <div class='sub' style='font-size:36px'>O comprador lê “compatível”, compra, a peça não serve. Na mediação, a leitura do comprador <b>tende a ganhar</b>.</div>
 <div class='sp'></div>{rodape(2, ln)}</div>""")
    s.append(f"""<div class='slide'>{cont(3)}
 <div class='num'>1</div>
 <h1 class='p'>Tabela, título e descrição dizem <em>a mesma coisa</em></h1>
 <div style='margin-top:30px'>
  <div class='li'><i></i><span>Versão, motor, ano e lado: <b>o que a descrição restringe, a tabela não pode liberar</b>.</span></div>
  <div class='li'><i></i><span>Restrição importante vai no <b>título e na 1ª linha</b>, não escondida no fim do texto.</span></div>
  <div class='li'><i class='x'></i><span>Tabela copiada do fornecedor <b>sem conferir</b> contra o próprio anúncio.</span></div>
 </div>
 <div class='nota'>No Mercado Livre, compatibilidade gerenciada pelo catálogo se ajusta só pelo painel do canal desde 15/07/2026 (documentação de desenvolvedores do ML).</div>
 <div class='sp'></div>{rodape(3, ln)}</div>""")
    s.append(f"""<div class='slide'>{cont(4)}
 <div class='num'>2</div>
 <h1 class='p'>Par ou unidade? <em>Lado do motorista</em> ou do passageiro?</h1>
 <div class='sub'>São as perguntas que mais se repetem em autopeças. Se a resposta não está no anúncio, vira pergunta antes da venda e reclamação depois.</div>
 <div style='margin-top:40px;display:flex;flex-direction:column;gap:18px'>
  <div class='card' style='padding:30px 34px;font-size:38px;font-weight:700'>❌ “Pastilha de freio dianteira”</div>
  <div class='card' style='padding:30px 34px;font-size:38px;font-weight:700;border-color:var(--green)'>✅ “Pastilha de freio dianteira · jogo com 4 · só 1.0 aspirado 2020-2021”</div>
 </div>
 <div class='nota'>Exemplo ilustrativo.</div>
 <div class='sp'></div>{rodape(4, ln)}</div>""")
    s.append(f"""<div class='slide'>{cont(5)}
 <div class='num'>3</div>
 <h1 class='p' style='font-size:64px'>“Serve no meu carro?” <em>se responde pela tabela</em>, nunca por palpite</h1>
 <div style='margin-top:14px' class='l7'>
  <div class='li'><i></i><span>Resposta vem da <b>tabela do anúncio</b>, do título, da descrição e do que a equipe já respondeu.</span></div>
  <div class='li'><i class='x'></i><span>Veículo fora da tabela <b>não recebe “serve”</b>. Melhor pedir o ano e a versão.</span></div>
 </div>
 <div class='num' style='margin-top:22px'>4</div>
 <h1 class='p' style='font-size:62px'>Peça que chegou e não serviu é <em class='a'>pós-venda</em></h1>
 <div class='sub' style='font-size:35px'>Não responda em público na pergunta do anúncio: leve para o atendimento da venda.</div>
 <div class='sp'></div>{rodape(5, ln)}</div>""")
    s.append(f"""<div class='slide'>{cont(6)}
 <div class='num'>5</div>
 <h1 class='p'>Reclamação tem prazo. <em class='a'>A solução é da loja.</em></h1>
 <div style='margin-top:30px'>
  <div class='li'><i></i><span>Leia a conversa <b>inteira, na ordem</b>: comprador, loja e mediador.</span></div>
  <div class='li'><i></i><span>Responda <b>dentro do prazo do canal</b>. Perder prazo pesa na reputação.</span></div>
  <div class='li'><i></i><span>Troca, devolução ou reembolso parcial: <b>decisão de quem conhece a peça</b>.</span></div>
  <div class='li'><i></i><span>Depois do caso, <b>corrija o anúncio</b>. Senão a próxima reclamação já está a caminho.</span></div>
 </div>
 <div class='sp'></div>{rodape(6, ln)}</div>""")
    s.append(f"""<div class='slide' style='padding-top:0'>{cont(7)}
 <div style="height:420px;margin:0 -80px 40px;background:linear-gradient(180deg,rgba(247,246,242,0) 55%,var(--paper) 100%),url('../../img/hf-equipe-aprovacao.png') center 38%/cover"></div>
 <div class='kick'>Onde a IA entra (e onde não entra)</div>
 <h1 class='p' style='font-size:62px'>Os agentes fazem o volume. <em>A equipe decide.</em></h1>
 <div style='margin-top:10px;font-size:35px' class='l7'>
  <div class='li'><i></i><span><b>Atendente:</b> prepara a resposta da reclamação e mostra o prazo.</span></div>
  <div class='li'><i></i><span><b>Curador de catálogo:</b> confere tabela × título e descrição e propõe quais veículos tirar.</span></div>
  <div class='li'><i></i><span><b>Modo sombra:</b> nada sai sem uma pessoa aprovar. Tudo registrado, com desfazer.</span></div>
 </div>
 <div class='sp'></div>{rodape(7, ln)}</div>""")
    if ln:
        fim = f"""<div class='sub' style='font-size:38px;color:var(--ink)'>Conheça o GestorPro para autopeças:</div>
 <div class='card' style='margin-top:22px;text-align:center;font:800 46px Inter;color:var(--green)'>Saiba mais: {LINK}</div>"""
    else:
        fim = """<div class='card' style='margin-top:30px;text-align:center;padding:56px 40px'>
  <div style='font-size:36px;font-weight:700;color:var(--ink2)'>Comenta</div>
  <div class='serif' style='font-size:190px;font-weight:800;color:var(--green);line-height:1.05'>PEÇA</div>
  <div style='font-size:34px;font-weight:700;color:var(--ink2)'>que eu te mando a página com a demonstração</div></div>"""
    s.append(f"""<div class='slide'>{cont(8)}
 <div class='kick'>Salve para a conferência antes da Black Friday</div>
 <h1 class='p'>Um time de agentes de IA no pós-venda da sua <em>loja de autopeças</em></h1>
 <div class='sub' style='font-size:36px'>GestorPro · Mercado Livre, Shopee, Magalu, Amazon e TikTok Shop, com várias lojas na mesma tela.</div>
 <div style='margin-top:34px'>{fim}</div>
 <div class='sp'></div>{rodape(8, ln)}</div>""")
    return s


def pagina(corpo, w=1080, h=1350, fundo='var(--paper)'):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}html,body{{width:{w}px;height:{h}px;background:{fundo}}}"
            f"</style></head><body>{corpo}</body></html>")


def render(pw, itens, pasta_html, pasta_png, w=1080, h=1350, transparente=False):
    os.makedirs(pasta_html, exist_ok=True)
    os.makedirs(pasta_png, exist_ok=True)
    b = pw.chromium.launch(channel='chrome')
    pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
    saidas = []
    for nome, corpo in itens:
        arq = os.path.join(pasta_html, nome + '.html')
        open(arq, 'w').write(pagina(corpo, w, h, 'transparent' if transparente else 'var(--paper)'))
        pg.goto('file://' + arq)
        pg.wait_for_timeout(900)
        out = os.path.join(pasta_png, nome + '.png')
        if transparente:
            pg.locator('.card').first.screenshot(path=out, omit_background=True)
        else:
            pg.screenshot(path=out)
        saidas.append(out)
    b.close()
    return saidas


def folha(pngs, out, col=4):
    ims = [Image.open(p).convert('RGB').resize((270, 338)) for p in pngs]
    lin = (len(ims) + col - 1) // col
    f = Image.new('RGB', (col * 280 + 10, lin * 348 + 10), (255, 255, 255))
    for i, im in enumerate(ims):
        f.paste(im, (10 + (i % col) * 280, 10 + (i // col) * 348))
    f.save(out)


if __name__ == '__main__':
    so = sys.argv[1] if len(sys.argv) > 1 else 'tudo'
    with sync_playwright() as pw:
        if so in ('tudo', 'carrossel'):
            pngs = render(pw, [('slide-%02d' % (i + 1), c) for i, c in enumerate(slides())],
                          os.path.join(AQUI, 'carrossel', 'html'), os.path.join(AQUI, 'carrossel', 'slides'))
            folha(pngs, os.path.join(AQUI, 'carrossel', 'folha.png'))
            for p in pngs:   # JPG para o agendador do Instagram
                Image.open(p).convert('RGB').save(p.replace('.png', '.jpg'), quality=92)
        if so in ('tudo', 'linkedin'):
            pngs = render(pw, [('doc-%02d' % (i + 1), c) for i, c in enumerate(slides(ln=True))],
                          os.path.join(AQUI, 'linkedin', 'html'), os.path.join(AQUI, 'linkedin', 'paginas'))
            ims = [Image.open(p).convert('RGB') for p in pngs]
            ims[0].save(os.path.join(AQUI, 'linkedin', 'autopecas-ia-tiops.pdf'), save_all=True, append_images=ims[1:], resolution=150)
        if so in ('tudo', 'cards'):
            cards = [('tabela', anuncio()), ('curador', curador()), ('atendente', atendente())]
            render(pw, [(n, f"<div style='padding:20px;width:1000px'>{c}</div>") for n, c in cards],
                   os.path.join(AQUI, 'reel', 'cards', 'html'), os.path.join(AQUI, 'reel', 'cards'), w=1040, h=1400, transparente=True)
    print('ok')
