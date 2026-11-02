"""Narração com a voz clonada do Itamar na HeyGen ("nova voz"), uma fala por arquivo.
uso: python3 tts.py [ids...]   -> audio/<id>.wav (48 kHz, sem silêncio nas pontas) + audio/<id>.words.json"""
import json, os, subprocess, sys
VOZ = '8bed0b172a10497cb244a2bd4fb73503'
TTS = os.path.expanduser('~/git/gestao-redes-sociais/.agents/skills/media-use/audio/scripts/heygen-tts.mjs')
env = dict(os.environ)
for l in open(os.path.expanduser('~/git/gestao-redes-sociais/.env')):
    if l.startswith('HEYGEN_API_KEY='):
        env['HEYGEN_API_KEY'] = l.split('=', 1)[1].strip().strip('"')
so = sys.argv[1:]
for it in json.load(open('narracao.json')):
    if so and it['id'] not in so:
        continue
    bruto = f"audio/{it['id']}_raw.wav"
    r = subprocess.run(['node', TTS, it['txt'], '-o', bruto, '--words', f"audio/{it['id']}.words.json",
                        '--voice', VOZ, '--lang', 'pt'], env=env, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr); sys.exit(1)
    out = f"audio/{it['id']}.wav"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', bruto, '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                    '-ar', '48000', '-ac', '1', out], check=True)
    os.remove(bruto)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out],
                             capture_output=True, text=True).stdout)
    print(it['id'], round(d, 2), flush=True)
