#!/usr/bin/env python3
"""Reels e Shorts a partir de dois vídeos explicativos do Gemini Notebook (12/11/2026).

Para cada vídeo:
- remove a marca "Gemini Notebook" do canto inferior direito;
- corta o fim morto (carregando + tela preta) logo depois da narração;
- gancho escrito nos primeiros segundos;
- cartão final de 3 s (Reel: "Comente CONNECT"; Short: "Link na descrição");
- sobe a imagem 140 px (no quadro 720x1280) nas cenas em que a legenda do Gemini
  fica no rodapé, para ela sair de baixo do nome/legenda do Instagram e do título do Shorts;
- 1080x1920 e volume em -14 LUFS (narração é TTS do Gemini, não a voz do Itamar).

uso: python3 monta.py            (gera os 4 MP4 em ./final)
"""
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(AQUI, 'trab')
FINAL = os.path.join(AQUI, 'final')
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
PRETO = '/System/Library/Fonts/Supplemental/Arial Black.ttf'
NEGRITO = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
L, A = 1080, 1920
CARTAO = 3.0          # segundos do cartão final
AMARELO = (255, 212, 0, 255)
BRANCO = (255, 255, 255, 255)

# Marca do Gemini no quadro original 720x1280: x 530-695, y 1239-1253.
WM = dict(x=520, y=1228, w=186, h=34)
# Vídeo B tem papel pontilhado parado: copia o mesmo pedaço 4 colunas de
# pontos à esquerda (passo ~46,7 px) em vez de borrar.
DESLOCA = 187

SOBE = 140            # px no quadro 720x1280 (= 3 linhas de pontos do papel do vídeo B)

VIDEOS = {
    # corte seco às 30,4 s: dali em diante fundo escuro liso e legenda no rodapé
    'publica-anuncio': dict(
        src='a.mp4', fim=67.35, remove='delogo', corte=30.4,
        gancho=[('A IA PUBLICA SEU', BRANCO), ('ANÚNCIO POR VOCÊ', AMARELO)],
        gancho_y=230, gancho_tam=100),
    # corte seco às 13,2 s: antes, foto do caderno; depois, papel pontilhado parado
    'pausa-ml-shopee': dict(
        src='b.mp4', fim=68.10, remove='copia', corte=13.2,
        gancho=[('PAUSE NO ML', BRANCO), ('E NA SHOPEE', BRANCO), ('COM UMA FRASE', AMARELO)],
        gancho_y=210, gancho_tam=96),
}

CTA = {
    'reel': dict(pilula='Comente CONNECT', baixo='que eu te mando o link na DM'),
    'short': dict(pilula='Link na descrição', baixo='marketplaces.tiops.com.br'),
}


def sh(cmd):
    subprocess.run(cmd, check=True)


def texto_contorno(d, xy, txt, fonte, cor, borda):
    d.text(xy, txt, font=fonte, fill=cor, stroke_width=borda, stroke_fill=(0, 0, 0, 240))


def png_gancho(linhas, y0, tam0, destino):
    img = Image.new('RGBA', (L, A), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = y0
    for txt, cor in linhas:
        tam = tam0
        f = ImageFont.truetype(PRETO, tam)
        while d.textlength(txt, font=f) > 980:
            tam -= 4
            f = ImageFont.truetype(PRETO, tam)
        x = (L - d.textlength(txt, font=f)) / 2
        texto_contorno(d, (x, y), txt, f, cor, 10)
        y += int(tam0 * 1.12)
    img.save(destino)


def png_cartao(pilula, baixo, destino):
    img = Image.new('RGBA', (L, A), (8, 12, 20, 236))
    d = ImageDraw.Draw(img)
    def centro(txt, f, y, cor, borda=0):
        x = (L - d.textlength(txt, font=f)) / 2
        if borda:
            texto_contorno(d, (x, y), txt, f, cor, borda)
        else:
            d.text((x, y), txt, font=f, fill=cor)
    centro('Marketplace Connect', ImageFont.truetype(PRETO, 84), 560, AMARELO)
    f = ImageFont.truetype(NEGRITO, 54)
    centro('Liga o ChatGPT, o Claude e o Gemini', f, 700, BRANCO)
    centro('ao Mercado Livre, à Shopee e mais', f, 770, BRANCO)
    tp = 92
    fp = ImageFont.truetype(PRETO, tp)
    while d.textlength(pilula, font=fp) > 860:
        tp -= 2
        fp = ImageFont.truetype(PRETO, tp)
    lw = d.textlength(pilula, font=fp)
    x0, y0 = (L - lw) / 2 - 50, 930
    d.rounded_rectangle((x0, y0, x0 + lw + 100, y0 + 150), radius=40, fill=AMARELO)
    alt = fp.getbbox(pilula)
    d.text(((L - lw) / 2, y0 + (150 - (alt[3] + alt[1])) / 2), pilula, font=fp, fill=(10, 10, 10, 255))
    centro(baixo, ImageFont.truetype(NEGRITO, 50), 1130, BRANCO)
    img.save(destino)


def mascara(destino, w, h, pena=7):
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rectangle((pena, pena, w - pena - 1, h - pena - 1), fill=255)
    m.filter(ImageFilter.GaussianBlur(pena / 2)).save(destino)


def audio(chave, cfg):
    """Corta no fim da narração, completa o cartão com silêncio e normaliza (passada separada)."""
    bruto = os.path.join(TRAB, chave + '_bruto.wav')
    sh([FF, '-v', 'error', '-y', '-i', os.path.join(TRAB, cfg['src']), '-vn',
        '-af', 'atrim=0:%.3f,afade=t=out:st=%.3f:d=0.25,apad=pad_dur=%.2f' % (cfg['fim'], cfg['fim'] - 0.25, CARTAO),
        '-ac', '2', '-ar', '48000', bruto])
    r = subprocess.run([FF, '-hide_banner', '-i', bruto, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    norm = os.path.join(TRAB, chave + '_norm.wav')
    sh([FF, '-v', 'error', '-y', '-i', bruto, '-af',
        'loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true'
        % (m['input_i'], m['input_tp'], m['input_lra'], m['input_thresh'], m['target_offset']),
        '-ar', '48000', norm])
    return norm


def base(chave, cfg):
    """Vídeo sem marca, cortado, em 1080x1920, com o último quadro esticado pelo tempo do cartão.

    Tudo é feito no quadro original 720x1280 e só no fim vai para 1080x1920.
    """
    saida = os.path.join(TRAB, chave + '_base.mp4')
    w, c = WM, cfg['corte']
    delogo = 'delogo=x=%d:y=%d:w=%d:h=%d' % (w['x'], w['y'], w['w'], w['h'])
    entradas = ['-i', os.path.join(TRAB, cfg['src'])]
    if cfg['remove'] == 'delogo':
        partes = ['[0:v]%s[v0]' % delogo]
    else:
        msk = os.path.join(TRAB, 'mascara.png')
        mascara(msk, w['w'], w['h'])
        entradas += ['-loop', '1', '-i', msk]
        partes = [
            # caderno (antes do corte): delogo; papel pontilhado: copia o pedaço ao lado
            '[0:v]split=3[m][s][dl]',
            '[s]crop=%d:%d:%d:%d,format=rgba[p]' % (w['w'], w['h'], w['x'] - DESLOCA, w['y']),
            '[1:v]format=gray[k]', '[p][k]alphamerge[pk]',
            '[m][pk]overlay=%d:%d:shortest=1[cp]' % (w['x'], w['y']),
            '[dl]%s[dg]' % delogo,
            "[cp][dg]overlay=0:0:enable='lt(t,%.3f)'[v0]" % c]
    if cfg['remove'] == 'delogo':
        # fundo escuro liso: sobe e estica a última linha para preencher
        partes += ['[v0]split[o][x]',
                   '[x]crop=720:%d:0:%d,pad=720:1280:0:0,fillborders=bottom=%d:mode=smear[sh]' % (1280 - SOBE, SOBE, SOBE)]
    else:
        # papel pontilhado: completa com faixas do mesmo papel na mesma fase dos pontos
        # (legenda do Gemini ocupa y 1122-1179 e a caixa com sombra vai até ~1196; conteúdo termina em 972)
        partes += ['[v0]split=4[o][x][y][z]',
                   '[x]crop=720:%d:0:%d[s1]' % (1280 - SOBE, SOBE),
                   '[y]crop=720:60:0:%d[f1]' % (1140 - SOBE),
                   '[z]crop=720:80:0:1200[f2]',
                   '[s1][f1][f2]vstack=3[sh]']
    partes += ["[o][sh]overlay=0:0:enable='gte(t,%.3f)'[v1]" % c,
               '[v1]trim=0:%.3f,setpts=PTS-STARTPTS,scale=%d:%d:flags=lanczos,'
               'tpad=stop_mode=clone:stop_duration=%.2f,fps=30,format=yuv420p[v]' % (cfg['fim'], L, A, CARTAO)]
    sh([FF, '-v', 'error', '-y'] + entradas + ['-filter_complex', ';'.join(partes), '-map', '[v]',
       '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-an', saida])
    return saida


def final(chave, cfg, base_mp4, norm_wav, tipo):
    os.makedirs(FINAL, exist_ok=True)
    g = os.path.join(TRAB, chave + '_gancho.png')
    c = os.path.join(TRAB, 'cartao_%s.png' % tipo)
    png_gancho(cfg['gancho'], cfg['gancho_y'], cfg['gancho_tam'], g)
    png_cartao(CTA[tipo]['pilula'], CTA[tipo]['baixo'], c)
    t_cartao = cfg['fim']
    filtro = (
        '[1:v]format=rgba,fade=t=in:st=0.15:d=0.25:alpha=1,fade=t=out:st=3.6:d=0.35:alpha=1[g];'
        '[2:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,setpts=PTS+%.3f/TB[c];'
        '[0:v]boxblur=18:2:enable=\'gte(t,%.3f)\'[b];'
        '[b][g]overlay=0:0:eof_action=pass[bg];'
        '[bg][c]overlay=0:0:eof_action=pass,format=yuv420p[v]' % (t_cartao, t_cartao))
    alvo = os.path.join(FINAL, '%s-%s.mp4' % (chave, tipo))
    sh([FF, '-v', 'error', '-y', '-i', base_mp4,
        '-loop', '1', '-t', '4', '-i', g,
        '-loop', '1', '-t', '%.2f' % CARTAO, '-i', c,
        '-i', norm_wav,
        '-filter_complex', filtro, '-map', '[v]', '-map', '3:a',
        '-c:v', 'libx264', '-crf', '19', '-preset', 'slow', '-profile:v', 'high', '-r', '30',
        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', alvo])
    return alvo


if __name__ == '__main__':
    for chave, cfg in VIDEOS.items():
        b = base(chave, cfg)
        n = audio(chave, cfg)
        for tipo in ('reel', 'short'):
            print(final(chave, cfg, b, n, tipo))
