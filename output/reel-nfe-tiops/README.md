# Lançamento do Emissor NF-e no Instagram (31/10/2026)

Duas peças para o @tiopstecnologia, a partir de https://nfe.tiops.com.br e do banner
`~/git/nfe-tiops/divulgacao/capa-nfe-tiops-v1.png`.

| Peça | Arquivo | Legenda |
|---|---|---|
| Reel 9:16, 42,7 s, voz clonada do Itamar (HeyGen) | `reel_nfe_tiops.mp4` (fora do git, 14 MB) + `capa.jpg` | `legenda.md`, DM em `dm.md` |
| Post de novidade 4:5 | `novidade/post_novidade.jpg` | `novidade/legenda.md` |

Publicado: Reel em 31/10/2026 14:18 (https://www.instagram.com/reel/DfKrIZNib-Q/, `publicado_instagram.json`).
Post de novidade (versão e-commerce) agendado na AWS para 01/11/2026 18:00 (`scripts/ig-agendado`, id `novidade-nfe-20261101`).

## Refazer o Reel
```
python3 tts.py            # narração (HeyGen, voz 8bed0b17…, ~US$ 0,10)
python3 timeline.py       # tempos pelas palavras de audio/n*.words.json
WORKERS=3 python3 render.py frames   # quadros (Chrome do sistema, headless)
python3 music.py && python3 monta.py # trilha, mixagem (-14 LUFS) e mp4
```
`render.py frames` pode travar no fim depois de gravar todos os quadros: confira
`ls frames | wc -l` (1281) e siga.
