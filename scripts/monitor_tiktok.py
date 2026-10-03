#!/usr/bin/env python3
"""Monitora contas do TikTok: detecta vídeos novos, baixa e gera digest em Markdown.

Uso:
    python3 scripts/monitor_tiktok.py                 # contas do CONTAS abaixo
    python3 scripts/monitor_tiktok.py outra_conta     # conta avulsa
    python3 scripts/monitor_tiktok.py --sem-download  # só lista/registra

Estado e saídas: output/monitor-tiktok/<conta>/
    estado.json   ids já vistos
    videos/       MP4 baixados
    digest.md     histórico (novos no topo)
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CONTAS = ["danielmaehara"]
ULTIMOS = 40
RAIZ = Path(__file__).resolve().parent.parent / "output" / "monitor-tiktok"


def listar(conta):
    r = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--playlist-end", str(ULTIMOS), "-J",
         f"https://www.tiktok.com/@{conta}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(f"[{conta}] yt-dlp falhou: {r.stderr[-400:]}")
    return json.loads(r.stdout).get("entries", [])


def baixar(conta, vid, pasta):
    pasta.mkdir(parents=True, exist_ok=True)
    url = f"https://www.tiktok.com/@{conta}/video/{vid}"
    r = subprocess.run(
        ["yt-dlp", "-o", str(pasta / f"{vid}.%(ext)s"), url],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def monitorar(conta, download=True):
    base = RAIZ / conta
    base.mkdir(parents=True, exist_ok=True)
    arq_estado = base / "estado.json"
    vistos = set(json.loads(arq_estado.read_text())) if arq_estado.exists() else set()
    primeira_vez = not vistos

    entradas = listar(conta)
    novos = [e for e in entradas if e["id"] not in vistos]

    linhas = []
    for e in novos:
        vid = e["id"]
        data = datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d %H:%M") if e.get("timestamp") else "?"
        ok = baixar(conta, vid, base / "videos") if download else False
        linhas.append(
            f"- **{data}** · [{vid}](https://www.tiktok.com/@{conta}/video/{vid})"
            f" · {e.get('view_count', 0)} views · {e.get('like_count', 0)} likes"
            f" · {e.get('duration', 0)}s · {'baixado' if ok else 'não baixado'}\n"
            f"  - Legenda: {(e.get('description') or e.get('title') or '(sem legenda)').strip()}\n"
            f"  - Áudio: {e.get('track', '')}"
        )

    if linhas:
        arq_digest = base / "digest.md"
        antigo = arq_digest.read_text() if arq_digest.exists() else f"# @{conta}\n"
        cab, _, resto = antigo.partition("\n")
        bloco = f"\n## {datetime.now():%Y-%m-%d %H:%M}" + (" (carga inicial)" if primeira_vez else "") + "\n" + "\n".join(linhas) + "\n"
        arq_digest.write_text(cab + "\n" + bloco + resto)

    arq_estado.write_text(json.dumps(sorted(vistos | {e["id"] for e in entradas})))
    print(f"[{conta}] {len(novos)} novo(s) de {len(entradas)} lidos" + (" (carga inicial)" if primeira_vez else ""))
    return novos


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for c in args or CONTAS:
        monitorar(c, download="--sem-download" not in sys.argv)
