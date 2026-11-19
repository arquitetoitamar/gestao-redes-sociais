"""Legenda .srt para subir no YouTube (no tempo do vídeo editado), com os nomes corrigidos.

uso: python3 legendas.py  -> legendas_youtube.srt
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import monta as M

TROCA = [(r'\b[Cc]loud\b', 'Claude'), (r'\bchat\s?I?PT\b', 'ChatGPT'), (r'\b[Cc]hat de PT\b', 'ChatGPT'),
         (r'\b[Cc]hat GPT\b', 'ChatGPT'), (r'\bMoreLog\b', 'MoreLogin'), (r'\bmore login\b', 'MoreLogin'),
         (r'\bPlayWrite\b', 'Playwright'), (r'\bCRAP\b', 'scraper'), (r'\bselar\b', 'CLI'),
         (r'\bagente de A\b', 'agente de IA'), (r'\be A lá\b', 'e IA lá'), (r'\bchatos\b', 'chats'),
         (r'\bmociagem\b', 'mensagem'), (r'\bcloud call work\b', 'Claude Cowork'), (r'\bGlockbot\b', 'Clawdbot')]


def ts(x):
    return '%02d:%02d:%06.3f' % (x // 3600, x % 3600 // 60, x % 60)


def main():
    e = json.load(open(M.T('edl.json')))
    d = json.load(open(M.T('fala.json')))
    ws = [(s['offsets']['from'] / 1000, s['offsets']['to'] / 1000, s['text'].strip())
          for s in d['transcription'] if s['text'].strip()]
    ws = [(M.src_para_out(e, a), M.src_para_out(e, max(a, b)), t) for a, b, t in ws
          if M.INICIO - 0.3 <= a < M.FIM and not any(x <= (a + b) / 2 < y for x, y in M.CORTES)]
    caps, cur = [], []
    for i, (a, b, t) in enumerate(ws):
        cur.append((a, b, t))
        txt = ' '.join(x[2] for x in cur)
        nxt = ws[i + 1][0] if i + 1 < len(ws) else None
        if len(txt) > 70 or (t[-1] in '.?!' and len(txt) > 25) or nxt is None or nxt - b > 0.8 or b - cur[0][0] > 5.5:
            caps.append([cur[0][0], b, txt])
            cur = []
    with open(os.path.join(AQUI, 'legendas_youtube.srt'), 'w') as f:
        for k, (a, b, t) in enumerate(caps, 1):
            for p, r in TROCA:
                t = re.sub(p, r, t)
            if len(t) > 42:
                c = t.rfind(' ', 0, len(t) // 2 + 8)
                t = t[:c] + '\n' + t[c + 1:]
            fim = min(b + 0.2, caps[k][0]) if k < len(caps) else b + 0.2
            f.write('%d\n%s --> %s\n%s\n\n' % (k, ts(a).replace('.', ','), ts(max(fim, a + 0.5)).replace('.', ','), t))
    print(len(caps), 'legendas')


if __name__ == '__main__':
    main()
