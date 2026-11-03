"""Monta build/timeline.js a partir das falas reais (tempo de cada palavra da HeyGen).
uso: python3 timeline.py ar|mx   (lê narracao_<v>.json e audio_<v>/)
Cenas = respiro + fala + respiro. Telas de palavra entram entre cenas, só com música.
Cues = início exato da palavra onde começa cada trecho-chave. Legenda = palavras em blocos."""
import json, subprocess, sys, re, unicodedata

V = sys.argv[1] if len(sys.argv) > 1 else "ar"
NARR = {n["id"]: n for n in json.load(open(f"narracao_{V}.json"))}
INTER = json.load(open(f"inter_{V}.json"))  # {"i1": ["PALABRA.", "estilo", dur], ...}

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))

PLAN = [("s0", "n0", 0.20, 0.30), ("s1", "n1", 0.25, 0.55), "i1", ("s2", "n2", 0.20, 0.45), "i2",
        ("s3", "n3", 0.20, 1.30), "i3", ("s4", "n4", 0.20, 1.20), "i4", ("s6", "n6", 0.20, 0.90),
        ("s7", "n7", 0.40, 2.60)]

scenes, subs, t = [], [], 0.0
for row in PLAN:
    if isinstance(row, str):
        word, style, d = INTER[row]
        scenes.append({"id": row, "kind": "inter", "word": word, "style": style, "start": round(t, 3), "dur": d})
        t += d
        continue
    sid, nid, lead, tail = row
    nd = dur(f"audio_{V}/{nid}.wav")
    ws = json.load(open(f"audio_{V}/{nid}.words.json"))
    ns = t + lead
    toks = [norm(w["text"]) for w in ws]
    cues = {}
    for k, ph in NARR[nid]["cues"].items():
        pt = norm(ph).split()
        hit = next((i for i in range(len(toks)) if toks[i:i + len(pt)] == pt), None)
        assert hit is not None, (nid, ph, toks)
        cues[k] = round(ns + ws[hit]["start"], 3)
    for w in ws:
        subs.append({"w": w["text"], "a": round(ns + w["start"], 3), "b": round(ns + w["end"], 3), "sc": sid})
    d = lead + nd + tail
    scenes.append({"id": sid, "kind": "scene", "narr": nid, "start": round(t, 3), "dur": round(d, 3),
                   "nstart": round(ns, 3), "ndur": round(nd, 3), "cues": cues})
    t += d

# blocos de legenda: até ~34 caracteres, quebra preferida em pontuação; nunca termina em palavra fraca
FRACAS = {"de", "del", "la", "el", "los", "las", "tu", "y", "o", "en", "a", "al", "con", "por", "para", "una", "un",
          "le", "que", "su", "mercado", "es", "ya", "sin"}
blocks, cur = [], []
def flush():
    if cur: blocks.append({"a": cur[0]["a"], "b": cur[-1]["b"], "w": [dict(x) for x in cur]}); cur.clear()
def txt(ws): return " ".join(x["w"] for x in ws)
for i, w in enumerate(subs):
    if cur and w["sc"] != cur[-1]["sc"]:
        flush()
    if cur and len(txt(cur + [w])) > 34 and norm(cur[-1]["w"]) not in FRACAS:
        flush()
    cur.append(w)
    fim = re.search(r"[.?!:]$", w["w"]) or w["w"].endswith("...")
    virg = w["w"].endswith(",") and len(txt(cur)) >= 16
    if fim or virg:
        flush()
flush()
for i, b in enumerate(blocks):  # segura o bloco na tela até o próximo começar (máx. 0,6 s)
    nxt = blocks[i + 1]["a"] if i + 1 < len(blocks) else b["b"] + 0.6
    b["b"] = round(min(nxt, b["b"] + 0.6), 3)

import os
over = json.load(open(f"telas_{V}.json")) if os.path.exists(f"telas_{V}.json") else {}
tl = {"fps": 30, "total": round(t, 3), "scenes": scenes, "subs": blocks, "over": over}
json.dump(tl, open("build/timeline.json", "w"), ensure_ascii=False, indent=1)
open("build/timeline.js", "w").write("window.TL=" + json.dumps(tl, ensure_ascii=False) + ";\n")
print("total", round(t, 2), "s · blocos de legenda", len(blocks))
for s in scenes:
    print(s["id"], s["start"], s["dur"], s.get("cues", s.get("word")))
