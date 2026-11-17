"""Vídeo da Gestão da Equipe (IMG_4798.MOV, celular filmando o monitor) para o grupo de WhatsApp e o Reel.

- vertical 1080x1920, 30 fps, áudio original sem ajuste
- Gmail pessoal desfocado (caixas.json, gerado por mascara.py)
- legenda queimada a partir das palavras do whisper (palavras.json) + título nos 5 s iniciais

uso: python3 monta.py [origem.MOV]
"""
import json, os, subprocess, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIG = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/Downloads/IMG_4798.MOV')
SAIDA = os.path.join(AQUI, 'gestao_equipe_1711.mp4')
FFMPEG_ASS = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
W, H, FPS = 1080, 1920, 30
FIM = 146.4

# correções da transcrição (o whisper escreve como ouviu)
TROCA = {}


def ts(s):
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return '%d:%02d:%05.2f' % (h, m, s)


def legendas():
    d = json.load(open(os.path.join(AQUI, 'palavras.json')))
    ps = [[s['offsets']['from'] / 1000, s['offsets']['to'] / 1000, s['text'].strip()]
          for s in d['transcription'] if s['text'].strip()]
    for i, p in enumerate(ps):                      # palavra com duração zero: estica até a próxima
        if p[1] <= p[0] and i + 1 < len(ps):
            p[1] = max(p[0] + 0.12, ps[i + 1][0])
        p[2] = TROCA.get(p[2], p[2])
    blocos, cur = [], []
    for i, p in enumerate(ps):
        cur.append(p)
        txt = ' '.join(x[2] for x in cur)
        prox = ps[i + 1] if i + 1 < len(ps) else None
        quebra = (p[2][-1] in '.,?!' and len(cur) >= 2) or len(cur) >= 5 or len(txt) >= 24 \
            or prox is None or prox[0] - p[1] > 0.45
        if quebra:
            blocos.append(cur)
            cur = []
    tempos = []
    for i, b in enumerate(blocos):
        ini = b[0][0]
        fim = b[-1][1] + 0.25
        if i + 1 < len(blocos):
            fim = min(fim if blocos[i + 1][0][0] - b[-1][1] > 0.6 else blocos[i + 1][0][0], blocos[i + 1][0][0])
        tempos.append([ini, fim])
    for i, t in enumerate(tempos):                   # nenhum bloco com menos de 0,55 s: empurra o seguinte
        if i and t[0] < tempos[i - 1][1]:
            t[0] = tempos[i - 1][1]
        t[1] = max(t[1], t[0] + 0.55)
    ev = []
    for b, (ini, fim) in zip(blocos, tempos):
        txt = ' '.join(x[2] for x in b).rstrip(',')
        ev.append(f'Dialogue: 1,{ts(ini)},{ts(min(fim, FIM))},Leg,,0,0,0,,{{\\fad(60,60)}}{txt}')
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Selo,Arial Black,40,&H00111111,&H00111111,&H0000D7FF,&H0000D7FF,0,0,0,0,100,100,1,0,3,14,0,8,60,60,110,1
Style: Titulo,Arial Black,74,&H00FFFFFF,&H00FFFFFF,&H00331D0B,&HE6331D0B,0,0,0,0,100,100,0,0,3,22,0,8,60,60,200,1
Style: Leg,Arial,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB4000000,1,0,0,0,100,100,0,0,3,14,0,2,70,70,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    topo = [f'Dialogue: 2,{ts(0)},{ts(5.2)},Selo,,0,0,0,,{{\\fad(150,250)}}NOVIDADE · MARKETPLACE CONNECT',
            f'Dialogue: 2,{ts(0.15)},{ts(5.2)},Titulo,,0,0,0,,{{\\fad(200,250)}}Gestão da Equipe:\\Ncada ação da IA,\\Nfuncionário por funcionário']
    caminho = os.path.join(AQUI, 'legendas.ass')
    open(caminho, 'w', encoding='utf-8').write(cab + '\n'.join(topo + ev) + '\n')
    return caminho, len(ev)


def desfoca(q, cs):
    for x0, y0, x1, y1 in cs:
        roi = q[y0:y1, x0:x1]
        if roi.size == 0:
            continue
        h, w = roi.shape[:2]
        pe = cv2.resize(roi, (max(1, w // 18), max(1, h // 18)), interpolation=cv2.INTER_AREA)
        q[y0:y1, x0:x1] = cv2.GaussianBlur(cv2.resize(pe, (w, h), interpolation=cv2.INTER_LINEAR), (0, 0), 6)
    return q


def main():
    ass, n_leg = legendas()
    caixas = {int(k): v for k, v in json.load(open(os.path.join(AQUI, 'caixas.json'))).items()}
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', ORIG, '-t', str(FIM), '-vf', f'scale={W}:{H}',
                            '-r', str(FPS), '-fps_mode', 'cfr', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen([FFMPEG_ASS, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', ORIG, '-map', '0:v', '-map', '1:a', '-t', str(FIM),
                            '-vf', f"ass='{ass}'", '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                            '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', SAIDA],
                           stdin=subprocess.PIPE)
    tam = W * H * 3
    n = 0
    while True:
        b = dec.stdout.read(tam)
        if len(b) < tam:
            break
        q = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        if n in caixas:
            q = desfoca(q.copy(), caixas[n])
        enc.stdin.write(q.tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print('quadros', n, '| legendas', n_leg, '| saída', SAIDA, os.path.getsize(SAIDA) // 1024 // 1024, 'MB')


if __name__ == '__main__':
    main()
