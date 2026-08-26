# Agente "Cortes Pipeline" — publicação automática de Shorts e Reels

> **Origem:** `AGENTS.md` do projeto Claude "Gestão Redes Sociais" (10/ago/2026).
> **⚠️ Segredos removidos para versionamento.** Tokens, chaves e URLs assinadas
> foram substituídos por placeholders `${VARIAVEL}`. Os valores reais ficam em
> `.env` (não versionado) e nos caminhos locais indicados. Ver `.env.example`.

Agente autônomo para publicação de shorts no YouTube e Instagram Reels.

## Workflow principal

1. Ler `clipes_status.json` do S3 para encontrar o clipe do dia
2. Baixar vídeo do S3 se necessário
3. Postar no YouTube Shorts via `youtube_upload.py`
4. Postar no Instagram Reels via `instagram_upload.py`
5. Atualizar `clipes_status.json` com links e status
6. Upload do JSON atualizado para S3
7. Notificar WhatsApp via Chatiops MCP

## Comandos

### YouTube Shorts
```bash
cd /Users/itamar/git/cortes && python3 youtube_upload.py \
  "<caminho_do_video.mp4>" \
  "<titulo> #Shorts" \
  "<descricao>" \
  "<tag1>" "<tag2>" ...
```
- Token: `~/.hermes/credentials/youtube_token.pickle`
- Client secret: `~/client_secret.json`
- Scopes: `youtube.upload`, `youtube.readonly`, `yt-analytics.readonly`

### Instagram Reels
```bash
cd /Users/itamar/git/cortes && python3 instagram_upload.py \
  "<url_publica_do_video>" \
  "<caption>"
```
- O vídeo **precisa** estar em URL pública do S3
- Config: `~/.hermes/credentials/instagram_config.json`
- Token da página expira em ~24h. Renovar via Graph API Explorer.
- Scopes: `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`, `pages_read_engagement`

### Instagram Feed (imagem)
```python
import urllib.request, urllib.parse, json, time

config = json.load(open('/Users/itamar/.hermes/credentials/instagram_config.json'))
token = config['page_access_token']
ig_id = '17841475188821957'

# Step 1: criar container
url = f'https://graph.facebook.com/v22.0/{ig_id}/media'
data = urllib.parse.urlencode({
    'image_url': '<url_publica_da_imagem>',
    'caption': '<caption>',
    'access_token': token,
}).encode()
r = json.loads(urllib.request.urlopen(urllib.request.Request(url, data=data, method='POST')).read())
container_id = r['id']

# Step 2: aguardar processamento e publicar
time.sleep(5)
url2 = f'https://graph.facebook.com/v22.0/{ig_id}/media_publish'
data2 = urllib.parse.urlencode({'creation_id': container_id, 'access_token': token}).encode()
r2 = json.loads(urllib.request.urlopen(urllib.request.Request(url2, data=data2, method='POST')).read())
print(f'https://instagram.com/p/{r2["id"]}')
```

### Upload para S3
```bash
aws s3 cp <arquivo> s3://${S3_BUCKET}/temp/<nome> --region us-east-1
```
- Prefixos públicos: `temp/*`, `cortes/*`, `video-gen/*`
- **NUNCA** usar `--acl public-read` (a bucket policy controla o acesso)

### WhatsApp (Chatiops MCP)
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"send_whatsapp","arguments":{"number":"'"${WHATSAPP_NUMERO}"'","body":"<mensagem>","priority":"alta"}}}' \
  "https://api.chatiops.tiops.com.br/mcp?token=${CHATIOPS_TOKEN}"
```

## Fontes de dados

### `clipes_status.json` (S3)
```
https://${S3_BUCKET}.s3.amazonaws.com/cortes/clipes_status.json
```

Estrutura de cada clipe:
```json
{
  "rank": 1,
  "slug": "nome-do-clipe",
  "s3_url": "https://...mp4",
  "status_postagem": "pendente | publicado",
  "data_programada_youtube": "2026-08-15",
  "titulo_youtube": "Titulo #Shorts",
  "hook": "Frase de impacto",
  "link_postagem": "https://youtube.com/shorts/...",
  "link_postagem_instagram": "https://instagram.com/reel/...",
  "views_youtube": 0, "likes_youtube": 0,
  "views_instagram": 0, "likes_instagram": 0
}
```

### Dashboard público
```
https://${S3_BUCKET}.s3.amazonaws.com/cortes/clipes_status.html
```

## Calendário

- 51 clipes programados (#1–10 cropados, #11–51 originais)
- Postagem diária às 8h via cron `7c4f0ba0fb51`
- #5 estava atrasado (programado 08/ago)

## Descrição do YouTube — template

```
<descricao do conteudo>

🎬 Episódio completo: https://youtu.be/LyDN9e8jgJY
📌 Inscreva-se: @tiopstecnologia
```

## Canais

- YouTube: `@tiopstecnologia`
- Instagram: `@tiopstecnologia` (IG ID: `17841475188821957`)
- Facebook Page ID: `790180970850516`

## Pitfalls

- **Instagram:** o vídeo precisa estar em URL pública do S3 (não arquivo local)
- **Instagram:** page token expira em ~24h. Se falhar, renovar no Graph API Explorer
- **YouTube:** token OAuth expira periodicamente, renovar com `~/client_secret.json`
- **S3:** a bucket policy bloqueia `--acl public-read`; arquivos são públicos por policy
- **Cron:** local-only, não roda com o Mac dormindo
- **Dashboard HTML:** adicionar `?t=' + Date.now()` no fetch para evitar cache
- **Nunca** postar no Slack sem aprovação explícita do Itamar
