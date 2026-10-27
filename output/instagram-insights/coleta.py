"""Coleta insights de todos os posts do @tiopstecnologia (Graph API v22).
Saída: posts.json (um registro por post, com métricas). Não imprime token."""
import json, os, sys, urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor

CFG = json.load(open(os.path.expanduser('~/.hermes/credentials/instagram_config.json')))
TOK = CFG['access_token']
IG = CFG['ig_account_id']
API = 'https://graph.facebook.com/v22.0/'

def get(path, **p):
    p['access_token'] = TOK
    u = path if path.startswith('http') else API + path + '?' + urllib.parse.urlencode(p)
    try:
        return json.loads(urllib.request.urlopen(u, timeout=60).read())
    except urllib.error.HTTPError as e:
        return {'error': json.loads(e.read()).get('error', {}).get('message', str(e))}

def todos_posts():
    campos = 'id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count'
    r = get(f'{IG}/media', fields=campos, limit=100)
    out = r.get('data', [])
    while r.get('paging', {}).get('next'):
        r = get(r['paging']['next'])
        out += r.get('data', [])
    return out

METRICAS = {
    'REELS': ['reach', 'views', 'likes', 'comments', 'shares', 'saved', 'total_interactions',
              'ig_reels_avg_watch_time', 'ig_reels_video_view_total_time'],
    'FEED':  ['reach', 'views', 'likes', 'comments', 'shares', 'saved', 'total_interactions',
              'follows', 'profile_visits'],
}

def insights(post):
    tipo = post.get('media_product_type', 'FEED')
    ms = METRICAS.get(tipo, METRICAS['FEED'])
    r = get(f"{post['id']}/insights", metric=','.join(ms))
    if 'error' in r:  # alguma métrica não suportada: tenta uma a uma
        r = {'data': []}
        for m in ms:
            x = get(f"{post['id']}/insights", metric=m)
            r['data'] += x.get('data', [])
    post['m'] = {d['name']: d['values'][0]['value'] for d in r.get('data', [])}
    return post

def limpa(o):
    """Tira 'paging': as URLs de próxima página carregam o access_token."""
    if isinstance(o, dict): return {k: limpa(v) for k, v in o.items() if k != 'paging'}
    if isinstance(o, list): return [limpa(x) for x in o]
    return o

def conta_30d():
    import time
    ate = int(time.time()); de = ate - 29 * 86400
    j = dict(since=de, until=ate)
    out = {
        'reach_dia': get(f'{IG}/insights', metric='reach', period='day', **j),
        'seguidores_dia': get(f'{IG}/insights', metric='follower_count', period='day', **j),
        'totais_30d': get(f'{IG}/insights', metric='reach,accounts_engaged,profile_views,views,total_interactions',
                          period='day', metric_type='total_value', **j),
        'follows_breakdown': get(f'{IG}/insights', metric='follows_and_unfollows', period='day',
                                 metric_type='total_value', breakdown='follow_type', **j),
        'reach_por_tipo': get(f'{IG}/insights', metric='reach', period='day', metric_type='total_value',
                              breakdown='media_product_type', **j),
    }
    for b in ['city', 'age', 'gender']:
        out['demo_' + b] = get(f'{IG}/insights', metric='follower_demographics', period='lifetime',
                               metric_type='total_value', breakdown=b)
    return out

posts = todos_posts()
with ThreadPoolExecutor(8) as ex:
    posts = list(ex.map(insights, posts))
conta = get(IG, fields='username,followers_count,follows_count,media_count')
json.dump(limpa({'conta': conta, 'posts': posts}), open('posts.json', 'w'), ensure_ascii=False, indent=1)
json.dump(limpa(conta_30d()), open('conta.json', 'w'), ensure_ascii=False, indent=1)
print(len(posts), 'posts;', sum(1 for p in posts if p['m']), 'com métricas')
