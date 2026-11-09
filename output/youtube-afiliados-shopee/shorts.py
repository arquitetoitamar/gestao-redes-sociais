"""Corta 3 Shorts verticais (1080x1920) do vídeo original "afiliados.mp4".
Layout: gancho no topo, conversa do ChatGPT ampliada, webcam arredondada e legenda embaixo, chamada para o vídeo completo no fim.
Áudio original (sem ajuste); esperas em silêncio aceleradas 4x. Respeita a área segura dos Shorts (topo 150 px, botões à direita).
uso: python3 shorts.py <video_original> <pasta_trab> [1 2 3]"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

SRC, TRAB = sys.argv[1], sys.argv[2]
QUAIS = [int(x) for x in sys.argv[3:]] or [1, 2, 3]
AQUI = os.path.dirname(os.path.abspath(__file__))
os.makedirs(TRAB, exist_ok=True)
FONTE = '/System/Library/Fonts/Supplemental/Arial Black.ttf'
NAVY, OR = (15, 20, 36), (238, 77, 45)

# (início, fim, velocidade, x do recorte da tela) — tempos do original
SHORTS = {
    1: dict(gancho=('A IA ACHA O PRODUTO', 'COM MAIOR COMISSÃO'),
            seg=[(230.10, 249.30, 1, 360), (270.50, 284.75, 1, 360)]),
    2: dict(gancho=('LINK DE AFILIADO', 'EM SEGUNDOS COM IA'),
            seg=[(336.00, 346.10, 1, 360), (346.10, 352.90, 4, 360), (352.90, 358.90, 1, 360), (381.45, 390.10, 1, 360)]),
    3: dict(gancho=('VÍDEO DO PRODUTO', 'FEITO PELA IA'),
            seg=[(446.00, 455.80, 1, 360), (733.10, 749.30, 1, 500)]),
}
CORRECOES = [('ALTA, GRATO,', 'ALTA, AGRATTO'), ('GRATO, DUPLA', 'AGRATTO DUPLA'), ('GRATO DUPLA', 'AGRATTO DUPLA'), ('LÁ SE BOOK MARKETPLACE ', ''),
             ('SE BOOK MARKETPLACE ', ''), ('PARA VOCÊ É E VAMOS', 'PARA VOCÊ. E VAMOS LÁ.'), ('AFILIADO AGORA ELE', 'AFILIADO. AGORA ELE'),
             ('CHAT DE IPT', 'CHATGPT'), ('CHAT.PT', 'CHATGPT')]
CROP_Y, CROP_W, CROP_H = 170, 960, 800          # região da conversa no original (escala 1,125 -> 1080x900)
CAM = (1622, 782, 244, 242)                      # webcam do Screen Studio no original

def fonte(n): return ImageFont.truetype(FONTE, n)

def banner(linhas, arq):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tag = 'AFILIADO SHOPEE + CHATGPT'; f = fonte(34); w = d.textlength(tag, font=f)
    d.rounded_rectangle([(1080 - w) / 2 - 26, 160, (1080 + w) / 2 + 26, 222], 31, fill=OR)
    d.text(((1080 - w) / 2, 168), tag, font=f, fill='white')
    for i, (txt, cor) in enumerate(zip(linhas, ('white', OR))):
        n = 86
        while fonte(n).getlength(txt) > 980: n -= 2
        f = fonte(n); w = d.textlength(txt, font=f)
        d.text(((1080 - w) / 2, 250 + i * 104), txt, font=f, fill=cor, stroke_width=4, stroke_fill=(0, 0, 0))
    im.save(arq)

def fim(arq):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = 'PASSO A PASSO COMPLETO NO CANAL'; f = fonte(40); w = d.textlength(t, font=f)
    d.rounded_rectangle([(1080 - w) / 2 - 34, 1230, (1080 + w) / 2 + 34, 1330], 28, fill=OR)
    d.text(((1080 - w) / 2, 1254), t, font=f, fill='white')
    im.save(arq)

def mascara(arq, w=300, h=298, r=46):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); m.save(arq)

def ts(s):
    h = int(s // 3600); s -= h * 3600; m = int(s // 60); s -= m * 60
    return '%d:%02d:%05.2f' % (h, m, s)

mascara(f'{TRAB}/mask.png'); fim(f'{TRAB}/fim.png')
modelo = os.path.expanduser('~/.cache/whisper-cpp/ggml-large-v3-turbo-q5_0.bin')
for n in QUAIS:
    cfg = SHORTS[n]; pasta = f'{TRAB}/s{n}'; os.makedirs(pasta, exist_ok=True)
    banner(cfg['gancho'], f'{pasta}/banner.png')
    lista = []
    for i, (a, b, vel, cx) in enumerate(cfg['seg']):
        arq = f'{pasta}/seg{i}.ts'; lista.append("file '%s'" % os.path.abspath(arq)); d = b - a
        g = ('color=c=0x0f1424:s=1080x1920:r=30:d=%.3f[bg];[0:v]split[s][c];'
             '[s]crop=%d:%d:%d:%d,scale=1080:900[scr];[c]crop=%d:%d:%d:%d,scale=300:298,format=rgba[cam0];'
             '[1:v]format=gray[mk];[cam0][mk]alphamerge[cam];'
             '[bg][scr]overlay=0:470[t1];[t1][cam]overlay=60:1400:shortest=1,setpts=(PTS-STARTPTS)/%g,fps=30,format=yuv420p[v]'
             % (d, CROP_W, CROP_H, cx, CROP_Y, CAM[2], CAM[3], CAM[0], CAM[1], vel))
        cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % a, '-t', '%.3f' % d, '-i', SRC, '-loop', '1', '-i', f'{TRAB}/mask.png']
        if vel != 1:
            cmd += ['-f', 'lavfi', '-t', '%.3f' % (d / vel), '-i', 'anullsrc=r=48000:cl=stereo']; am = '2:a'
        else:
            am = '0:a'
        cmd += ['-filter_complex', g, '-map', '[v]', '-map', am, '-t', '%.3f' % (d / vel), '-c:v', 'libx264', '-crf', '17', '-preset', 'fast',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-f', 'mpegts', arq]
        subprocess.run(cmd, check=True)
    open(f'{pasta}/lista.txt', 'w').write('\n'.join(lista) + '\n')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{pasta}/lista.txt', '-c', 'copy', f'{pasta}/bruto.mp4'], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{pasta}/bruto.mp4'],
                               capture_output=True, text=True).stdout)
    # legenda: transcreve o próprio corte (frases curtas)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{pasta}/bruto.mp4', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', f'{pasta}/a.wav'], check=True)
    subprocess.run(['whisper-cli', '-m', modelo, '-l', 'pt', '-ml', '34', '-sow', '-f', f'{pasta}/a.wav', '-osrt', '-of', f'{pasta}/leg'], capture_output=True)
    ev = []
    for bl in open(f'{pasta}/leg.srt').read().strip().split('\n\n'):
        l = bl.split('\n')
        if len(l) < 3: continue
        a, b = l[1].split(' --> ')
        f = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + float(s[6:].replace(',', '.'))
        txt = ' '.join(l[2:]).strip().replace('chat de IPT', 'ChatGPT').replace('chat.pt', 'ChatGPT').replace('cloud', 'Claude')
        txt = txt.upper()
        for de, para in CORRECOES: txt = txt.replace(de, para)
        if txt.strip(): ev.append('Dialogue: 0,%s,%s,Leg,,0,0,0,,%s' % (ts(f(a)), ts(min(f(b), dur)), txt.strip()))
    open(f'{pasta}/leg.ass', 'w').write(
        '[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n'
        'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, '
        'ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
        'Style: Leg,Arial Black,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,4,1,7,400,130,1420,1\n\n'
        '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n' + '\n'.join(ev) + '\n')
    g = ("[0:v][1:v]overlay=0:0[a];[a]subtitles=%s/leg.ass:fontsdir=/System/Library/Fonts/Supplemental[b];"
         "[2:v]format=rgba,fade=in:st=0:d=0.3:alpha=1,setpts=PTS-STARTPTS+%.3f/TB[f];[b][f]overlay=0:0:eof_action=pass:enable='gte(t,%.3f)'[v]"
         % (pasta, dur - 3.0, dur - 3.0))
    subprocess.run(['/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg', '-v', 'error', '-y', '-i', f'{pasta}/bruto.mp4', '-loop', '1', '-t', '%.3f' % dur,
                    '-i', f'{pasta}/banner.png', '-loop', '1', '-t', '3', '-i', f'{TRAB}/fim.png', '-filter_complex', g, '-map', '[v]', '-map', '0:a',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', f'{TRAB}/short{n}.mp4'], check=True)
    print('short%d.mp4 %.1f s' % (n, dur), flush=True)
