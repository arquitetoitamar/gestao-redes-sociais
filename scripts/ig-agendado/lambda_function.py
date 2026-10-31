"""Publica um post agendado no Instagram (@tiopstecnologia) — Lambda tiops-ig-agendado.

Chamada pelo EventBridge Scheduler na hora marcada, sem depender do Mac. Evento:
  {"id": "reel-nfe-claude-20261031", "tipo": "reel"|"imagem", "url": "<mídia pública no S3>",
   "key": "temp/agendados/...", "caption": "...", "comentario": "...", "thumb_offset": 2500,
   "apagar_midia": true, "teste": false}
Com "teste": true só confere o token e se a mídia está acessível; não publica nada.

Idempotente: grava agendados-estado/<id>.json antes de publicar; se a marca já existe, não roda de novo.
"""
import json, os, time, urllib.error, urllib.parse, urllib.request
import boto3

S3 = boto3.client('s3')
SM = boto3.client('secretsmanager')
BUCKET = os.environ['BUCKET']
SECRET = os.environ['SECRET']
V = os.environ.get('GRAPH_VERSION', 'v22.0')
G = 'https://graph.facebook.com/' + V


def http(metodo, url, dados=None):
    corpo = urllib.parse.urlencode(dados).encode() if dados else None
    req = urllib.request.Request(url, data=corpo, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        try:
            out = json.loads(e.read() or b'{}')
        except Exception:
            out = {}
        out['_http'] = e.code
        return out


def estado(pid, dados):
    S3.put_object(Bucket=BUCKET, Key='agendados-estado/%s.json' % pid, ContentType='application/json',
                  Body=json.dumps(dados, ensure_ascii=False).encode())


def ja_rodou(pid):
    try:
        S3.head_object(Bucket=BUCKET, Key='agendados-estado/%s.json' % pid)
        return True
    except Exception:
        return False


def handler(event, context):
    pid = event['id']
    cfg = json.loads(SM.get_secret_value(SecretId=SECRET)['SecretString'])
    ig, tok = cfg['ig_account_id'], cfg['token']

    if event.get('teste'):
        conta = http('GET', '%s/%s?%s' % (G, ig, urllib.parse.urlencode({'fields': 'username', 'access_token': tok})))
        try:
            with urllib.request.urlopen(urllib.request.Request(event['url'], method='HEAD'), timeout=30) as r:
                midia = r.status
        except urllib.error.HTTPError as e:
            midia = e.code
        return {'conta': conta.get('username', conta), 'midia_http': midia, 'ja_rodou': ja_rodou(pid)}

    if ja_rodou(pid):
        print('já rodou, nada a fazer', pid)
        return {'ja_rodou': pid}
    estado(pid, {'status': 'iniciado', 'em': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
    try:
        dados = {'access_token': tok, 'caption': event['caption']}
        if event['tipo'] == 'reel':
            dados.update(media_type='REELS', video_url=event['url'], share_to_feed='true')
            if event.get('thumb_offset') is not None:
                dados['thumb_offset'] = str(int(event['thumb_offset']))
        else:
            dados['image_url'] = event['url']
        r = http('POST', '%s/%s/media' % (G, ig), dados)
        if 'id' not in r:
            raise RuntimeError('container recusado: %s' % r)
        cid = r['id']
        for _ in range(100):
            s = http('GET', '%s/%s?%s' % (G, cid, urllib.parse.urlencode({'fields': 'status_code,status', 'access_token': tok})))
            if s.get('status_code') == 'FINISHED':
                break
            if s.get('status_code') in ('ERROR', 'EXPIRED'):
                raise RuntimeError('processamento falhou: %s' % s)
            time.sleep(5)
        else:
            raise RuntimeError('Instagram não processou a mídia a tempo')
        p = http('POST', '%s/%s/media_publish' % (G, ig), {'creation_id': cid, 'access_token': tok})
        if 'id' not in p:
            raise RuntimeError('publicação recusada: %s' % p)
        mid = p['id']
        info = http('GET', '%s/%s?%s' % (G, mid, urllib.parse.urlencode({'fields': 'permalink,timestamp', 'access_token': tok})))
        res = {'status': 'publicado', 'id': mid, 'url': info.get('permalink'), 'quando': info.get('timestamp')}
        if event.get('comentario'):
            c = http('POST', '%s/%s/comments' % (G, mid), {'message': event['comentario'], 'access_token': tok})
            res['comentario'] = c.get('id', c)
        if event.get('apagar_midia') and event.get('key'):
            S3.delete_object(Bucket=BUCKET, Key=event['key'])
        estado(pid, res)
        print(json.dumps(res))
        return res
    except Exception as e:
        estado(pid, {'status': 'erro', 'erro': str(e)[:1500]})
        raise
