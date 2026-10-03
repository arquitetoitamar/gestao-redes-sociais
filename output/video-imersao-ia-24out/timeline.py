"""Monta timeline.json a partir das durações reais da narração.

Cada cena de conteúdo dura: respiro inicial + fala + respiro final.
Interstitials (tela cheia com uma palavra) entram entre as cenas, só com música.
Os "cues" são os instantes em que cada frase-chave é falada, estimados pela
posição do texto (vírgula e ponto contam como pausa).
"""
import json, subprocess

narr = {n["id"]: n["txt"] for n in json.load(open("narracao.json"))}

def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out)

# (id, tipo, narração, respiro_ini, respiro_fim | palavra, estilo, duração)
PLAN = [
    ("s0", "scene", "n0", 0.15, 0.35),
    ("s1", "scene", "n1", 0.20, 0.40),
    ("s2", "scene", "n2", 0.15, 0.45),
    ("s3", "scene", "n3", 0.15, 0.35),
    ("s4", "scene", "n4", 0.20, 1.60),
]

CUES = {
    "n0": ["ouvir falar", "inteligência"],
    "n1": ["vinte e quatro", "São Paulo", "criar o seu", "agente de IA", "trabalhar", "marketplace"],
    "n2": ["Na prática", "criar seus", "ver aplicações", "descobrir", "automatizar"],
    "n3": ["Um dia inteiro", "Itamar Rocha", "professor", "fundador da Tiops", "plataforma"],
    "n4": ["Vagas limitadas", "Clique", "Saiba mais", "garanta"],
}

PAUSE = {",": 3, ".": 7, ":": 6, "?": 7, "!": 7}

def weights(txt):
    """Peso acumulado por caractere: letras valem 1, pontuação vale uma pausa."""
    acc, out = 0.0, []
    for i, ch in enumerate(txt):
        out.append(acc)
        acc += PAUSE.get(ch, 1)
        if txt[i:i + 3] == "...":
            acc += 4
    out.append(acc)
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
    txt = narr[nid]
    w = weights(txt)
    total_w = w[-1]
    ns = t + lead
    cues = {}
    for ph in CUES[nid]:
        idx = txt.find(ph)
        assert idx >= 0, (nid, ph)
        cues[ph] = round(ns + nd * (w[idx] / total_w), 3)
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
