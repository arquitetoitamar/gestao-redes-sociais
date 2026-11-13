#!/usr/bin/env python3
"""Peças sem o Itamar para a página da TiOps (regra de 13/11/2026: a página é da marca).

- heroi do slide 1 do Estúdio: os 3 painéis da arte, sem a pessoa que aparecia ao lado;
- imagem da MadeiraMadeira: tela da demonstração (o vídeo tinha rosto e voz do Itamar);
- imagem do Emissor NF-e: print da nota autorizada em homologação (o vídeo tinha a voz clonada
  e a saudação "itamar silva" do Claude).
"""
import os
from PIL import Image
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(AQUI)
TRAB = os.path.join(AQUI, 'trab')
PECAS = os.path.join(AQUI, 'pecas')
ROBO = 'file://' + os.path.join(OUT, 'post-estudio-operacao-ia', 'assets', 'tiops-robo.png')


def heroi():
    a = os.path.join(OUT, 'post-estudio-operacao-ia', 'assets')
    ims = [Image.open(os.path.join(a, f + '.png')).convert('RGBA') for f in ('esq', 'meio', 'dir')]
    h = 690
    ims = [i.resize((int(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    gap = 24
    W = Image.new('RGBA', (sum(i.width for i in ims) + gap * 2, h), (0, 0, 0, 0))
    x = 0
    for i in ims:
        W.paste(i, (x, 0), i)
        x += i.width + gap
    dest = os.path.join(TRAB, 'heroi-estudio.png')
    W.save(dest)
    return dest


def recortes():
    import subprocess
    mad = os.path.join(TRAB, 'mad_demo.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'reel-madeiramadeira', 'reel_madeiramadeira.mp4'),
                    '-vf', "select='eq(n\\,470)',crop=1080:1060:0:190", '-fps_mode', 'passthrough', '-frames:v', '1', mad], check=True)
    nfe = os.path.join(TRAB, 'nfe_autorizada.png')
    Image.open(os.path.join(OUT, 'reel-nfe-claude', 'captura', 'f01950.jpg')).convert('RGB').crop((40, 330, 1640, 1260)).save(nfe)
    return mad, nfe


CSS = """
:root{--bg:#060B1C;--azul:#1F6BFF;--ciano:#3CCBFF;--cinza:#9AA7C2}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:-apple-system,"SF Pro Display","Helvetica Neue",Arial,sans-serif;color:#fff;
 background:radial-gradient(900px 700px at 85% 8%,rgba(31,107,255,.40) 0%,rgba(31,107,255,0) 65%),
            radial-gradient(800px 600px at 0% 100%,rgba(60,203,255,.16) 0%,rgba(60,203,255,0) 60%),var(--bg);
 padding:72px 72px 0;display:flex;flex-direction:column}
.tag{display:inline-block;align-self:flex-start;border:2px solid var(--ciano);color:var(--ciano);font-weight:900;font-size:22px;letter-spacing:3px;padding:10px 24px;border-radius:999px;margin-bottom:24px}
h1{font-size:60px;font-weight:900;line-height:1.06;letter-spacing:-1.8px}
.hl{color:var(--ciano)}
.sub{font-size:28px;line-height:1.35;font-weight:600;color:#C9D3EA;margin:18px 0 28px}
.foto{display:block;width:936px;border-radius:24px;border:2px solid rgba(60,203,255,.45);
 box-shadow:0 0 0 8px rgba(60,203,255,.06),0 30px 70px rgba(0,0,0,.55),0 0 80px rgba(31,107,255,.35)}
.nota{font-size:20px;color:#5E6B8A;margin-top:12px;text-align:right}
.sp{flex:1}
.rod{height:92px;margin:0 -72px;padding:0 60px;display:flex;align-items:center;gap:16px;font-size:24px;font-weight:800;color:var(--cinza)}
.rod img{height:50px}.rod .dir{margin-left:auto;color:#fff}
"""


def cartao(nome, tag, titulo, sub, img, nota, direita, largura=936):
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="tag">{tag}</div><h1>{titulo}</h1><p class="sub">{sub}</p>
<img class="foto" src="file://{img}" style="width:{largura}px;align-self:center"><p class="nota" style="width:{largura}px;align-self:center">{nota}</p><div class="sp"></div>
<div class="rod"><img src="{ROBO}">TiOps Tecnologia<span class="dir">{direita}</span></div></body></html>"""
    arq = os.path.join(TRAB, nome + '.html')
    open(arq, 'w', encoding='utf-8').write(html)
    return arq


def main():
    heroi()
    mad, nfe = recortes()
    pares = [
        ('madeiramadeira', cartao('madeiramadeira', 'NOVIDADE',
            'A MadeiraMadeira chegou ao <span class="hl">Marketplace Connect.</span>',
            'Pedidos do dia e produtos sem estoque da MadeiraMadeira, junto com o Mercado Livre, numa conversa só com o Claude ou o ChatGPT.',
            mad, 'Exemplo ilustrativo.', 'Marketplace Connect', largura=800)),
        ('emissor-nfe', cartao('emissor-nfe', 'EMISSOR NF-E',
            'NF-e emitida <span class="hl">conversando com o Claude.</span>',
            'Prévia sem gastar número, alertas antes de emitir e nota autorizada na SEFAZ, com número e protocolo.',
            nfe, 'Ambiente de homologação. Cliente, pedido e valores de teste.', 'nfe.tiops.com.br')),
    ]
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for nome, arq in pares:
            pg.goto('file://' + arq)
            pg.wait_for_timeout(300)
            png = os.path.join(TRAB, nome + '.png')
            pg.screenshot(path=png)
            Image.open(png).convert('RGB').save(os.path.join(PECAS, nome + '-linkedin.jpg'), quality=93)
            print(os.path.join(PECAS, nome + '-linkedin.jpg'))
        b.close()


if __name__ == '__main__':
    main()
