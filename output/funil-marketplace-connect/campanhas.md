# Campanhas do funil Marketplace Connect (Brasil)

Criadas em 03/11/2026, por volta de 23h, pelo conector Meta ADS, com o OK do Itamar ao plano de R$ 1.000
(`estrategia.md`). O início estava marcado para 04/11 às 08h; a pedido do Itamar, foi antecipado
para **03/11 às 23h20**. Às 23h23 os três anúncios estavam aprovados e com entrega "preparing",
sem erro de pagamento.

| Campanha | Conjunto | Anúncio | Verba total | Período |
|---|---|---|---|---|
| `120255061318190007` MC \| Topo VSL /comece \| Tráfego LPV | `120255061320240007` A1 (80%) | `120255061346410007` Reel "Claude + ML + Shopee" (post 26/06 `18103749911014452`) | R$ 360 | 03/11 23h20 a 04/12 |
| (mesma) | `120255061329580007` A2 (teste) | `120255061346580007` Reel explicativo PT (post 29/09 `18025844813858148`) | R$ 90 | 03/11 23h20 a 18/11 |
| `120255061318320007` MC \| Isca avaliar anúncio grátis | `120255061330480007` B | `120255061346810007` Reel viral "nota do anúncio" (post 14/08 `18020078531879388`) | R$ 200 (no nível da campanha) | 03/11 23h20 a 04/12 |

**México** (criada em 04/11 às 13h, a pedido do Itamar, no mesmo molde da Argentina):

| Campanha | Conjunto | Anúncio | Verba total | Período |
|---|---|---|---|---|
| `120255074686820007` MX \| Trafego \| Connect ES | `120255074690090007` México, 25+ (sugestão 25–55), MercadoLivre E (donos de pequenas empresas OU administradores de página) | `120255074694310007` Reel em espanhol "tú" (post 03/11 `17865776925694327`) → `l.tiops.com.br/mx?o=meta-mx` | R$ 90 (no nível da campanha) | 04/11 13h10 a 07/11 13h10 |

A página principal abre em espanhol para quem está no México (testado com navegador `es-MX`). A
verba do México fica fora do plano de R$ 1.000 do Brasil, assim como a da Argentina.

**Alcance** (criada em 04/11 às 22h, a pedido do Itamar: "quero aparecer pra 100 mil empresas, pelo menos";
verba de R$ 700 aprovada por ele, fora do plano de R$ 1.000):

| Campanha | Conjunto | Anúncios | Verba | Período |
|---|---|---|---|---|
| `120255079974880007` MC \| Alcance 100 mil sellers \| Instagram (objetivo alcance, frequência máx. 2 a 3 em 7 dias) | `120255079984050007` BR, perfil seller (LAL clientes + LAL engajados + MercadoLivre, sem clientes atuais) | `120255079997560007` carrossel "sistema de IA" (post 04/11 `18576817813077656`) e `120255079997870007` Reel nota do anúncio | R$ 700 total (CBO) | 04/11 22h a 11/11 22h |
| (mesma) | `120255079985570007` Polos: Franca, Nova Serrana, Ibitinga, Gaspar e Apucarana (raio de 12 a 15 km) | `120255079998970007` carrossel e `120255079999490007` Reel | (CBO) | (mesmo) |

- Link dos anúncios: `l.tiops.com.br/comece?o=meta-alcance`, com botão "Saiba mais".
- Os polos saíram da base da Receita (`output/base-empresas/`): cidades onde um nicho de marketplace concentra de 46% a 60% das empresas.
- Meta: 100 mil pessoas, estimadas a R$ 5–7 por mil alcançadas.

**ManyChat** (04/11): duas automações respondem a **qualquer comentário** desses dois posts:

- `COMECE - Carrossel sistema de IA (anúncio alcance)`;
- `COMECE - Reel nota do anúncio (anúncio alcance)`.

Cada uma faz uma resposta pública, manda uma DM de boas-vindas com o botão "Quero o link" e depois o botão "Ver o vídeo", que leva a `l.tiops.com.br/comece?o=manychat-anuncio`.

Total do Brasil no ar: **R$ 650**. Faltam R$ 350:

- C, remarketing: R$ 200 a partir de 11/11;
- D, conversão por cadastro: R$ 150 a partir de 18/11.

**Configuração comum aos conjuntos:**

- otimização: visita à página de destino;
- cobrança por impressão;
- público: Brasil (mora ou esteve), idade mínima de 25 anos;
- sugestões para o Meta: 25–55 anos, interesse MercadoLivre E (donos de pequenas empresas OU
  administradores de página comercial);
- posicionamentos automáticos.

O **Público Advantage+ ficou ligado**: idade e interesses entram como sugestão, e o Meta pode ir
além deles. A Argentina usou público fechado. Se a qualidade das visitas cair, a primeira coisa a
testar é fechar o público.

**Por que o A2 vai só até 18/11:** o mínimo do Meta é cerca de R$ 5,49/dia. Com R$ 90, o teste
cabe em 14 dias. No dia 18, o vencedor fica com a verba.

**Criativos:** posts existentes do @tiopstecnologia (curtidas e comentários continuam), botão
"Saiba mais".

- A: `l.tiops.com.br/comece?o=meta-br`
- B: `marketplaces.tiops.com.br/avaliar-anuncio-meli-com-ia?o=meta-isca`

**Declaração de IA:** não marcada. O vídeo explicativo usa voz sintética; a declaração só é
obrigatória fora do Brasil.

## Leituras

**Rotina diária:** tarefa agendada `resumo-campanhas-mc-whatsapp` no Claude desktop, todo dia por
volta de 08h10. Ela lê o dia anterior pelo conector Meta ADS, o pixel (só navegador), o link
curto e a Stripe, manda o resumo no WhatsApp do Itamar e anota a leitura aqui. Só roda com o app
aberto.

### 03/11/2026 (lida em 04/11 às 12h20)

Plano BR entrou no ar às 23h20; o Meta não registrou gasto dele em 03/11. O acumulado abaixo vai até
a hora da leitura (inclui a manhã de 04/11).

| Anúncio | Gasto ontem | Acumulado | Visitas (acum.) | R$/visita (acum.) | Status |
|---|---|---|---|---|---|
| A1 Claude+ML+Shopee | R$ 0,00 | R$ 2,09 | 6 | R$ 0,35 | ativo |
| A2 Explicativo | R$ 0,00 | R$ 1,51 | 1 | R$ 1,51 | ativo |
| B Isca grátis | R$ 0,00 | R$ 0,98 | 3 | R$ 0,33 | ativo |
| AR Argentina | R$ 12,08 (29 visitas, R$ 0,42) | R$ 26,11 | 42 | R$ 0,62 | ativo |

- Plano R$ 1.000: R$ 4,58 gastos até a leitura.
- Pixel em 03/11, só navegador: CompleteRegistration 0, SubscribedButtonClick 0, ViewContent 9, Lead 1
  (InitiateCheckout 4). Purchase pelo servidor: 0.
- Link curto, pessoas em 03/11: /comece 5, /ar 48. Na janela de 2 dias, meta-br soma 39 cliques no
  /comece, quase todos em 04/11.
- Stripe: 11 assinaturas Plus criadas em 03/11 (1 já pediu cancelamento).
- ⚠️ Argentina passou de R$ 15 com R$ 0,62/visita no acumulado. Termina em 06/11, então não vale
  trocar o criativo.
- ⚠️ O pixel não registrou cadastro nem clique em Assinar, mas a Stripe teve 11 assinaturas.
  Conferir se esses eventos estão disparando.
