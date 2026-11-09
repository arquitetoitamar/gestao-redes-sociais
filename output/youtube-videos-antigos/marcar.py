import json, urllib.request, urllib.parse, re, sys, os
TOK='/Users/itamar/.google_gtm_youtube_token.json'
H={'Authorization':'Bearer '+json.load(open(TOK))['access_token'],'Content-Type':'application/json'}
API='https://www.googleapis.com/youtube/v3/videos'
LINK='https://youtu.be/e5RfKvZPLL4'
MES={'04':'abr','05':'mai','06':'jun','07':'jul','08':'ago'}
MARCA='⚠️ Vídeo de '
modo=sys.argv[1]; backup=sys.argv[2]; only=sys.argv[3:]  # modo: dry|apply
v=json.load(open('videos.json')); seen=set(); ids=[]
for x in v:
    if x['id'] in seen: continue
    seen.add(x['id'])
    t=x['titulo'].lower()
    if x['priv']=='public' and x['seg']>180 and '2026-04'<=x['data']<'2026-09-01' and re.search(r'mercado|shopee|marketplace|gestorpro|claude|chatgpt|bling|chatiops|whatsapp|an[uú]ncio|agentes|tiktok shop',t):
        ids.append(x['id'])
if only: ids=[i for i in ids if i in only]
snips={}
for k in range(0,len(ids),50):
    r=json.loads(urllib.request.urlopen(urllib.request.Request(API+'?'+urllib.parse.urlencode({'part':'snippet','id':','.join(ids[k:k+50])}),headers=H)).read())
    for it in r['items']: snips[it['id']]=it['snippet']
if not os.path.exists(backup):
    json.dump({i:{'title':s['title'],'description':s.get('description',''),'tags':s.get('tags',[])} for i,s in snips.items()},open(backup,'w'),ensure_ascii=False,indent=1)
ok=skip=fail=0
for i in ids:
    s=snips[i]; desc=s.get('description','')
    if desc.startswith(MARCA): skip+=1; print('JA',i); continue
    mes=MES[s['publishedAt'][5:7]]
    nova=f"{MARCA}{mes}/2026, versão antiga. Veja o que mudou: {LINK}\n\n"+desc
    if len(nova)>5000 or '<' in nova or '>' in nova: fail+=1; print('LIMITE',i,len(nova)); continue
    body={'id':i,'snippet':{k:s[k] for k in ('title','categoryId','tags','defaultLanguage','defaultAudioLanguage') if k in s}}
    body['snippet']['description']=nova
    if modo=='dry': print('OK-dry',i,mes,len(nova),s['title'][:50]); ok+=1; continue
    try:
        r=json.loads(urllib.request.urlopen(urllib.request.Request(API+'?part=snippet',data=json.dumps(body).encode(),headers=H,method='PUT')).read())
        assert r['snippet']['description'].startswith(MARCA)
        ok+=1; print('OK',i,mes,s['title'][:50])
    except urllib.error.HTTPError as e:
        fail+=1; print('ERRO',i,e.code,e.read()[:200])
print(f'ok={ok} ja={skip} falha={fail} total={len(ids)}')
