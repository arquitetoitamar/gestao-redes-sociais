import json, os, sys, time, urllib.request, urllib.parse, urllib.error

TOK = os.path.expanduser('~/.google_gtm_youtube_token.json')
SEC = os.path.expanduser('~/client_secret.json')
API = 'https://www.googleapis.com/youtube/v3/'


def _tok():
    return json.load(open(TOK))


def refresh():
    t = _tok()
    s = json.load(open(SEC))
    c = s.get('installed') or s.get('web')
    body = urllib.parse.urlencode({
        'client_id': c['client_id'],
        'client_secret': c['client_secret'],
        'refresh_token': t['refresh_token'],
        'grant_type': 'refresh_token',
    }).encode()
    r = urllib.request.urlopen('https://oauth2.googleapis.com/token', body)
    new = json.load(r)
    t['access_token'] = new['access_token']
    json.dump(t, open(TOK, 'w'), indent=2)
    return t['access_token']


def call(method, path, params=None, body=None, retry=True):
    url = API + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    hdr = {'Authorization': 'Bearer ' + _tok()['access_token']}
    if data:
        hdr['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=hdr, method=method)
    try:
        r = urllib.request.urlopen(req)
        bruto = r.read()
        return json.loads(bruto) if bruto else {}
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            refresh()
            return call(method, path, params, body, retry=False)
        if e.code in (429, 500, 502, 503) and retry:
            time.sleep(3)
            return call(method, path, params, body, retry=False)
        sys.stderr.write('HTTP %s %s\n%s\n' % (e.code, url, e.read().decode()[:800]))
        raise
    except urllib.error.URLError:
        if not retry:
            raise
        time.sleep(3)
        return call(method, path, params, body, retry=False)
