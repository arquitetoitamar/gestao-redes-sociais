"""Monta build/timeline.json a partir da duração real de cada fala.

Cada cena de conteúdo dura: respiro inicial + fala + respiro final.
Telas de palavra (inter) entram entre as cenas, só com música.
Os "cues" são o instante em que cada trecho começa a ser falado, tirado do
tempo por palavra que a HeyGen devolve (audio/<id>.words.json).
"""
import json, re, subprocess

narr = {n["id"]: n["txt"] for n in json.load(open("narracao.json"))}


def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out)


# (id, "scene", narração, respiro_ini, respiro_fim) | (id, "inter", palavra, estilo, duração)
PLAN = [
    ("s0", "scene", "n0", 0.15, 0.40),
    ("i1", "inter", "NOVIDADE.", "blue", 0.80),
    ("s1", "scene", "n1", 0.20, 0.45),
    ("s2", "scene", "n2", 0.20, 0.55),
    ("s3", "scene", "n3", 0.20, 0.50),
    ("s4", "scene", "n4", 0.20, 0.75),
    ("i2", "inter", "E TEM MAIS.", "dark", 0.75),
    ("s5", "scene", "n5", 0.20, 1.05),
    ("s6", "scene", "n6", 0.20, 0.85),
    ("s7", "scene", "n7", 0.35, 2.40),
]

CUES = {
    "n0": ["copia", "pedido", "marketplace", "emitir", "nota fiscal"],
    "n1": ["Emissor", "Tiops", "direto", "SEFAZ", "certificado", "sua empresa"],
    "n2": ["prévia", "imposto", "frete", "desconto", "sem gastar"],
    "n3": ["intermediador", "Mercado", "Shopee", "Amazon", "Magalu", "SHEIN", "TikTok"],
    "n4": ["XML", "DANFE", "dez", "colar"],
    "n5": ["português", "Claude", "ChatGPT"],
    "n6": ["homologação", "Só vale", "liberar"],
    "n7": ["NOTA", "link"],
}


def norm(w):
    return re.sub(r"[^\wÀ-ÿ-]", "", w).lower()


def cue_times(nid):
    words = json.load(open(f"audio/{nid}.words.json"))
    off = words[0]["start"]                      # o silêncio inicial foi cortado do wav
    toks = [norm(w["text"]) for w in words]
    out = {}
    for ph in CUES[nid]:
        alvo = [norm(x) for x in ph.split()]
        for i in range(len(toks) - len(alvo) + 1):
            if toks[i:i + len(alvo)] == alvo:
                out[ph] = words[i]["start"] - off
                break
        else:
            raise SystemExit(f"{nid}: não achei '{ph}' em {toks}")
    return out


scenes, t = [], 0.0
for row in PLAN:
    sid, kind = row[0], row[1]
    if kind == "inter":
        _, _, word, style, d = row
        scenes.append({"id": sid, "kind": "inter", "word": word, "style": style,
                       "start": round(t, 3), "dur": d})
        t += d
        continue
    _, _, nid, lead, tail = row
    nd = dur(f"audio/{nid}.wav")
    ns = t + lead
    cues = {ph: round(ns + x, 3) for ph, x in cue_times(nid).items()}
    d = lead + nd + tail
    scenes.append({"id": sid, "kind": "scene", "narr": nid, "start": round(t, 3), "dur": round(d, 3),
                   "nstart": round(ns, 3), "ndur": round(nd, 3), "cues": cues})
    t += d

tl = {"fps": 30, "total": round(t, 3), "scenes": scenes}
json.dump(tl, open("build/timeline.json", "w"), ensure_ascii=False, indent=1)
open("build/timeline.js", "w").write("window.TL=" + json.dumps(tl, ensure_ascii=False) + ";\n")
print("total", round(t, 2), "s")
for s in scenes:
    print(s["id"], s["start"], s["dur"], s.get("cues", s.get("word")))
