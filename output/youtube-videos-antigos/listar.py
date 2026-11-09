import json, urllib.request, urllib.parse, re, sys
TOK='/Users/itamar/.google_gtm_youtube_token.json'
t=json.load(open(TOK)); c=json.load(open('/Users/itamar/client_secret.json'))
inst=c.get('installed') or c.get('web')
d=urllib.parse.urlencode({'refresh_token':t['refresh_token'],'client_id':inst['client_id'],'client_secret':inst['client_secret'],'grant_type':'refresh_token'}).encode()
n=json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',data=d)).read())
t['access_token']=n['access_token']; json.dump(t,open(TOK,'w'),indent=2)
H={'Authorization':'Bearer '+t['access_token']}
def get(u,p):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u+'?'+urllib.parse.urlencode(p),headers=H)).read())
ch=get('https://www.googleapis.com/youtube/v3/channels',{'part':'contentDetails','mine':'true'})
up=ch['items'][0]['contentDetails']['relatedPlaylists']['uploads']
ids=[];tok=None
while True:
    p={'part':'contentDetails','playlistId':up,'maxResults':50}
    if tok:p['pageToken']=tok
    r=get('https://www.googleapis.com/youtube/v3/playlistItems',p)
    ids+= [i['contentDetails']['videoId'] for i in r['items']]
    tok=r.get('nextPageToken')
    if not tok:break
out=[]
for k in range(0,len(ids),50):
    r=get('https://www.googleapis.com/youtube/v3/videos',{'part':'snippet,statistics,status,contentDetails,liveStreamingDetails','id':','.join(ids[k:k+50])})
    for v in r['items']:
        dur=v['contentDetails']['duration']
        m=re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',dur); dd,h,mi,s=[int(x or 0) for x in m.groups()]
        out.append({'id':v['id'],'data':v['snippet']['publishedAt'][:10],'titulo':v['snippet']['title'],'views':int(v['statistics'].get('viewCount',0)),
          'priv':v['status']['privacyStatus'],'seg':dd*86400+h*3600+mi*60+s,'live':'liveStreamingDetails' in v})
out.sort(key=lambda x:x['data'])
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
print(len(out),'videos')
