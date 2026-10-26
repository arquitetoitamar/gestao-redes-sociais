# Shorts — semana de 27/10 a 02/11

14 Shorts, 2 por dia: 08:00 (negócio) e 18:00 (história pessoal).
`agenda.py` tem a lista com título, descrição e tags já validados contra
os limites do YouTube. **Nada foi publicado nem agendado** — falta a
decisão de canal (abaixo).

## O que entrou

Sete peças já produzidas (`~/Downloads`) e sete cortes verticais novos,
feitos aqui a partir do vlog da casa nova (`output/offtopic-casa-nova`).

Os cortes saem de `monta.py`: fundo é o próprio quadro ampliado e
desfocado, o 16:9 original fica centrado, gancho fixo em cima e legenda
rolante embaixo — tudo em PNG do PIL, porque o ffmpeg desta máquina não
tem `drawtext` nem libass. Os tempos ficam em `cortes.py`, conferidos
contra os SRT do vlog.

```bash
python3 monta.py          # refaz os 8 cortes
python3 agenda.py         # confere limites e imprime o calendário
```

## O que ficou de fora, e por quê

- **`remoto.mp4`** (renderiza, mas não está na agenda): o Samuel aparece
  em quadro quase o tempo todo. No vlog completo, que está como não
  listado, isso é uma coisa; num Short, que o YouTube empurra para
  desconhecidos, é outra. Decisão do Itamar.
- **`ostentar.mp4`** foi aparado de 36 s para 15 s. O trecho original
  seguia para "meus filhos podem brincar aqui à vontade, ele pode sair
  na rua" — isto é, a rotina das crianças somada à cidade, que o vlog já
  diz em voz alta. O corte fecha antes disso.
- **Nenhum corte usa `01-3866.mp4`**, o clipe da entrada: é onde o número
  da casa fica legível.
- **Os 14 clipes `IMG_97xx`/`IMG_98xx`** (gravações da Imersão de 24/10)
  não entraram: aparecem terceiros identificáveis, clientes falando os
  próprios números e linha de produto, e métrica interna da Tiops. Só o
  `IMG_9703` tem consentimento dito em câmera. Ver a conversa.
- **`humanoid.mp4`** traz crédito "RICARDO AMORIM" na tela — material de
  terceiro.
- **`Security_camera_video_advertisement_*`** e **`br-11110105-*`** são
  anúncios de produto, não conteúdo de canal.
- **`preview_voz_generica.mp4`** termina em "Saiba mais, Nabil" — defeito
  da voz sintética.
- **`ugcmarketplaceconnect.mp4`** é quase igual ao `novo`; fica de reserva.

## Pendente

O token do `google-gtm-youtube` só alcança o canal `UC4mEWT48J1erkqlbHqfHpEg`
("Itamar Rocha"). Se o offtopic for canal separado, os sete cortes do vlog
precisam de uma autorização OAuth nova.
