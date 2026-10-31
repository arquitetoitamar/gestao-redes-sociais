---
name: treinamento-gestorpro
description: Grava uma aula do treinamento GestorPro a partir de uma tela do GestorPro (aberta no Chrome já logado) e de um roteiro do Itamar — captura a tela em retina, narra com o avatar e a voz do Itamar (HeyGen), anima zoom, rolagem, destaques, cartões e cursor conforme a fala, gera capa sem foto e sobe NÃO LISTADO na playlist "GestorPro — Treinamento". Use em "grava o treinamento do GestorPro", "aula do GestorPro da tela X", "gera a próxima aula com este roteiro", "treinamento de <tela> no mesmo padrão".
---

# Aula do treinamento GestorPro

Padrão aprovado em 31/10/2026 com a aula "Promoções e Guardião de margem"
(`output/aula-gestorpro-promocoes/`, https://youtu.be/nNvF3JV_5Ns). O motor está em
`motor/`; a pasta de cada aula guarda só os dados (narração, roteiro visual, capturas, vídeos).

Entrada do usuário: **URL da tela** (ex.: `https://gestorpro.tiops.com.br/escritorio.html#/promotions?acct=all&p=2026-10`)
e **roteiro** (seções com o que dizer e o que mostrar). Saída: link não listado + link da playlist.

## Regras que não mudam
- Treinamento é para outras lojas: **olho de privacidade fechado** (botão "Mostrar valores" no topo
  com `aria-label="Mostrar valores"` = valores e nomes de produto borrados). A narração **não lê**
  valores, faturamento, margem ou nomes da loja do ensaio; explica o que cada número significa.
- Nunca clicar em botão que muda dado: Enviar para aprovação, Mandar para a fila, Rodar o motor,
  Sincronizar, Conferir…, interruptores. Só navegação (abas, "abrir", links de tela).
- Abertura simples (cartela "TREINAMENTO GESTORPRO" + título), sem as cenas da Imersão.
  Capa **sem foto** do Itamar.
- Mostrar o custo do HeyGen antes de gerar. Publicar só depois do vídeo pronto e conferido.

## Passo a passo
Defina `S=.agents/skills/treinamento-gestorpro` e `A=output/aula-gestorpro-<tema>`.

1. **Pasta**: `mkdir -p $A/{capturas,trab,videos}`; `.gitignore` com `videos/ trab/ capturas/ *.mp4 *.wav`;
   copie `$S/modelo/roteiro.py` e escreva `$A/narracao.md` (uma seção por `## N. Título`, fala corrida,
   primeira pessoa, frases curtas; ~5 a 8 min no total). Preencha `AULA` e `CAPITULOS` no roteiro.
2. **Avatar e voz** (HeyGen, gêmeo digital `fcd7fefe…` + voz "nova voz" `8bed0b17…`):
   `python3 $S/motor/heygen.py $A saldo` → custo ≈ US$ 0,62/min (avatar_iii; a aula de 6 min custou US$ 3,71).
   Avise o custo, depois `heygen.py $A cria todas` e `heygen.py $A espera` (repita até todas prontas;
   baixa `videos/av-N.mp4` e grava o tempo por palavra em `trab/pal-N.json`). Carteira zerada → peça recarga
   em platform.heygen.com (é separada da assinatura).
3. **Captura da tela** (Claude in Chrome + capturador nativo):
   - Abra a URL numa aba do grupo do Claude; confira o olho fechado; esconda o robô flutuante:
     `document.head.insertAdjacentHTML('beforeend','<style>.robo-global{display:none!important}</style>')`.
   - Retina: a janela no monitor externo sai 1x. Peça licença ao usuário, leve a janela para a tela do
     notebook e ative a aba controlada (o id da aba do AppleScript é o mesmo `tabId` da extensão):
     `osascript -e 'tell application "Google Chrome" to set bounds of window 1 to {0, 33, 1470, 956}'`.
     No fim, devolva os `bounds` anteriores.
   - Meça os blocos (pontos CSS dentro de `main`, já somando `main.scrollTop`) com
     `getBoundingClientRect()` para preencher as constantes do roteiro.
   - **Faixas da rolagem**: rode `python3 $S/motor/captura.py $A 90` em segundo plano e, na página,
     agende (a extensão deixa brilho rosa nas bordas e um cursor laranja por ~15 s depois de cada comando;
     por isso a espera de 20 s):
     ```js
     setTimeout(async () => { const sleep = ms => new Promise(r => setTimeout(r, ms));
       const main = document.querySelector('main'), orig = document.title, H = main.scrollHeight;
       let p = 0; while (true) { main.scrollTop = p; await sleep(2400);
         document.title = 'CAP-faixa-' + String(Math.round(main.scrollTop)).padStart(5,'0') + '-h' + innerHeight;
         await sleep(900); document.title = orig; await sleep(200);
         if (p >= H - main.clientHeight) break; p = Math.min(p + 560, H - main.clientHeight); }
       main.scrollTop = 0; }, 20000); 'agendado'
     ```
   - **Estados** (outra página, modal, aba): mesmo esquema, com `element.click()` dentro do `setTimeout`
     e título `CAP-<nome>-h<innerHeight>`. Declare em `ESTADOS` do roteiro (`tela` ou `pagina` + `scroll`).
   - `python3 $S/motor/prepara.py $A` costura `capturas/pagina.png` e `moldura16x9.png`. Se avisar
     **NÃO BATE**, a página recarregou entre faixas (tabelas mudam de tamanho): tire a faixa ruim e recapture.
4. **Roteiro visual** (`roteiro.py`): eventos disparados por trechos da fala **como o whisper escreveu**
   (ex.: "pra" em vez de "para", "vai e vem"); `python3 $S/motor/aula.py $A tempos` acusa o trecho que
   não achou. Tipos: `foco`, `luz` (com `rot`), `cartao`, `grande`, `clique`, `estado`, `geral`, `apaga`, `fecha`.
   Linha larga perto do fim da página → `foco` com `z` 1.05 (só centraliza); botão pequeno → `z` 1.6.
   Confira com `aula.py $A quadros t1,t2,…` (JPGs em `trab/`).
5. **Render**: confira `df -h ~` (≥ 1,5 GB livres: a swap do Mac usa o mesmo disco e 6 processos enchem tudo);
   `python3 $S/motor/aula.py $A` (3 processos) → `videos/final.mp4`. Se cair no áudio, `aula.py $A junta`.
6. **Capa**: Higgsfield `gpt_image_2_5` (16:9, high, 2k, ~2,75 créditos) com a captura da tela como
   referência; fundo azul-marinho, pílula amarela "TREINAMENTO GESTORPRO", título em 3 linhas grandes
   (branco/amarelo/branco), subtítulo azul-claro, janela do app inclinada à direita e um ícone 3D do tema.
   Salve como `$A/thumb.jpg` 1280x720.
7. **Publicar**: `python3 $S/motor/publica.py $A texto`, depois `sobe` → não listado, capa, playlist
   "GestorPro — Treinamento" (`PLZKCwN02VMgU`, criada em 31/10/2026), `containsSyntheticMedia: true`.
   Responda com o link do vídeo e o da playlist.
8. **Limpar**: depois do YouTube processar, apague `$A/videos` e os WAV de `trab/`; commit e push só dos
   textos da aula (`narracao.md`, `roteiro.py`, `publicado.json`, `thumb.jpg`, `.gitignore`).
