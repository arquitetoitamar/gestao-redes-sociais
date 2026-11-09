import json, urllib.request, sys
H={'Authorization':'Bearer '+json.load(open('/Users/itamar/.google_gtm_youtube_token.json'))['access_token'],'Content-Type':'application/json'}
API='https://www.googleapis.com/youtube/v3/videos'
b=json.load(open(sys.argv[1]))
for i in sys.argv[2:]:
    s=json.loads(urllib.request.urlopen(urllib.request.Request(f'{API}?part=snippet&id={i}',headers=H)).read())['items'][0]['snippet']
    body={'id':i,'snippet':{k:s[k] for k in ('title','categoryId','tags','defaultLanguage','defaultAudioLanguage') if k in s}}
    body['snippet']['description']=b[i]['description']
    urllib.request.urlopen(urllib.request.Request(f'{API}?part=snippet',data=json.dumps(body).encode(),headers=H,method='PUT')).read()
    c=json.loads(urllib.request.urlopen(urllib.request.Request(f'{API}?part=snippet,status&id={i}',headers=H)).read())['items'][0]
    ok=c['snippet']['description']==b[i]['description'] and c['snippet']['title']==b[i]['title'] and c['snippet'].get('tags',[])==b[i]['tags'] and c['status']['privacyStatus']=='public'
    print('OK' if ok else 'DIVERGE', i, c['snippet']['title'][:50])
