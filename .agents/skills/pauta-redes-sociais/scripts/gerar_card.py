#!/usr/bin/env python3
"""Gera card de notícia (feed 4:5 e story 9:16) a partir de um JSON.

Uso: python3 gerar_card.py pauta.json pasta_saida/

pauta.json:
{
  "tag": "IA & INFRAESTRUTURA",
  "titulo": "A corrida da IA agora é por infraestrutura",
  "destaque": "US$ 1 bi",
  "destaque_legenda": "Samsung + 5 empresas do grupo na Helix (KKR)",
  "bullets": ["Data centers, energia e fibra óptica", "..."],
  "fonte": "Fonte: @danielmaehara"
}
Saída: post_4x5.jpg (1080x1350) e story_9x16.jpg (1080x1920).
"""
import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{width:1080px;height:{h}px;background:radial-gradient(circle at 80% 0%,#1d4ed8 0%,#0b1020 55%);
font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;color:#fff;padding:{pad}px 80px;
display:flex;flex-direction:column;justify-content:space-between}}
.tag{{display:inline-block;background:#22d3ee;color:#06202a;font-weight:800;font-size:30px;
letter-spacing:2px;padding:12px 24px;border-radius:10px}}
h1{{font-size:{ts}px;line-height:1.05;font-weight:900;margin-top:40px}}
.num{{font-size:150px;font-weight:900;color:#22d3ee;line-height:1;margin-top:30px}}
.numl{{font-size:34px;color:#cbd5e1;margin-top:10px}}
ul{{list-style:none;margin-top:40px}}
li{{font-size:38px;line-height:1.3;margin-bottom:22px;padding-left:46px;position:relative;color:#e2e8f0}}
li:before{{content:'→';position:absolute;left:0;color:#22d3ee;font-weight:900}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:30px;color:#94a3b8}}
.brand{{font-weight:900;color:#fff;font-size:38px}}
</style></head><body>
<div><span class="tag">{tag}</span><h1>{titulo}</h1>
<div class="num">{destaque}</div><div class="numl">{destaque_legenda}</div>
<ul>{bullets}</ul></div>
<div class="foot"><span>{fonte}</span><span class="brand">@tiopstecnologia</span></div>
</body></html>"""


def render(d, h, pad, ts, destino):
    e = lambda k: html.escape(d.get(k, ""))
    doc = TEMPLATE.format(
        h=h, pad=pad, ts=ts, tag=e("tag"), titulo=e("titulo"), destaque=e("destaque"),
        destaque_legenda=e("destaque_legenda"), fonte=e("fonte"),
        bullets="".join(f"<li>{html.escape(b)}</li>" for b in d.get("bullets", [])),
    )
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": h})
        pg.set_content(doc)
        pg.screenshot(path=str(destino), type="jpeg", quality=92)
        b.close()


if __name__ == "__main__":
    pauta = json.loads(Path(sys.argv[1]).read_text())
    saida = Path(sys.argv[2])
    saida.mkdir(parents=True, exist_ok=True)
    render(pauta, 1350, 90, 84, saida / "post_4x5.jpg")
    render(pauta, 1920, 200, 92, saida / "story_9x16.jpg")
    print(f"ok: {saida}/post_4x5.jpg e story_9x16.jpg")
