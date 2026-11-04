# Anúncio Meta: Argentina (teste de 3 dias)

Criado em 03/11/2026 no Gerenciador de Anúncios, conta `1322329366662228`. O Itamar autorizou
"30 reais por dia durante 3 dias".

| Nível | Nome | ID |
|---|---|---|
| Campanha | AR \| Trafego \| Connect ES \| nov-26 (objetivo Tráfego) | 120255058273400007 |
| Conjunto | AR \| Vendedores ML \| 25-55 \| ES | 120255058273390007 |
| Anúncio | AR \| Reel explica MC \| vos \| ES | 120255058273410007 |

## Orçamento e período

- **Orçamento total de R$ 90**, em 3 dias. Usei orçamento total em vez de diário porque o
  diário pode gastar até 75% a mais num dia.
- De 03/11 16:41 a 06/11 16:41 (horário de Brasília).

## Público

- **Onde:** só Argentina.
- **Idade:** 25 a 55 anos.
- **Segmentação** (público limitado, sem "usar como sugestão"):
  - quem é "Administradores de página comercial" **OU** "Proprietários de pequenas empresas";
  - **E** tem interesse em "MercadoLivre".
- **Tamanho estimado:** 850 mil a 1 milhão de pessoas.
- **Posicionamentos:** Advantage+ (automáticos).

## Anúncio

- **Vídeo:** `saida/reel_mc_es_anuncio_ar_meta.mp4` (versão "vos", 48 s, termina em
  "Tocá Más información").
- **Texto principal:** "Tu IA ya puede operar tu tienda de Mercado Libre: le pedís en español,
  prepara el cambio y vos aprobás. Publicaciones, precios, stock y preguntas, todo desde una
  conversación con Claude o ChatGPT. Ya disponible en Argentina."
- **Título:** "Conectá tu Mercado Libre a tu IA". **Descrição:** "Una autorización, sin código."
- **Botão:** Saiba mais (aparece como "Más información" para quem usa o Facebook em espanhol).
- **Destino:** `https://l.tiops.com.br/ar?o=meta-ar`, que leva à página da Argentina.
- **Meta:** visualizações da página de destino.
- **Recursos de IA do Meta desligados:** melhorias no texto, retoques de vídeo, efeitos de
  vídeo, aprimorar CTA e detalhes no layout. Só "comentários relevantes" ficou ligado.

## Como medir (06/11)

- Cliques humanos no slug `ar` com `o=meta-ar` (`link_cliques`).
- Lojas MLA novas conectadas no período (`site_id = MLA`, tag argentina no CRM).
- Custo por visualização da página no Gerenciador.
- Se acabar sem nenhuma loja MLA, consertar o funil (cadastro em espanhol) antes de gastar mais.

## Leitura 1: 03/11, 20:45 (cerca de 4 h no ar)

| Métrica | Valor |
|---|---|
| Gasto | R$ 5,50 de R$ 90 |
| Impressões / alcance | 843 / 695 (frequência 1,21) |
| CPM | R$ 6,52 |
| Cliques no link | 16 (CTR 1,90%, CPC R$ 0,34) |
| Visualizações da página de destino | 13 (R$ 0,42 cada) |

- **Encurtador:** `ar` registrou 40 cliques "humanos" com `o=meta-ar`, mais 219 robôs. O
  número fica acima dos 16 do Meta porque a revisão e as pré-visualizações do Meta também
  batem no link. Vale o número do Meta.
- **Comparação:** a campanha BR do Reel do Claude custava R$ 0,20 por visita. A da Argentina
  sai pelo dobro, mas com impressão barata e CTR alto.
- **Orgânico:**
  - Short no YouTube: 4 visualizações.
  - Cliques `o=youtube`: 6 no `ar` e 5 no `mx`, mais que as visualizações, então
    provavelmente são o verificador de links do YouTube.
  - Instagram: não foi possível ler os números (o Chrome mostrou página de erro).
- **Lojas conectadas** (DEV-MC, de 16:41 a 20:47, sem os usuários de teste):
  - 0 lojas MLA e 0 lojas MLM;
  - 2 cadastros novos, de qualquer origem.

  O cadastro não guarda a origem do link curto, então não dá para atribuir os 2 ao anúncio.

## 03/11, 21h: destino trocado

- **Pedido do Itamar:** levar para a página principal em vez da página da Argentina.
- **Slugs `ar` e `mx`:** apontam para `https://marketplaces.tiops.com.br/` (sem `?o=` fixo).
- **O link do anúncio não mudou**, então não houve nova revisão.
- **Origem até o cadastro** (DEV-MC):
  - PR #502: o redirect anexa `o`, `ind` e `utm_*` do clique ao destino;
  - PR #500: o cadastro grava `customer_profiles.origem`.
- **#502 no ar (03/11, noite):** `l.tiops.com.br/ar?o=meta-ar` redireciona para
  `https://marketplaces.tiops.com.br/?o=meta-ar`. Daqui em diante, o cadastro vindo do anúncio
  grava `customer_profiles.origem = meta-ar`.
- **Na medição, descontar os cliques de teste** da DEV-MC e meus: `o=teste`, `o=teste-ajuste`,
  `o=teste-deploy` e `o=teste-final`.
