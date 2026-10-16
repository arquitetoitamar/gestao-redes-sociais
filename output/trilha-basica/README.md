# Trilha Básica do Marketplace Connect — estado em 13/10/2026

Brief: `~/git/meli-oauth-buddy/docs/planos/BRIEF-DEV-MIDIA-trilha-basica.md`
Plano: https://claude.ai/code/artifact/750375f2-8ec5-4479-9b25-be9c206b2d77

## Playlists criadas (não listadas)

| Trilha | Id | Link |
|---|---|---|
| Básica | `PLW3upCIZHed4` | https://www.youtube.com/playlist?list=PLW3upCIZHed4 |
| Avançada | `PLavmDN-e4LEE` | https://www.youtube.com/playlist?list=PLavmDN-e4LEE |

As 12 playlists que já existiam não foram tocadas.

## Na playlist básica (5 aulas)

| Pos | Aula | Vídeo | Observação |
|---|---|---|---|
| 0 | 4 | `e6YZbIU3oK8` | pronto, sem corte |
| 1 | 5 | `f1t_OJZBrxg` | o de 27/08, não o homônimo `0qUq0wKouF4` |
| 2 | 6 | `k1b8TMwiwg0` | entrou como está, por decisão do Itamar |
| 3 | 11 | `oE3QT7Ze3VM` | **novo** · corte 02:08.1→06:48.0 de `kvGLTgxkEjk` · 4m40 · não listado |
| 4 | 12 | `LtifaBOjLRQ` | pronto, sem corte |

Nenhum vídeo que já existia foi renomeado, teve descrição reescrita ou mudou de
visibilidade.

## Aula 11 — publicada com os ids tapados

O corte bom deixava os ids das contas do Mercado Livre na tela de 04:23 até o
fim. Com autorização do Itamar, abri exceção à regra de cópia de fluxo:
localizei cada ocorrência por OCR quadro a quadro, gerei 21 caixas sólidas
(`mascara-aula11.txt`) e recodifiquei em libx264 crf 18 — 23 segundos de
máquina. Conferência: OCR nos 280 quadros do arquivo final, **zero** ocorrência
de id de conta. O que sobrou de número longo é `MLB429215`, que é a categoria do
Mercado Livre e faz parte da aula. Contact sheet em `mascarado.jpg`.

Ponto a conferir quando assistir: em 01:55 do corte ele diz "marca genérica, que
eu não vou colocar ali a marca que é real". Na tela a própria IA sinaliza a
divergência de marca, o que joga a favor; o áudio sozinho é ambíguo.

## Aulas 1, 2 e 10 — sem fonte, entram na lista de gravação

Decisão de 13/10: viram gravação do Itamar, junto com 3, 7, 8, 9, 13 e 14.
Por quê:

- **1 e 2** — live 06/10 (`4Xti4U6Lt-A`). A abertura é música e queda de
  transmissão; a demo tem id de conta do Mercado Livre e da Shopee falados em
  voz alta, telefone e e-mail de importador, e margem de 30% e 100%.
- **10** — live 31/05 (`0kK3z0Ic4qU`). Os 50 primeiros minutos são estratégia,
  não mecânica. O tema multi-loja só aparece em dois fragmentos de ~30 s
  separados por 3 min. O entorno tem preço de plano, taxa de setup e consumo de
  token.

## Alternativas olhadas no acervo (163 vídeos)

- `kvarRdQXFo4` (4m39, "Marketplace Connect — Integre Seus Marketplaces") — o
  título engana: é dica de stock hitmap gravada às pressas, não um explicador.
- `fjrfmhMUD4M` (4m26, "Anúncio no mercado livre pelo Claude") — tema certo,
  mas filmado com celular apontado pro monitor, torto e ilegível.
- `IiPvKDJ0gMo` (4m14, "Conectando o ChatGPT nos marketplaces") — bom passo a
  passo, mas usa o fluxo de modo desenvolvedor, que a própria live de 06/10 diz
  ter mudado.

## Arquivos

- `manifesto-trilha-basica.json` — cópia do que está em `~/midia-tmp/`
- `mascara-aula11.txt` — as 21 caixas de drawbox usadas na aula 11
- `t_0610.txt`, `t_3105.txt` — legendas automáticas condensadas das duas lives
- `contato.jpg`, `tira.jpg`, `tira2.jpg` — frames da janela da aula 11 antes da máscara
- `mascarado.jpg` — o mesmo trecho depois da máscara

## Como trocar ou regravar uma aula

O manifesto é a fonte do padrão: nome, descrição, tags e ordem saem dele, não
do que eu digitar na hora. Para mudar o padrão de uma aula, edite a tabela em
[`scripts/trilha/monta_manifesto.py`](../../scripts/trilha/monta_manifesto.py)
e rode-o; ele reescreve o manifesto sem perder o que já está publicado.

```bash
cd scripts/trilha
python3 aula.py --estado                 # o que está em cada posição
python3 aula.py 7 ~/gravacoes/aula07.mp4 # publica ou substitui a aula 7
```

Publicar e substituir são o mesmo comando. Ele sobe como **não listado** com o
título e a descrição do manifesto, encaixa na posição certa pelo número da
aula, tira o vídeo anterior da playlist e atualiza o manifesto.

O vídeo substituído **nunca é apagado**: se foi este script que publicou, vira
privado; se é vídeo que já existia no canal, sai da playlist e mais nada.

## Padrão

| Campo | Regra |
|---|---|
| Título | `MC · Básico · Aula 07 — Qual endereço conectar` |
| Descrição | uma linha do que a aula resolve + link da playlist |
| Tags | `marketplace connect`, `trilha basica`, tema, `aula <n>` |
| Categoria | Educação |
| Visibilidade | não listado |

**As aulas 4, 5, 6 e 12 estão fora desse padrão** — são vídeos que já existiam
no canal e o brief proibiu renomear. Três são públicos e levam CTA próprio na
descrição (curso de Claude na 5, `?o=yt-conector` na 6); a 12 tem o rodapé do
Google Vids. Decisão pendente do Itamar.

## Conferir vídeo antes de publicar: o OCR não basta

Em 16/10 a Aula 06 subiu com o id da conta do Mercado Livre na tela. Duas
varreduras por OCR — a normal e uma com o quadro ampliado e `--psm 11` —
disseram que estava limpo. O tesseract lia `ID: 667706601` como
`IDESGAZOG001`: texto pequeno e cinza vira letra, e nenhum filtro de dígito
pega isso.

**O que funciona é olhar.** Monte um contact sheet (`fps=1/8,tile=5x4`), passe
o olho, e amplie onde houver tabela, cabeçalho de painel ou resposta de IA
listando conta. O OCR serve para achar a janela de tempo depois que você já
sabe o que procurar — não para dizer que não há nada.

Naquele vídeo a varredura visual achou três exposições que o OCR perdeu: o
e-mail no cabeçalho do painel, o e-mail na tela de autorização, e a resposta
final com o inventário de contas de cinco canais.
