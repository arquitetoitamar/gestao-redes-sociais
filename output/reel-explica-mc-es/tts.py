"""Narração em espanhol com a voz clonada do Itamar na HeyGen (c463ef5b).
uso: python3 tts.py <narracao.json> <pasta_audio> [ids...] -> <pasta>/<id>.wav + <id>.words.json"""
import json, os, subprocess, sys
VOZ = 'c463ef5bf11146d49bf754fa1e515401'
TTS = os.path.expanduser('~/git/gestao-redes-sociais/.agents/skills/media-use/audio/scripts/heygen-tts.mjs')
env = dict(os.environ)
for l in open(os.path.expanduser('~/git/gestao-redes-sociais/.env')):
    if l.startswith('HEYGEN_API_KEY='):
        env['HEYGEN_API_KEY'] = l.split('=', 1)[1].strip().strip('"')
narr, pasta, so = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(pasta, exist_ok=True)
for it in json.load(open(narr)):
    if so and it['id'] not in so:
        continue
    bruto = f"{pasta}/{it['id']}_raw.wav"
    r = subprocess.run(['node', TTS, it['txt'], '-o', bruto, '--words', f"{pasta}/{it['id']}.words.json",
                        '--voice', VOZ, '--lang', 'es'], env=env, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr); sys.exit(1)
    out = f"{pasta}/{it['id']}.wav"
    # silêncio inicial que o corte remove: desloca as palavras para o áudio cortado
    sd = subprocess.run(['ffmpeg', '-i', bruto, '-af', 'silencedetect=n=-45dB:d=0.01', '-f', 'null', '-'],
                        capture_output=True, text=True).stderr
    lead = 0.0
    for ln in sd.splitlines():
        if 'silence_start: 0' in ln or 'silence_start: -' in ln:
            continue
        if 'silence_end' in ln:
            lead = float(ln.split('silence_end:')[1].split('|')[0]); break
    wp = f"{pasta}/{it['id']}.words.json"
    ws = json.load(open(wp))
    for w in ws:
        w['start'] = round(max(0, w['start'] - lead), 3); w['end'] = round(max(0, w['end'] - lead), 3)
    json.dump(ws, open(wp, 'w'), ensure_ascii=False, indent=1)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', bruto, '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                    '-ar', '48000', '-ac', '1', out], check=True)
    os.remove(bruto)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out],
                             capture_output=True, text=True).stdout)
    print(it['id'], round(d, 2), flush=True)
