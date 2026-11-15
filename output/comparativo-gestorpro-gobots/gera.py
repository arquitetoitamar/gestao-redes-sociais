#!/usr/bin/env python3
"""Gera o PDF comparativo GestorPro x GoBots (sem valores).

Fontes: ~/Downloads/GestorPro e GoBots.(md|html|pdf), 15/11/2026.
Regra: nenhum preço, custo, percentual, número de cliente ou valor em dinheiro.

  python3 gera.py      -> comparativo.html, comparativo-gestorpro-gobots.pdf, paginas/, folha.png
"""
import os, re, subprocess, glob
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(AQUI, 'comparativo.html')
PDF = os.path.join(AQUI, 'comparativo-gestorpro-gobots.pdf')
LINK = 'https://l.tiops.com.br/gestorpro?o=pdf-comparativo-gobots'

CSS = r"""
@page { size: A4; margin: 0; }
:root{
  --accent:#3f5ee8; --accent2:#7d93ff; --soft:#eef1fd; --ink:#12141a; --muted:#59617a; --dim:#727b93;
  --line:#e3e7f0; --line2:#cfd6e4; --bg:#f4f6fa; --other:#7a8197; --ok:#1f8a5b; --warn:#b46a00;
  --font:"Inter",-apple-system,"Segoe UI",sans-serif; --display:"Inter Tight","Inter",sans-serif;
  --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff;color:var(--ink);font-family:var(--font);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:16mm 16mm 18mm;position:relative;overflow:hidden;page-break-after:always;break-after:page}
.page:last-child{page-break-after:auto;break-after:auto}
.foot{position:absolute;left:16mm;right:16mm;bottom:8mm;display:flex;justify-content:space-between;font-size:7.5pt;color:var(--dim);border-top:1px solid var(--line);padding-top:2.5mm}
.kicker{font-family:var(--mono);font-size:7.5pt;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600}
h1{font-family:var(--display);font-weight:800;letter-spacing:-.02em}
h2{font-family:var(--display);font-size:19pt;line-height:1.15;font-weight:750;letter-spacing:-.015em;margin:2mm 0 3mm}
h3{font-family:var(--display);font-size:11pt;font-weight:700;margin-bottom:1.5mm}
p{font-size:9.6pt;line-height:1.5;color:var(--muted)}
.lead{font-size:10.5pt;line-height:1.55;color:var(--muted);max-width:165mm}
.small{font-size:8pt;color:var(--dim);line-height:1.45}
b,strong{color:var(--ink)}

/* capa */
.capa{padding:0;background:var(--bg)}
.capa .topo{padding:18mm 18mm 0}
.capa h1{font-size:40pt;line-height:1;margin:5mm 0 4mm}
.capa h1 span{color:var(--accent)}
.capa .tese{font-family:var(--display);font-size:20pt;line-height:1.18;font-weight:700;max-width:160mm;margin-bottom:4mm}
.capa .lead{max-width:168mm}
.capa .hero{margin:8mm 18mm 0;border-radius:5mm;overflow:hidden;border:1px solid var(--line2);background:#fff}
.capa .hero img{display:block;width:174mm;height:124mm;object-fit:cover}
.chips{display:flex;flex-wrap:wrap;gap:2.2mm;margin-top:6mm}
.chip{font-size:8.6pt;border:1px solid var(--line2);background:#fff;border-radius:20mm;padding:1.6mm 3.6mm;color:var(--muted)}
.chip b{color:var(--accent)}
.capa .rodape{position:absolute;left:18mm;right:18mm;bottom:12mm;display:flex;justify-content:space-between;align-items:flex-end;font-size:8.5pt;color:var(--dim)}
.marca{font-family:var(--display);font-weight:800;font-size:13pt;color:var(--ink)}
.marca span{color:var(--accent)}

/* resumo */
.cards3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm;margin:5mm 0 7mm}
.card{border:1px solid var(--line);border-radius:3.5mm;padding:4.5mm;background:#fff}
.card.hl{border-color:var(--accent2);background:var(--soft)}
.card .tag{font-family:var(--mono);font-size:7pt;letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin-bottom:2mm}
.card.hl .tag{color:var(--accent)}
.card p{font-size:9.2pt}

/* tabelas */
table{width:178mm;border-collapse:collapse;font-size:8.8pt}
th{font-family:var(--mono);font-size:7pt;letter-spacing:.12em;text-transform:uppercase;color:var(--dim);text-align:left;font-weight:600;padding:0 2.5mm 2mm;border-bottom:1.5px solid var(--line2)}
td{padding:2.6mm 2.5mm;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.4;color:var(--muted)}
td:first-child{color:var(--ink);font-weight:600}
td .nota{display:block;font-size:7.8pt;color:var(--dim);font-weight:400;margin-top:.6mm}
tr.grupo td{font-family:var(--mono);font-size:7pt;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700;padding-top:4mm;border-bottom:1px solid var(--line2)}
.v{font-weight:700}
.v.sim{color:var(--ok)} .v.nao{color:var(--other)} .v.ia{color:var(--accent)} .v.meio{color:var(--warn)}
.gp{background:#fafbff}

.mapa td{padding:3.4mm 2.5mm}
.dot{display:inline-block;width:3.1mm;height:3.1mm;border-radius:50mm;vertical-align:-0.5mm;margin-right:1.8mm;border:1.6px solid currentColor}
.dot.f{background:currentColor}
.dot.h{background:linear-gradient(90deg,currentColor 1.4mm,transparent 1.4mm)}
.dot.e{opacity:.55}
.c-gb{color:var(--other)} .c-gp{color:var(--accent)}
.legenda{display:flex;gap:6mm;margin-top:3mm;font-size:8pt;color:var(--dim)}

/* quem faz */
.quem td{padding:3.2mm 2.5mm}
.quem td b{display:block;margin-bottom:.6mm}
.quem td.gpcol b{color:var(--accent)}

.destaque{margin-top:7mm;border-radius:4mm;background:var(--ink);color:#fff;padding:7mm 8mm;display:grid;grid-template-columns:1fr;gap:2mm}
.destaque .kicker{color:var(--accent2)}
.destaque h2{color:#fff;font-size:16pt;margin:1mm 0 2mm}
.destaque p{color:#c9cfdf;font-size:9.6pt}

/* fluxo */
.fluxo-top{display:grid;grid-template-columns:62mm 1fr;gap:6mm;align-items:center;margin-bottom:4mm}
.fluxo-top img{width:62mm;height:35mm;object-fit:cover;border-radius:3mm;border:1px solid var(--line)}
svg.fluxo{width:178mm;height:auto;display:block}
.nota-gb{margin-top:3mm;border-left:3px solid var(--line2);padding:1.5mm 0 1.5mm 4mm}

/* devolução */
.formula{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;align-items:stretch;gap:2mm;margin:4mm 0 3mm}
.formula .t{border:1px solid var(--line);border-radius:3mm;padding:3.2mm;background:#fff}
.formula .t b{display:block;font-size:9.2pt;margin-bottom:.6mm}
.formula .t span{font-size:7.8pt;color:var(--dim);line-height:1.35;display:block}
.formula .op{align-self:center;font-family:var(--mono);font-size:15pt;color:var(--accent);font-weight:700}
.hipo{display:grid;grid-template-columns:1fr 1fr 1fr;gap:3mm}
.hipo .t{border-radius:3mm;padding:3.5mm;background:var(--soft);border:1px solid var(--accent2)}
.hipo .t.cinza{background:var(--bg);border-color:var(--line2)}
.hipo .t b{display:block;font-size:9.4pt;margin-bottom:.8mm}
.hipo .t span{font-size:8.4pt;color:var(--muted);line-height:1.4}

/* travas */
.travas{display:grid;grid-template-columns:1fr 1fr 1fr;gap:3.5mm;margin-top:4mm}
.trava{border:1px solid var(--line);border-radius:3mm;padding:4mm;background:#fff}
.trava .n{font-family:var(--mono);font-size:7.5pt;color:var(--accent);font-weight:700;margin-bottom:1.5mm}
.trava h3{font-size:10pt}
.trava p{font-size:8.6pt;line-height:1.45}

.conclusao{margin-top:7mm;display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.cta{margin-top:6mm;background:var(--accent);color:#fff;border-radius:4mm;padding:6mm 8mm;display:flex;justify-content:space-between;align-items:center}
.cta .t{font-family:var(--display);font-size:15pt;font-weight:750;line-height:1.2}
.cta .t span{display:block;font-family:var(--font);font-size:9pt;font-weight:400;color:#dfe5ff;margin-top:1mm}
.cta a{background:#fff;color:var(--accent);text-decoration:none;font-weight:700;font-size:10.5pt;border-radius:20mm;padding:3mm 6mm;white-space:nowrap}
.fontes{margin-top:6mm;font-size:7.6pt;color:var(--dim);line-height:1.5}
.fontes b{color:var(--muted)}
"""

def foot(n):
    return f'<div class="foot"><span>GestorPro × GoBots · comparativo</span><span>TiOps · página {n}</span></div>'

def v(txt):
    """Formata o valor de célula: sim / não / IA / agente / texto."""
    t = txt.lower()
    if t in ('sim',):
        cls = 'sim'
    elif t in ('não', 'não informado', 'fora do produto'):
        cls = 'nao'
    elif t in ('ia', 'agente', 'agentes'):
        cls = 'ia'
    else:
        cls = 'meio'
    return f'<span class="v {cls}">{txt}</span>'

def cel(valor, nota=''):
    n = f'<span class="nota">{nota}</span>' if nota else ''
    return v(valor) + n

# ---------- função por função (texto das fontes, sem valores) ----------
FUNCOES = [
    ('Pré-venda', [
        ('Resposta automática de pergunta', '', ('IA', ''), ('IA', 'reativa, em segundos; só fora do expediente, se você quiser')),
        ('Separa pergunta que é reclamação', '“cadê meu pedido?” no anúncio', ('não informado', ''), ('sim', '')),
        ('Aprende com as respostas da equipe, por anúncio', '', ('sim', ''), ('sim', 'com aprovação, origem e desfazer; preço e estoque nunca viram “fato”')),
        ('Tabela de compatibilidade decide a resposta', '', ('não informado', ''), ('sim', '')),
        ('Histórico do comprador ao lado da pergunta', '', ('sim', ''), ('sim', '')),
        ('Respostas prontas da equipe', '', ('sim', ''), ('sim', 'por anúncio ou família, e o agente segue como exemplo')),
        ('Testar a IA com uma pergunta livre', '', ('sim', ''), ('sim', 'mostra de onde saiu cada informação')),
        ('Quanto o time vendeu respondendo', '', ('sim', ''), ('sim', 'agentes e pessoas na mesma régua, com grupo de comparação')),
        ('Perguntas da Magalu', '', ('sim', ''), ('leitura', 'resposta em liberação')),
    ]),
    ('Pós-venda', [
        ('Agente responde reclamação e mediação no prazo', '', ('painel para a equipe', ''), ('IA', '')),
        ('Fila com responsável, nota interna e “resolver e ir para o próximo”', '', ('sim', ''), ('sim', 'mostra só o que o agente não resolveu')),
        ('“Afeta a reputação?” em cada caso', '', ('sim', ''), ('sim', 'e até quando resolver tira o peso')),
        ('Perda por devolução', '', ('selo de custo', ''), ('sim', 'com o custo cadastrado na própria linha')),
        ('Nota fiscal de devolução e CT-e na reclamação', '', ('não informado', ''), ('sim', '')),
        ('Exportar listas em planilha', '', ('sim', ''), ('sim', '')),
    ]),
    ('O resto da operação', [
        ('Margem real por pedido', 'taxa, frete, imposto, custo, repasse do canal', ('não', ''), ('sim', '')),
        ('Promoções decididas pelo lucro medido da loja', '', ('não', ''), ('agente', '')),
        ('Anúncios pagos', '', ('sugestões', ''), ('agente', '')),
        ('Estoque, ruptura e catálogo', '', ('não', ''), ('agentes', '')),
        ('Configurar pelo seu Claude ou ChatGPT', '', ('não', ''), ('sim', '')),
    ]),
    ('O que o GestorPro não faz, de propósito', [
        ('Envio em massa para lista de CPF', 'o Mercado Livre só deixa a loja iniciar conversa uma vez, entre o pagamento e a entrega', ('sim', ''), ('não', 'mensagem por gatilho, na janela certa')),
        ('Mensagem de ausência no chat', 'o canal recusa mensagem automática, e a loja fala duas vezes seguidas', ('sim', ''), ('não', 'o agente responde no horário que você escolher')),
        ('Aviso sonoro a cada pergunta e venda', '', ('sim', ''), ('não', 'você é avisado só do que precisa decidir')),
    ]),
]

def tabela_funcoes(grupos):
    linhas = []
    for nome, itens in grupos:
        linhas.append(f'<tr class="grupo"><td colspan="3">{nome}</td></tr>')
        for func, sub, gb, gp in itens:
            s = f'<span class="nota">{sub}</span>' if sub else ''
            linhas.append(f'<tr><td style="width:72mm">{func}{s}</td><td style="width:40mm">{cel(*gb)}</td><td class="gp">{cel(*gp)}</td></tr>')
    return ('<table><thead><tr><th>Função</th><th>GoBots</th><th>GestorPro</th></tr></thead><tbody>'
            + ''.join(linhas) + '</tbody></table>')

# ---------- mapa da operação ----------
MAPA = [
    ('Perguntas', ('f', 'IA responde; a equipe revisa depois'), ('f', 'Atendente responde')),
    ('Chat do pedido', ('f', 'IA faz a triagem'), ('f', 'Atendente responde no expediente escolhido')),
    ('Reclamações e mediação', ('h', 'Painel para a equipe'), ('f', 'Atendente responde; você decide a solução')),
    ('Devoluções', ('h', 'Lista com situação'), ('f', 'Mostra quanto a loja perde e o que fazer')),
    ('Anúncios pagos', ('h', 'Sugestões'), ('f', 'Agente cuida')),
    ('Margem por pedido', ('e', 'Fora do produto'), ('f', 'Agente cuida')),
    ('Promoções', ('e', 'Fora do produto'), ('f', 'Agente cuida')),
    ('Estoque e ruptura', ('e', 'Fora do produto'), ('f', 'Agentes cuidam')),
    ('Catálogo e anúncios', ('e', 'Fora do produto'), ('f', 'Agentes cuidam')),
    ('Repasses e taxas', ('e', 'Fora do produto'), ('f', 'Entram na margem de cada pedido')),
]

def tabela_mapa():
    ls = []
    for area, (eg, tg), (ep, tp) in MAPA:
        ls.append(f'<tr><td style="width:46mm">{area}</td>'
                  f'<td class="c-gb" style="width:62mm"><i class="dot {eg}"></i><span style="color:var(--muted)">{tg}</span></td>'
                  f'<td class="c-gp gp"><i class="dot {ep}"></i><span style="color:var(--ink)">{tp}</span></td></tr>')
    return ('<table class="mapa"><thead><tr><th>Área da loja</th><th>GoBots</th><th>GestorPro</th></tr></thead><tbody>'
            + ''.join(ls) + '</tbody></table>')

# ---------- fluxo de atendimento (SVG) ----------
def svg_fluxo():
    A = '#3f5ee8'; INK = '#12141a'; MU = '#59617a'; DIM = '#727b93'; LN = '#cfd6e4'; SOFT = '#eef1fd'
    def caixa(x, y, w, h, n, titulo, linhas, fill='#fff', stroke=LN):
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>']
        tx = x + 16
        if n:
            out.append(f'<circle cx="{x+26}" cy="{y+24}" r="12" fill="{A}"/>'
                       f'<text x="{x+26}" y="{y+28.5}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">{n}</text>')
            tx = x + 46
        out.append(f'<text x="{tx}" y="{y+29}" font-size="15.5" font-weight="700" fill="{INK}">{titulo}</text>')
        for i, l in enumerate(linhas):
            out.append(f'<text x="{x+18}" y="{y+54+i*19}" font-size="12.6" fill="{MU}">{l}</text>')
        return ''.join(out)
    def lado(x, y, w, h, linhas):
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f4f6fa" stroke="{LN}" stroke-dasharray="5 4"/>']
        for i, l in enumerate(linhas):
            out.append(f'<text x="{x+14}" y="{y+24+i*18}" font-size="12" fill="{MU}">{l}</text>')
        return ''.join(out)
    def seta(d):
        return f'<path d="{d}" fill="none" stroke="{A}" stroke-width="1.8" marker-end="url(#ponta)"/>'
    def tseta(x1, y1, x2, y2):
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{DIM}" stroke-width="1.3" stroke-dasharray="4 4" marker-end="url(#pontac)"/>'
    def pill(x, w, t):
        return (f'<rect x="{x}" y="8" width="{w}" height="40" rx="20" fill="{SOFT}" stroke="{A}" stroke-width="1.2"/>'
                f'<text x="{x+w/2}" y="33" text-anchor="middle" font-size="13.2" font-weight="600" fill="{INK}">{t}</text>')
    s = []
    s.append('<defs><marker id="ponta" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{A}"/></marker>'
             '<marker id="pontac" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{DIM}"/></marker></defs>')
    # entradas
    s.append(pill(10, 215, 'Pergunta no anúncio'))
    s.append(pill(245, 215, 'Mensagem no chat do pedido'))
    s.append(pill(480, 230, 'Reclamação ou mediação'))
    s.append(seta('M117,48 C117,66 200,62 225,84'))
    s.append(seta('M352,48 C352,66 275,62 255,84'))
    s.append(seta('M595,48 C595,70 330,58 270,86'))
    # 1 separa
    s.append(caixa(10, 88, 470, 82, '1', 'Separa o caso', [
        'Pergunta que é reclamação (“cadê meu pedido?”)',
        'não vira resposta pública no anúncio.']))
    s.append(tseta(480, 129, 506, 129))
    s.append(lado(510, 96, 200, 66, ['Caso já está com alguém', 'da equipe? O agente', 'não fala nele.']))
    s.append(seta('M245,170 L245,194'))
    # 2 contexto
    s.append(caixa(10, 198, 470, 112, '2', 'Lê o contexto', []))
    chips = [('Ficha do anúncio', 28, 256), ('Tabela de compatibilidade', 236, 256),
             ('O que a equipe ensinou', 28, 288), ('Histórico do comprador', 236, 288)]
    for t, x, y in chips:
        s.append(f'<rect x="{x}" y="{y-17}" width="{198 if x==28 else 226}" height="25" rx="7" fill="{SOFT}"/>'
                 f'<text x="{x+11}" y="{y+0.5}" font-size="12.4" fill="{INK}">{t}</text>')
    s.append(tseta(480, 254, 506, 254))
    s.append(lado(510, 221, 200, 66, ['Preço e estoque nunca', 'viram “fato” no que', 'o agente aprende.']))
    s.append(seta('M245,310 L245,334'))
    # 3 travas
    s.append(caixa(10, 338, 470, 116, '3', 'Passa pelas travas', [
        '• Nunca fala duas vezes seguidas no mesmo caso.',
        '• Responde na janela do canal e no expediente escolhido.',
        '• Troca, reembolso e devolução nunca em texto livre.']))
    s.append(tseta(480, 396, 506, 396))
    s.append(lado(510, 363, 200, 66, ['No começo o agente', 'prepara e você aprova.', 'Age sozinho quando você liga.']))
    # saídas
    s.append(seta('M245,454 C245,474 120,468 117,492'))
    s.append(seta('M245,454 L360,492'))
    s.append(seta('M245,454 C260,474 590,464 600,492'))
    saidas = [(10, 'Responde e publica', ['Pergunta: em segundos.', 'Chat: na janela do canal.']),
              (247, 'Prepara a solução', ['Troca, reembolso ou devolução:', 'você decide com um clique.']),
              (484, 'Avisa você', ['O que precisa de você vira aviso.', 'Prazo não vence calado.'])]
    for x, t, ls in saidas:
        s.append(f'<rect x="{x}" y="496" width="226" height="86" rx="12" fill="#fff" stroke="{A}" stroke-width="1.6"/>'
                 f'<text x="{x+16}" y="524" font-size="14.5" font-weight="700" fill="{A}">{t}</text>')
        for i, l in enumerate(ls):
            s.append(f'<text x="{x+16}" y="{548+i*18}" font-size="12.2" fill="{MU}">{l}</text>')
    # registro
    s.append(seta('M360,582 L360,604'))
    s.append(f'<rect x="10" y="608" width="700" height="58" rx="12" fill="{INK}"/>'
             f'<text x="30" y="633" font-size="14" font-weight="700" fill="#fff">Tudo fica no histórico, com o motivo, e pode ser desfeito.</text>'
             f'<text x="30" y="654" font-size="12.2" fill="#c9cfdf">A equipe ensina pelas próprias respostas; o agente aprende com a sua aprovação.</text>')
    return ('<svg class="fluxo" viewBox="0 0 720 674" xmlns="http://www.w3.org/2000/svg" '
            'font-family="Inter, -apple-system, Segoe UI, sans-serif">' + ''.join(s) + '</svg>')

QUEM = [
    ('Pergunta no anúncio',
     ('IA responde', 'Responde e envia; a equipe revisa depois.'),
     ('Atendente responde', 'Usa a ficha, a tabela de compatibilidade e o que a equipe ensinou. Pergunta que é reclamação não vira resposta pública.')),
    ('Chat do pedido',
     ('IA faz a triagem', 'Menu de assuntos e mensagem de ausência; passa para a equipe.'),
     ('Atendente no expediente que você escolher', 'Responde dentro da janela que o canal permite, sem mensagem automática que o canal recusa.')),
    ('Reclamação e mediação',
     ('Painel para a equipe', 'Prazo, motivo e responsável organizados para quem atende.'),
     ('Atendente responde, você decide a solução', 'Escreve no prazo, nunca fala duas vezes seguidas e traz troca, reembolso ou devolução para você decidir com um clique.')),
    ('Devolução',
     ('Lista com situação', 'Selo de “custo não cadastrado”.'),
     ('Quanto a loja perde, e o que fazer', 'Custo, frete de ida e volta e o que o canal cobriu. Falta o custo? Cadastra ali mesmo.')),
    ('Margem, promoção, estoque',
     ('Fora do produto', ''),
     ('Agentes cuidam', 'Entram e saem de promoção pelo lucro medido da loja, apontam ruptura e o pedido que deu prejuízo.')),
]

def tabela_quem():
    ls = []
    for trab, (gt, gd), (pt, pd) in QUEM:
        ls.append(f'<tr><td style="width:36mm">{trab}</td>'
                  f'<td style="width:62mm"><b>{gt}</b>{gd}</td>'
                  f'<td class="gp gpcol"><b>{pt}</b>{pd}</td></tr>')
    return ('<table class="quem"><thead><tr><th>Trabalho</th><th>GoBots</th><th>GestorPro</th></tr></thead><tbody>'
            + ''.join(ls) + '</tbody></table>')

TRAVAS = [
    ('Nunca fala duas vezes seguidas', 'A vez de falar é de quem a conversa diz. Mensagem repetida no mesmo caso é bloqueada.'),
    ('Solução é sempre sua', 'Troca, reembolso e devolução são escolhidos por você. O agente nunca oferece em texto livre.'),
    ('A tabela do anúncio decide', '“Serve no meu carro?” é respondido pela tabela de compatibilidade, nunca por suposição.'),
    ('Tudo registrado e desfazível', 'Cada ação dos agentes fica no histórico, com o motivo, e pode ser desfeita.'),
    ('Começa sugerindo', 'No início o agente prepara e você aprova. Ele só passa a agir sozinho quando você liga.'),
    ('Prazo não vence calado', 'Caso que precisa de você chega como aviso, e só conta como avisado quando o aviso chegou.'),
]

def html():
    paginas = []
    # 1 capa
    paginas.append(f'''
<section class="page capa">
  <div class="topo">
    <div class="kicker">Comparativo · novembro de 2026</div>
    <h1>GestorPro <span>×</span> GoBots</h1>
    <div class="tese">Atendimento é uma parte da loja. O GestorPro cuida dela inteira.</div>
    <p class="lead">O GoBots é uma boa ferramenta de atendimento com IA. O GestorPro é um time de agentes que atende o comprador e também cuida de margem, promoção, estoque, anúncios e anúncios pagos, com você decidindo só o que eles não podem decidir.</p>
    <div class="chips">
      <span class="chip"><b>Mercado Livre</b>, Shopee, Magalu, Amazon, Shein e TikTok</span>
      <span class="chip"><b>10 agentes</b> num escritório</span>
      <span class="chip">Tudo registrado e <b>desfazível</b></span>
    </div>
  </div>
  <div class="hero"><img src="img/agentes-escritorio.jpg" alt="Agentes de IA trabalhando: preço, estoque, catálogo e atendimento"></div>
  <div class="rodape"><span class="marca">Gestor<span>Pro</span> · TiOps</span><span>Agentes de IA cuidando de preço, estoque, catálogo e atendimento.</span></div>
</section>''')
    # 2 resumo + mapa
    paginas.append(f'''
<section class="page">
  <div class="kicker">Em resumo</div>
  <h2>Duas propostas diferentes para a mesma loja</h2>
  <div class="cards3">
    <div class="card"><div class="tag">GoBots</div><h3>Atendimento com IA</h3><p>Responde perguntas, faz a triagem do chat e organiza o pós-venda para a equipe atender.</p></div>
    <div class="card hl"><div class="tag">GestorPro</div><h3>Time de agentes</h3><p>Atende o comprador e também cuida de margem, promoção, estoque, catálogo e anúncios pagos.</p></div>
    <div class="card"><div class="tag">Quem decide</div><h3>Você, no que importa</h3><p>Os agentes resolvem o que podem. Troca, reembolso e devolução são sempre escolhidos por você.</p></div>
  </div>
  <div class="kicker">Mapa da operação da loja</div>
  <h2 style="font-size:15pt">O que cada um cobre</h2>
  {tabela_mapa()}
  <div class="legenda">
    <span><i class="dot f" style="color:var(--ink)"></i>IA ou agente faz</span>
    <span><i class="dot h" style="color:var(--ink)"></i>organiza para a equipe ou sugere</span>
    <span><i class="dot e" style="color:var(--ink)"></i>fora do produto</span>
  </div>
  {foot(2)}
</section>''')
    # 3 quem faz o quê
    paginas.append(f'''
<section class="page">
  <div class="kicker">Quem faz o quê</div>
  <h2>A sua equipe e os agentes trabalham como um time só</h2>
  <p class="lead" style="margin-bottom:5mm">Cada tipo de trabalho tem dono: um agente, uma pessoa, ou o agente prepara e a pessoa decide. Quando um caso está com alguém da equipe, o agente não fala nele.</p>
  {tabela_quem()}
  <div class="destaque">
    <div class="kicker">Pós-venda</div>
    <h2>O pós-venda é onde a loja perde dinheiro. É lá que o Atendente do GestorPro trabalha sozinho.</h2>
    <p>Reclamação e mediação têm prazo do canal e pesam na reputação. Numa conta real de um grande vendedor do Mercado Livre, o Atendente de pós-venda passou a responder no lugar do lojista, e só traz para a equipe o que precisa de decisão.</p>
  </div>
  {foot(3)}
</section>''')
    # 4 fluxo
    paginas.append(f'''
<section class="page">
  <div class="fluxo-top">
    <img src="img/agente-atendimento.jpg" alt="Agente de atendimento respondendo mensagens">
    <div>
      <div class="kicker">Fluxo de atendimento automático</div>
      <h2 style="margin-bottom:2mm">Da mensagem do comprador à resposta, sem a loja escrever</h2>
      <p>Como o Atendente do GestorPro trata cada pergunta, mensagem e reclamação.</p>
    </div>
  </div>
  {svg_fluxo()}
  <p class="small nota-gb">No GoBots, a IA responde perguntas no anúncio e faz a triagem do chat do pedido; reclamações e mediações vão para um painel organizado para a equipe atender.</p>
  {foot(4)}
</section>''')
    # 5 função por função (1)
    paginas.append(f'''
<section class="page">
  <div class="kicker">Função por função</div>
  <h2>O que cada um tem</h2>
  <p class="small" style="margin-bottom:4mm">Conferido no GestorPro em novembro de 2026. Do GoBots, o que o site e o produto mostram.</p>
  {tabela_funcoes(FUNCOES[:2])}
  {foot(5)}
</section>''')
    # 6 função por função (2) + devolução
    paginas.append(f'''
<section class="page">
  <div class="kicker" style="margin-bottom:4mm">Função por função · continuação</div>
  {tabela_funcoes(FUNCOES[2:])}
  <div style="margin-top:8mm">
    <div class="kicker">Devolução sem chute</div>
    <h2 style="font-size:15pt">“Custo não cadastrado” deixa de ser um selo e vira uma conta com saída</h2>
    <p>Cada devolução mostra quanto a loja perde em duas hipóteses. O que o sistema não sabe, ele diz que falta. Nunca chuta um número.</p>
    <div class="formula">
      <div class="t"><b>Custo do produto</b><span>cadastrado por SKU</span></div><div class="op">+</div>
      <div class="t"><b>Frete de ida</b><span>pago na venda</span></div><div class="op">+</div>
      <div class="t"><b>Frete de volta</b><span>cobrado na devolução</span></div><div class="op">−</div>
      <div class="t"><b>O que o canal cobriu</b><span>quando cobre</span></div>
    </div>
    <div class="hipo">
      <div class="t"><b>Voltou vendável</b><span>A perda é o frete de ida e o de volta, menos o que o canal cobriu.</span></div>
      <div class="t"><b>Não voltou vendável</b><span>Soma também o custo do produto.</span></div>
      <div class="t cinza"><b>Sem custo cadastrado?</b><span>A tela diz que falta e mostra o campo para cadastrar na própria linha.</span></div>
    </div>
  </div>
  {foot(6)}
</section>''')
    # 7 travas + conclusão
    travas = ''.join(f'<div class="trava"><div class="n">{i+1:02d}</div><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(TRAVAS))
    paginas.append(f'''
<section class="page">
  <div class="kicker">O que protege a sua conta</div>
  <h2>Um agente útil é o modelo mais as travas em volta dele</h2>
  <p class="lead">Trocar o modelo de IA não muda nada disto. É o que deixa um agente escrever no seu canal sem você ficar de olho.</p>
  <div class="travas">{travas}</div>
  <div class="conclusao">
    <div class="card"><div class="tag">Quando o GoBots atende bem</div><p>Para quem precisa de uma boa ferramenta de atendimento com IA: responder perguntas, fazer a triagem do chat e organizar o pós-venda para a equipe.</p></div>
    <div class="card hl"><div class="tag">Onde o GestorPro vai além</div><p>Para quem quer agentes cuidando da loja inteira: pós-venda no prazo, margem por pedido, promoções, estoque, catálogo e anúncios pagos, com você decidindo só o que eles não podem decidir.</p></div>
  </div>
  <div class="cta">
    <div class="t">Veja o escritório de agentes do GestorPro<span>Mercado Livre, Shopee, Magalu, Amazon, Shein e TikTok.</span></div>
    <a href="{LINK}">Saiba mais · l.tiops.com.br/gestorpro</a>
  </div>
  <div class="fontes"><b>Fontes.</b> Informações do GoBots: site público (gobots.ai) e produto, consultados em 15/11/2026. Funções do GestorPro conferidas no produto em novembro de 2026. O caso de pós-venda vem de uma conta de cliente acompanhada em setembro e outubro de 2026, com o nome omitido. Imagens ilustrativas geradas por IA. GestorPro é um produto da TiOps.</div>
  {foot(7)}
</section>''')
    return ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>GestorPro × GoBots</title>'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Inter+Tight:wght@700;800&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">'
            f'<style>{CSS}</style></head><body>' + ''.join(paginas) + '</body></html>')


def main():
    doc = html()
    open(HTML, 'w', encoding='utf-8').write(doc)
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        pg = b.new_page()
        pg.goto('file://' + HTML, wait_until='networkidle')
        pg.evaluate('document.fonts.ready')
        # confere estouro de conteúdo em cada página
        estouro = pg.evaluate('''() => [...document.querySelectorAll('.page')].map((el,i) => {
            const foot = el.querySelector('.foot');
            const limite = foot ? foot.getBoundingClientRect().top : el.getBoundingClientRect().bottom;
            let maior = 0;
            el.querySelectorAll('*').forEach(c => { if (c.closest('.foot')) return; const r = c.getBoundingClientRect(); if (r.height) maior = Math.max(maior, r.bottom); });
            return {pagina: i+1, sobra_px: Math.round(limite - maior)};
        })''')
        for e in estouro:
            print('página %(pagina)d: sobra %(sobra_px)d px antes do rodapé' % e)
        pg.pdf(path=PDF, format='A4', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        b.close()
    pasta = os.path.join(AQUI, 'paginas')
    os.makedirs(pasta, exist_ok=True)
    for f in glob.glob(os.path.join(pasta, '*.png')):
        os.remove(f)
    subprocess.run(['pdftoppm', '-r', '70', '-png', PDF, os.path.join(pasta, 'p')], check=True)
    from PIL import Image
    ims = [Image.open(f) for f in sorted(glob.glob(os.path.join(pasta, 'p-*.png')))]
    w, h = ims[0].size
    cols = 4
    rows = (len(ims) + cols - 1) // cols
    folha = Image.new('RGB', (w * cols + 10 * (cols + 1), h * rows + 10 * (rows + 1)), (200, 204, 214))
    for i, im in enumerate(ims):
        folha.paste(im, (10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 10)))
    folha.save(os.path.join(AQUI, 'folha.png'))
    # checagem: nada de valor
    proib = re.compile(r'R\$|US\$|%|reais|mensal|/mês')
    achados = proib.findall(doc)
    txt = subprocess.run(['pdftotext', PDF, '-'], capture_output=True, text=True).stdout
    achados_pdf = proib.findall(txt)
    print('páginas:', len(ims), '| proibidos no HTML:', achados, '| no PDF:', achados_pdf)


if __name__ == '__main__':
    main()
