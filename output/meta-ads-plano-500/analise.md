# Meta Ads · análise e plano de R$ 500 para escalar assinantes

Conta: **Tiops tecnologia** (`1322329366662228`), BRL, fuso America/Sao_Paulo.
Levantado em 11/10/2026. Pixel `626514493772417` ("Ti Soluções de Tecnologia Event Data").

## 1. Por que nada está rodando

As 3 campanhas marcadas `ACTIVE` têm `delivery.status = off`:

- substatus das campanhas: `account_spend_limit_reached`
- erro no nível da conta: *"Your ads have been paused because your prepaid funds are empty."*

Gasto **de toda a história da conta**: R$ 53,92. Last delivery: 11–12/09.

São dois travamentos somados — saldo pré-pago zerado **e** limite de gastos da conta batido.
Colocar crédito sem levantar o limite não destrava.

## 2. O que as campanhas antigas ensinaram

| Campanha | Gasto | CTR | CPC | Resultado | Custo/result. |
|---|---|---|---|---|---|
| MC \| Sellers 300k \| Tráfego LPV | R$ 17,70 | 6,91% | R$ 0,14 | 95 LPV | **R$ 0,19** |
| MC \| Sellers \| Reels novos IG \| Tráfego LPV | R$ 17,69 | 1,25% | R$ 0,40 | 38 LPV | R$ 0,47 |
| MC \| Sellers \| Visitas ao perfil IG | R$ 8,54 | 8,40% | R$ 0,16 | 10 visitas perfil | R$ 0,85 |
| Curso Claude iniciantes — Udemy (pausada) | R$ 5,11 | 3,30% | R$ 0,18 | 28 cliques | R$ 0,18 |
| Post IG "Claude trabalhando 24h" (pausada) | R$ 4,88 | 6,48% | R$ 0,31 | 15 cliques | R$ 0,33 |

Média da conta: CTR 3,78%, CPC R$ 0,20, CPM R$ 7,63 em 7.063 impressões.

**O tráfego é barato.** R$ 0,19 por visita qualificada é bom para o nicho.
O problema não é custo de mídia.

**O problema é o objetivo.** Todas as 5 são `OUTCOME_TRAFFIC` / `LINK_CLICKS`.
Nenhuma otimiza por cadastro ou assinatura — o Meta nunca foi informado do que é um
assinante, então não tem como procurar quem assina. Tráfego não escala assinante.

## 3. O funil orgânico funciona (e é o que torna isso viável)

Eventos recebidos em 7 dias, via navegador **e** servidor (CAPI):

| Evento | Bruto (7d) | Real (ver nota) | Por dia |
|---|---|---|---|
| PageView | ~5.600 | ~2.800 | ~400 |
| ConectouCanal (custom) | 561 | ~280 | ~40 |
| CompleteRegistration | 149 | **~74** | ~10 |
| InitiateCheckout | 24 | ~12 | ~1,7 |
| ViewContent | ~90 | ~45 | ~6 |
| Lead | 10 | ~5 | <1 |

> **Nota — contagem dobrada.** Consultando só `WEB_ONLY`, o `CompleteRegistration` dá
> exatamente metade do total em **todos** os intervalos (ex.: 05/10 08h → total 14, web 7).
> Pixel e CAPI estão mandando o mesmo evento e a visão de estatísticas não deduplica.
> O relatório de anúncios deduplica **se** os dois lados mandarem o mesmo `event_id` —
> isso precisa ser conferido no código antes de confiar em qualquer CPA.

Taxa PageView → CompleteRegistration: ~74/2.800 = **2,6%** (público morno: conteúdo dele,
grupo de WhatsApp, base atual).

Queda a conferir: 10 e 11/10 com **zero** CompleteRegistration, contra ~10/dia na semana.

## 4. Infra de anúncio já pronta

Públicos ativos:

- `MC | Lista de clientes | set-26` (CUSTOM — lista de clientes)
- `LAL 1% | MC Lista de clientes` (lookalike dos clientes)
- `MC | Conectaram canal ou cadastraram | 180d` (site, 180 dias)
- `LAL 1% | MC Conectaram canal ou cadastraram` (lookalike de quem converteu)

Conversões personalizadas registradas: **nenhuma**. Então `ConectouCanal` — que é o sinal
mais forte que existe, "o cara plugou a loja de verdade" — **não pode ser escolhido como
otimização** enquanto não for registrado como conversão personalizada.

## 5. Qual peça impulsionar

Alcance orgânico das últimas peças: 46 a 148. Com n de 50 a 80, diferença entre 12% e 15%
de engajamento é ruído — **não dá para eleger vencedor por engajamento.** A retenção é a
única métrica com separação real.

| Peça | Dur. | Retenção média | Engaj./alcance | Salvos | Compart. |
|---|---|---|---|---|---|
| [Dd4thUwARvx](https://www.instagram.com/reel/Dd4thUwARvx/) — MC explicador | 42s | **14,7s = 35%** | **14,8%** | 0 | 3 |
| [Dd42HV5jyxg](https://www.instagram.com/reel/Dd42HV5jyxg/) — quanto sobra no ML | — | 12,9s | 13,5% | 1 | 2 |
| [DeSd9Thlii9](https://www.instagram.com/reel/DeSd9Thlii9/) — 2.232 ações | 28,8s | 9,3s = 32% | 5,9% | **3** | 1 |
| [DePQrtOD7Fe](https://www.instagram.com/reel/DePQrtOD7Fe/) — 13 anúncios | 38,2s | 10,5s = 27% | 9,6% | 2 | 0 |
| [DeRjlIllv7d](https://www.instagram.com/reel/DeRjlIllv7d/) — a IA se recusou | 53,9s | 10,7s = 20% | 12,2% | 2 | 1 |
| [DeAr4lptZmu](https://www.instagram.com/reel/DeAr4lptZmu/) — Imersão | — | 9,1s | 4,7% | 1 | 2 |

**Frio → `Dd4thUwARvx`.** Segura 35% de um vídeo de 42s e explica o que o produto é.
Público frio precisa entender o produto antes de assinar; os outros cortes pressupõem que
a pessoa já sabe o que é o Marketplace Connect.

**Retargeting → `DeSd9Thlii9`.** Mais salvamentos de todas (3) e foi feito para funil.
Quem já conhece responde a prova de operação, não a explicação.

### Travão antes de gastar

As duas legendas terminam em "Comenta CONNECT" / "link na bio".
Em anúncio pago com URL de destino esse CTA morre — e as palavras CONNECT e GESTOR
**não estão configuradas no ManyChat**, então comentário vira comentário sem resposta.
Precisa de texto próprio de anúncio, com "Saiba mais" apontando para o cadastro.

## 6. Plano dos R$ 500 (14 dias)

**Passo 0 — só o Itamar faz (pagamento):**
adicionar R$ 500 de crédito pré-pago **e** levantar o limite de gastos da conta.
Sem os dois, nada entrega.

**Passo 1:** registrar `ConectouCanal` como conversão personalizada.

**Passo 2:** conferir no código se pixel e CAPI mandam o mesmo `event_id`.
Sem isso, todo CPA reportado sai pela metade do valor real.

**Passo 3:** pausar as 3 campanhas de tráfego. Elas competem pelo mesmo público e
otimizam pela métrica errada.

**Passo 4:** campanha nova, `OUTCOME_SALES`, otimizando `CompleteRegistration`
(ainda não `ConectouCanal` — pouco volume para sair do aprendizado), janela 7d clique / 1d visualização.

| Conjunto | Público | Criativo | Verba |
|---|---|---|---|
| A — frio escalável | `LAL 1% | MC Conectaram canal ou cadastraram` | Dd4thUwARvx | R$ 25/dia × 10d = **R$ 250** |
| B — retargeting | `MC \| Conectaram canal ou cadastraram \| 180d`, excluindo a lista de clientes | DeSd9Thlii9 | R$ 10/dia × 10d = **R$ 100** |
| Reserva | — | o vencedor | **R$ 150** nos últimos 4 dias |

**Expectativa, com as contas na mesa:** a R$ 0,19/visita e 2,6% de conversão o cadastro
sairia a ~R$ 7,30. Mas esses 2,6% são de público morno; frio converte bem pior.
Orçar **R$ 8 a R$ 15 por cadastro** → os R$ 350 iniciais devem render **25 a 45 cadastros**.
Os primeiros R$ 150 são medição, não resultado: servem para descobrir o CPA real.

Nenhum conjunto vai sair do aprendizado (precisa de ~50 conversões/semana e R$ 25/dia não
chega lá). Com R$ 500 o objetivo honesto é **descobrir o CPA**, não escalar ainda.
Escalar é a decisão do mês seguinte, com o CPA na mão.

## 7. A alternativa que rende mais nos próximos 13 dias

A Imersão é 24/10 — 13 dias. Landing no ar, checkout Stripe funcionando,
R$ 2.500 presencial / R$ 1.000 online, e **inclui 1 mês de Marketplace Connect**.

Uma venda presencial devolve 5x os R$ 500. Um assinante devolve uma fração disso no
primeiro mês. Em retorno puro sobre os mesmos R$ 500, a Imersão ganha — e quem entra na
Imersão vira assinante do mesmo jeito, pelo mês incluso.

Contra: é prazo, não canal. Depois de 24/10 não escala; aquisição de assinante escala.

**Sugestão:** R$ 300 na Imersão até 23/10 (público `LAL 1% | MC Lista de clientes`,
criativo DeAr4lptZmu, otimizando `InitiateCheckout`) e R$ 200 no teste de CPA de assinante.
Decisão é do Itamar — ele pediu assinante, e o plano da seção 6 entrega assinante.
