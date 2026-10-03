import json,base64,subprocess,os,sys,urllib.request
KEY=os.environ['GOOGLE_API_KEY']; VOICE=sys.argv[1] if len(sys.argv)>1 else 'Charon'
items=json.load(open('narracao.json'))
only=sys.argv[2:] 
for it in items:
    if only and it['id'] not in only: continue
    prompt="Leia em português do Brasil, como um apresentador de tecnologia gravando um Reels: tom animado e confiante, ritmo ágil e natural, sem pausas longas. Texto: "+it['txt']
    body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":VOICE}}}}}
    open('/tmp/_req.json','w').write(json.dumps(body))
    r=subprocess.run(['curl','-4','-s','-m','120','-X','POST','https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent','-H','x-goog-api-key: '+KEY,'-H','Content-Type: application/json','-d','@/tmp/_req.json'],capture_output=True)
    d=json.loads(r.stdout)
    raw=base64.b64decode(d['candidates'][0]['content']['parts'][0]['inlineData']['data'])
    out=f"audio/{it['id']}.wav"
    subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar','24000','-ac','1','-i','-','-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse','-ar','48000',out],input=raw)
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout)
    print(it['id'],round(dur,2),flush=True)
