#!/Users/itamar/tools/autoclip/venv/bin/python
"""Cortes verticais de um vídeo longo: o AutoClip escolhe os trechos, o nosso fluxo edita.

O AutoClip (~/tools/autoclip) é bom em achar os melhores momentos, mas devolve título em chinês,
recorte fixo no centro e legenda pequena. Aqui ele só escolhe; o resto segue o padrão de
output/reel-startup-pandemia/monta.py:

  1. legenda pt-BR com whisper-cli (ou a --srt que você passar)
  2. AutoClip `run` escolhe os trechos e dá nota
  3. enquadramento por cena: corte de cena + rosto (YuNet, o mesmo modelo do AutoClip)
  4. título de tela, legenda do Instagram, hashtags (no máx. 5) e texto do Shorts em pt-BR,
     além da correção da legenda, tudo pelo OpenRouter
  5. render 1080x1920 em fundo branco: título em cima, vídeo 1080x1216 no meio,
     legenda queimada, crédito da fonte embaixo e cartão final com CTA (opcional)
  6. calendário espaçado (um corte a cada 2 dias), sem publicar nada

Uso:
  scripts/cortes/cortes.py VIDEO --nome band-pqtec [--srt X.srt] [--fonte "Reportagem: Band Cidade"]
        [--contexto "Itamar é o entrevistado"] [--cta CONNECT] [--max 4] [--min-nota 70]
        [--corta-topo 0.08] [--corta-base 0.20]
  scripts/cortes/cortes.py --render output/cortes-band-pqtec   # re-renderiza depois de revisar

Para revisar, edite output/cortes-<nome>/plano.json (títulos, desfoque) e legenda-NN.srt (falas),
depois rode com --render. Vídeo e trabalho ficam fora do git (regra dos 10 MB).
"""
import argparse
import datetime as dt
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
AUTOCLIP = Path.home() / 'tools/autoclip/autoclip'
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'          # tem libass; o ffmpeg do PATH não tem
FP = '/opt/homebrew/opt/ffmpeg-full/bin/ffprobe'
YUNET = next(Path(cv2.__file__).parents[1].glob('backend/assets/models/face_detection_yunet_*.onnx'))
MODELOS_WHISPER = ['ggml-large-v3-turbo-q5_0.bin', 'ggml-large-v3-turbo.bin', 'ggml-small.bin', 'ggml-base.bin']
LLM_MODELO = os.environ.get('CORTES_MODELO', 'deepseek/deepseek-chat-v3.1')

# layout (pixels do quadro 1080x1920)
W, H = 1080, 1920
VY, VH = 360, 1216                       # faixa do vídeo
AZUL = (11, 29, 51)                      # texto escuro
DESTAQUE = (37, 99, 235)                 # cor de destaque sobre o branco
CINZA = (107, 114, 128)
FONTES = '/System/Library/Fonts/Supplemental'
FINANCEIRO = re.compile(r'R\$|\bmilh(ão|ões)\b|\bbilh|faturamento|faturou|\bmargem|\blucro|\bGMV\b|\d+\s?%', re.I)


def sh(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def seg(t):
    h, m, r = t.replace('.', ',').split(':')
    s, ms = (r.split(',') + ['0'])[:2]
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, '0')[:3]) / 1000


def srt_ts(s):
    ms = round(s * 1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sg, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{sg:02d},{ms:03d}'


def ass_ts(s):
    h, r = divmod(max(s, 0), 3600); m, r = divmod(r, 60)
    return f'{int(h)}:{int(m):02d}:{r:05.2f}'


def le_srt(p):
    itens = []
    for bloco in Path(p).read_text(encoding='utf-8').strip().split('\n\n'):
        linhas = bloco.strip().splitlines()
        i = next((k for k, l in enumerate(linhas) if '-->' in l), None)
        if i is None:
            continue
        a, b = [x.strip() for x in linhas[i].split('-->')]
        texto = ' '.join(l.strip() for l in linhas[i + 1:]).strip()
        if texto:
            itens.append((seg(a), seg(b), texto))
    return itens


def grava_srt(p, itens):
    Path(p).write_text('\n'.join(f'{k}\n{srt_ts(a)} --> {srt_ts(b)}\n{t}\n' for k, (a, b, t) in enumerate(itens, 1)),
                       encoding='utf-8')


def duracao(video):
    return float(subprocess.check_output([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                          str(video)]).strip())


# ---------------------------------------------------------------- 1. legenda
def transcreve(video, trab):
    pasta = Path.home() / '.cache/whisper-cpp'
    modelo = next((pasta / m for m in MODELOS_WHISPER if (pasta / m).exists()), None)
    if not modelo:
        sys.exit(f'nenhum modelo do whisper-cli em {pasta} (baixe {MODELOS_WHISPER[0]})')
    if 'large' not in modelo.name:
        print(f'aviso: usando {modelo.name}; o large-v3-turbo erra menos em pt-BR', file=sys.stderr)
    wav = trab / 'audio16k.wav'
    sh([FF, '-y', '-loglevel', 'error', '-i', video, '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav])
    sh(['whisper-cli', '-m', modelo, '-l', 'pt', '-f', wav, '-osrt', '-of', trab / 'transcricao'],
       stdout=subprocess.DEVNULL)
    saida = trab / 'transcricao.srt'
    if not saida.exists():
        sys.exit('whisper-cli não gerou a legenda (confira o arquivo do modelo)')
    wav.unlink()
    return saida


# ---------------------------------------------------------------- 2. AutoClip escolhe
def escolhe(video, srt, nome, trab, min_nota):
    dados = trab / 'autoclip'
    dados.mkdir(exist_ok=True)
    (dados / 'privacy.json').write_text('{"analytics": false, "crash_reports": false}\n')
    r = subprocess.run([AUTOCLIP, '--data-dir', dados, 'run', video, '--srt', srt, '--name', nome,
                        '--min-score', '0.5', '--no-db', '--json'], capture_output=True, text=True)
    (trab / 'autoclip.log').write_text(r.stderr)
    if r.returncode != 0:
        sys.exit(f'AutoClip falhou (veja {trab / "autoclip.log"})')
    res = json.loads(r.stdout)
    (trab / 'autoclip.json').write_text(json.dumps(res, ensure_ascii=False, indent=2))
    clips = [c for c in res['clips'] if (c.get('score_100') or 0) >= min_nota]
    return sorted(clips, key=lambda c: -(c.get('score_100') or 0))


# ---------------------------------------------------------------- 3. enquadramento
def enquadra(video, ini, fim, topo, base, passo=0.2):
    """Cenas (a, b, centro_x) relativas ao início do corte. Corte de cena pelo histograma, centro pelo maior rosto."""
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    sw, shh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    pw = 640
    ph = round(shh * pw / sw)
    y0, y1 = int(ph * topo), int(ph * (1 - base))
    det = cv2.FaceDetectorYN.create(str(YUNET), '', (pw, y1 - y0), 0.6)
    cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
    pula = max(1, round(fps * passo))
    amostras, cortes, ant, n = [], [], None, 0
    while True:
        ok = cap.grab()
        if not ok:
            break
        t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        if t > fim:
            break
        n += 1
        if n % pula:
            continue
        ok, q = cap.retrieve()
        if not ok:
            continue
        q = cv2.resize(q, (pw, ph))
        hsv = cv2.cvtColor(q, cv2.COLOR_BGR2HSV)
        hist = cv2.normalize(cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256]), None).flatten()
        if ant is not None and cv2.compareHist(ant, hist, cv2.HISTCMP_CORREL) < 0.6:
            cortes.append(t - ini)
        ant = hist
        _, faces = det.detect(np.ascontiguousarray(q[y0:y1]))
        cx = None
        if faces is not None and len(faces):
            f = max(faces, key=lambda f: f[2] * f[3])
            if f[2] * f[3] > (pw * 0.035) ** 2:          # ignora rosto minúsculo de fundo
                cx = float((f[0] + f[2] / 2) / pw)
        amostras.append((t - ini, cx))
    cap.release()
    dur = fim - ini
    limites = [0.0]
    for c in cortes:
        if c - limites[-1] >= 0.8:                       # cena curta demais vira parte da anterior
            limites.append(c)
    if dur - limites[-1] < 0.8 and len(limites) > 1:
        limites.pop()
    limites.append(dur)
    cenas, ultimo = [], 0.5
    for a, b in zip(limites, limites[1:]):
        xs = [cx for t, cx in amostras if a <= t < b and cx is not None]
        c = statistics.median(xs) if xs else (ultimo if cenas else 0.5)
        cenas.append([round(float(a), 3), round(float(b), 3), round(float(c), 3)])
        ultimo = c
    return cenas, (sw, shh)


# ---------------------------------------------------------------- 4. textos (OpenRouter)
def llm(prompt):
    from openai import OpenAI
    chave = os.environ.get('OPENROUTER_API_KEY')
    if not chave:
        sys.exit('falta OPENROUTER_API_KEY no ambiente')
    cli = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=chave, timeout=120)
    for _ in range(3):
        r = cli.chat.completions.create(model=LLM_MODELO, temperature=0.4, max_tokens=4000,
                                        messages=[{'role': 'user', 'content': prompt}])
        txt = r.choices[0].message.content or ''
        m = re.search(r'\{.*\}', txt, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    raise RuntimeError('o modelo não devolveu JSON válido')


def textos(falas, contexto, fonte, cta):
    numeradas = [{'n': k, 'texto': t} for k, (_, _, t) in enumerate(falas, 1)]
    prompt = f"""Você edita cortes curtos (Reels/Shorts) para o perfil @tiopstecnologia do Itamar Rocha
(fundador da Tiops, IA para quem vende em marketplace). Português do Brasil, frases curtas, sem jargão,
sem emoji no título, sem inventar fato ou número que não esteja na fala.

Contexto do vídeo: {contexto or 'não informado'}
Fonte original: {fonte or 'gravação própria do Itamar'}
Palavra do CTA: {cta or 'nenhuma'}

Falas do trecho (legenda automática, numerada):
{json.dumps(numeradas, ensure_ascii=False)}

Devolva SÓ um JSON com:
- "titulo": gancho para a tela, até 30 caracteres, use "\\n" para quebrar em 2 linhas equilibradas
- "legenda": legenda do Instagram em 2 a 4 parágrafos curtos, escrita pelo próprio Itamar
  (primeira pessoa quando ele aparece ou fala); cite a fonte original se houver;
  se houver palavra de CTA, termine com "💬 Comenta {cta or 'PALAVRA'} que eu te mando no direct."
- "hashtags": lista de no máximo 5 hashtags relevantes (com #)
- "titulo_shorts": título do YouTube Shorts, até 90 caracteres, buscável
- "descricao_shorts": 1 ou 2 frases para a descrição do Shorts, citando a fonte se houver
- "motivo": uma frase dizendo por que este trecho prende atenção
- "falas": a MESMA lista de falas (mesma quantidade e mesmos "n"), só com ortografia, pontuação e
  nomes próprios corrigidos; não resuma nem reescreva"""
    r = llm(prompt)
    corr = {f.get('n'): f.get('texto') for f in r.get('falas', []) if isinstance(f, dict)}
    if len(corr) == len(falas) and all(isinstance(corr.get(k), str) and corr[k].strip() for k in range(1, len(falas) + 1)):
        r['falas'] = [(a, b, corr[k].strip()) for k, (a, b, _) in enumerate(falas, 1)]
    else:
        print('aviso: correção da legenda veio desalinhada; mantive a original', file=sys.stderr)
        r['falas'] = falas
    r['hashtags'] = [h if h.startswith('#') else '#' + h for h in r.get('hashtags', [])][:5]
    return r


def fatia_legenda(itens, ini, fim, max_chars=46):
    """Falas dentro do corte, tempos a partir de zero, quebradas em blocos curtos (até 2 linhas)."""
    saida = []
    for a, b, t in itens:
        if b <= ini or a >= fim:
            continue
        a, b = max(a, ini) - ini, min(b, fim) - ini
        palavras, blocos, atual = t.split(), [], ''
        for p in palavras:
            if atual and len(atual) + 1 + len(p) > max_chars:
                blocos.append(atual); atual = p
            else:
                atual = (atual + ' ' + p).strip()
        if atual:
            blocos.append(atual)
        total = sum(len(x) for x in blocos) or 1
        t0 = a
        for x in blocos:
            t1 = t0 + (b - a) * len(x) / total
            saida.append((round(t0, 2), round(t1, 2), x))
            t0 = t1
    return saida


# ---------------------------------------------------------------- 5. render
def fonte(nome, tam):
    for p in (f'{FONTES}/{nome}.ttf', f'/Library/Fonts/{nome}.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, tam)
    return ImageFont.load_default()


def bgr(c):
    return f'&H00{c[2]:02X}{c[1]:02X}{c[0]:02X}'


def tamanho_titulo(titulo, largura=960, maximo=88, minimo=50):
    """Corpo do .ass para a linha mais longa do título caber na largura.

    O libass desenha o Fontsize na altura ascendente+descendente, menor que o mesmo número em px
    do PIL; por isso mede no PIL e converte pela métrica da fonte."""
    regua = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    for tam in range(maximo, minimo - 1, -2):
        f = fonte('Arial Black', tam)
        if max(regua.textlength(l, font=f) for l in titulo.split('\n')) <= largura:
            break
    asc, desc = fonte('Arial Black', tam).getmetrics()
    return asc + desc


def equilibra(titulo):
    """Sem quebra manual, divide em 2 linhas de tamanho parecido."""
    if '\n' in titulo or len(titulo) <= 16:
        return titulo
    p = titulo.split()
    k = min(range(1, len(p)), key=lambda i: abs(len(' '.join(p[:i])) - len(' '.join(p[i:]))), default=0)
    return ' '.join(p[:k]) + '\n' + ' '.join(p[k:]) if k else titulo


def monta_ass(p, titulo, falas, dur, credito):
    titulo = equilibra(titulo)
    tam = tamanho_titulo(titulo)
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Titulo,Arial Black,{tam},{bgr(AZUL)},{bgr(AZUL)},&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,8,60,60,80,1
Style: Leg,Arial,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB4000000,1,0,0,0,100,100,0,0,3,14,0,2,70,70,400,1
Style: Credito,Arial,34,{bgr(CINZA)},{bgr(CINZA)},&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,0,0,1,0,0,8,70,70,{VY + VH + 50},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f'Dialogue: 0,{ass_ts(0)},{ass_ts(dur)},Titulo,,0,0,0,,' + titulo.replace('\n', '\\N'),
          f'Dialogue: 0,{ass_ts(0)},{ass_ts(dur)},Credito,,0,0,0,,{credito}']
    ev += [f'Dialogue: 1,{ass_ts(a)},{ass_ts(b)},Leg,,0,0,0,,{{\\fad(60,60)}}{t}' for a, b, t in falas]
    Path(p).write_text(cab + '\n'.join(ev) + '\n', encoding='utf-8')


def cartao_cta(p, cta):
    im = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)

    def centro(y, txt, f, cor):
        d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=cor)
    d.rounded_rectangle((140, 700, 940, 1000), radius=36, outline=DESTAQUE, width=8)
    centro(740, 'Comenta', fonte('Arial Bold', 56), AZUL)
    centro(820, cta, fonte('Arial Black', 120), DESTAQUE)
    centro(1060, 'que eu te mando no direct', fonte('Arial Bold', 52), AZUL)
    centro(1500, '@tiopstecnologia', fonte('Arial Bold', 40), CINZA)
    im.save(p)


def render(pasta, c, plano):
    trab = pasta / 'trab'
    n = c['n']
    video, (sw, shh) = plano['video'], plano['tamanho']
    ini, fim = c['ini'], c['fim']
    dur = round(fim - ini, 3)
    falas = le_srt(pasta / f'legenda-{n:02d}.srt')
    y0 = round(shh * plano['corta_topo'] / 2) * 2
    y1 = round(shh * (1 - plano['corta_base']) / 2) * 2
    ch = y1 - y0
    cw = min(round(ch * W / VH / 2) * 2, sw)
    credito = ' · '.join(x for x in (plano.get('fonte'), '@tiopstecnologia') if x)
    ass = trab / f'corte-{n:02d}.ass'
    monta_ass(ass, c['titulo'], falas, dur, credito)
    partes, rot = [], []
    for k, cena in enumerate(c['cenas']):
        a, b, cx = cena[:3]
        desfoca = len(cena) > 3 and cena[3]          # 4º valor true = desfocar (painel, print de conta)
        x = int(min(max(cx * sw - cw / 2, 0), sw - cw)) // 2 * 2
        partes.append(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,crop={cw}:{ch}:{x}:{y0},'
                      f'scale={W}:{VH}:flags=lanczos,setsar=1{",boxblur=18:2" if desfoca else ""}[v{k}]')
        rot.append(f'[v{k}]')
    fc = ';'.join(partes) + f';{"".join(rot)}concat=n={len(rot)}:v=1:a=0[vid]'
    fc += f';color=c=white:s={W}x{H}:r=30[bg];[bg][vid]overlay=0:{VY}:shortest=1,subtitles={ass}[out]'
    fc += f';[0:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.06,afade=t=out:st={max(dur - 0.4, 0)}:d=0.4[aud]'
    corpo = trab / f'corpo-{n:02d}.mp4'
    sh([FF, '-y', '-loglevel', 'error', '-ss', ini, '-t', dur, '-i', video, '-filter_complex', fc,
        '-map', '[out]', '-map', '[aud]', '-t', dur, '-r', 30, '-c:v', 'libx264', '-crf', 19, '-preset', 'medium',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', 48000, corpo])
    final = pasta / f'corte-{n:02d}.mp4'
    if plano.get('cta'):
        png = trab / 'cta.png'
        cartao_cta(png, plano['cta'])
        fecho = trab / 'fecho.mp4'
        sh([FF, '-y', '-loglevel', 'error', '-loop', 1, '-i', png, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
            '-t', 2.5, '-r', 30, '-vf', 'fade=t=in:st=0:d=0.3', '-c:v', 'libx264', '-crf', 19, '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-shortest', fecho])
        sh([FF, '-y', '-loglevel', 'error', '-i', corpo, '-i', fecho, '-filter_complex',
            '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]', '-map', '[v]', '-map', '[a]', '-c:v', 'libx264',
            '-crf', 19, '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart', final])
    else:
        corpo.replace(final)
    # folha de conferência: 6 quadros lado a lado
    d = duracao(final)
    quadros = []
    for k in range(6):
        q = trab / f'q{k}.jpg'
        sh([FF, '-y', '-loglevel', 'error', '-ss', d * (k + 0.5) / 6, '-i', final, '-frames:v', 1, '-vf', 'scale=270:-2', q])
        quadros.append(Image.open(q)); q.unlink()
    folha = Image.new('RGB', (270 * 6, quadros[0].height), 'white')
    for k, q in enumerate(quadros):
        folha.paste(q, (270 * k, 0))
    folha.save(trab / f'folha-{n:02d}.jpg', quality=85)
    return final


# ---------------------------------------------------------------- 6. textos de publicação e calendário
def escreve_md(pasta, plano):
    cal = ['# Calendário sugerido', '',
           'Um corte a cada 2 dias, do mais forte para o mais fraco (nunca postar junto: um canibaliza o outro).',
           'Horário 19h: Reels rendem entre 16h e 20h, e 16h/18h/20h são da série "Pergunta pro Claude".',
           'Nada é publicado sem "sim" do Itamar.', '',
           '| Data | Corte | Título | Nota AutoClip | Avisos |', '|---|---|---|---|---|']
    dia = dt.date.fromisoformat(plano['inicio'])
    for c in plano['cortes']:
        n = c['n']
        avisos = '⚠ número financeiro: rodar as 5 perguntas' if c.get('financeiro') else ''
        cal.append(f"| {dia.strftime('%d/%m')} 19h | corte-{n:02d} | {c['titulo'].replace(chr(10), ' ')} "
                   f"| {c['nota']} | {avisos} |")
        dia += dt.timedelta(days=2)
        md = [f"# Corte {n:02d}: {c['titulo'].replace(chr(10), ' ')}", '',
              f"Trecho {srt_ts(c['ini'])[:8]}–{srt_ts(c['fim'])[:8]} do original ({c['fim'] - c['ini']:.0f} s), "
              f"nota {c['nota']} do AutoClip. {c.get('motivo', '')}", '']
        if c.get('financeiro'):
            md += ['> ⚠ A fala cita valores ou porcentagens. Antes de publicar, rodar as 5 perguntas das regras de publicação.', '']
        borradas = [f'{x[0]:.1f}–{x[1]:.1f} s' for x in c['cenas'] if len(x) > 3 and x[3]]
        md += ['Cenas desfocadas: ' + (', '.join(borradas) if borradas else 'nenhuma') +
               '. Tela com painel, gráfico ou print de conta: pôr `true` como 4º valor da cena no plano.json e rodar `--render`.', '']
        md += ['## Legenda do Instagram', '', c['legenda'], '', '## Primeiro comentário', '', ' '.join(c['hashtags']), '',
               '## YouTube Shorts', '', f"**Título:** {c['titulo_shorts']}", '', c['descricao_shorts'], '']
        (pasta / f'corte-{n:02d}.md').write_text('\n'.join(md), encoding='utf-8')
    (pasta / 'calendario.md').write_text('\n'.join(cal) + '\n', encoding='utf-8')


def prepara(a):
    video = Path(a.video).resolve()
    pasta = REPO / 'output' / f'cortes-{a.nome}'
    trab = pasta / 'trab'
    trab.mkdir(parents=True, exist_ok=True)
    (pasta / '.gitignore').write_text('trab/\n*.mp4\n*.wav\n')
    srt = Path(a.srt).resolve() if a.srt else transcreve(video, trab)
    print(f'legenda: {srt}', file=sys.stderr)
    clips = escolhe(video, srt, a.nome, trab, a.min_nota)[:a.max]
    if not clips:
        sys.exit(f'AutoClip não achou trecho com nota ≥ {a.min_nota}; tente --min-nota 60')
    print(f'AutoClip escolheu {len(clips)} trecho(s)', file=sys.stderr)
    itens = le_srt(srt)
    plano = {'video': str(video), 'nome': a.nome, 'fonte': a.fonte, 'contexto': a.contexto, 'cta': a.cta,
             'corta_topo': a.corta_topo, 'corta_base': a.corta_base, 'cortes': [],
             'inicio': a.inicio or (dt.date.today() + dt.timedelta(days=1)).isoformat()}
    for n, cl in enumerate(clips, 1):
        ini, fim = seg(cl['start_time']), seg(cl['end_time'])
        janela = [(max(x, ini), min(y, fim), t) for x, y, t in itens if y > ini and x < fim]
        txt = textos(janela, a.contexto, a.fonte, a.cta)
        falas = fatia_legenda(txt['falas'], ini, fim)
        grava_srt(pasta / f'legenda-{n:02d}.srt', falas)
        cenas, tamanho = enquadra(video, ini, fim, a.corta_topo, a.corta_base)
        plano['tamanho'] = tamanho
        plano['cortes'].append({
            'n': n, 'ini': ini, 'fim': fim, 'nota': cl.get('score_100'), 'cenas': cenas,
            'titulo': txt.get('titulo', '').strip(), 'legenda': txt.get('legenda', '').strip(),
            'hashtags': txt['hashtags'], 'titulo_shorts': txt.get('titulo_shorts', '').strip(),
            'descricao_shorts': txt.get('descricao_shorts', '').strip(), 'motivo': txt.get('motivo', '').strip(),
            'financeiro': bool(FINANCEIRO.search(' '.join(t for _, _, t in janela))),
        })
        print(f"  corte {n:02d}: {txt.get('titulo', '').replace(chr(10), ' ')} · {len(cenas)} cena(s)", file=sys.stderr)
    (pasta / 'plano.json').write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding='utf-8')
    return pasta


def renderiza(pasta):
    plano = json.loads((pasta / 'plano.json').read_text(encoding='utf-8'))
    for c in plano['cortes']:
        print(f"render corte {c['n']:02d}…", file=sys.stderr)
        print(render(pasta, c, plano))
    escreve_md(pasta, plano)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', nargs='?')
    ap.add_argument('--nome')
    ap.add_argument('--srt')
    ap.add_argument('--fonte', default='', help='crédito da fonte original, ex.: "Reportagem: Band Cidade"')
    ap.add_argument('--contexto', default='', help='quem fala e do que se trata (ajuda título e correção)')
    ap.add_argument('--cta', default='', help='palavra do ManyChat (CONNECT, NOTA…); vazio = sem cartão final')
    ap.add_argument('--max', type=int, default=4)
    ap.add_argument('--min-nota', type=int, default=70)
    ap.add_argument('--corta-topo', type=float, default=0.0, help='fração de cima a descartar (relógio/logo da TV)')
    ap.add_argument('--corta-base', type=float, default=0.0, help='fração de baixo a descartar (tarja da TV)')
    ap.add_argument('--inicio', help='data do 1º post no calendário (AAAA-MM-DD); padrão amanhã')
    ap.add_argument('--render', metavar='PASTA', help='só re-renderiza a partir do plano.json')
    a = ap.parse_args()
    if a.render:
        renderiza(Path(a.render).resolve())
    else:
        if not (a.video and a.nome):
            ap.error('informe VIDEO e --nome (ou --render PASTA)')
        renderiza(prepara(a))
