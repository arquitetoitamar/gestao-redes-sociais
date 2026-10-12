# Campanha criada e ativada — 11/10/2026

Conta **Tiops tecnologia** `1322329366662228`. Tudo `ACTIVE`.
**Ainda não entrega**: `delivery.status = off`, substatus `account_spend_limit_reached`.
Falta o passo que só o Itamar faz (seção "Antes de entregar").

## Estrutura

**Campanha** `120254709850060007` — "MC | Assinantes | Cadastro | out-26"
Objetivo `OUTCOME_SALES`, leilão, sem categoria especial. Orçamento por conjunto (ABO),
porque os dois conjuntos recebem verbas diferentes de propósito.

| Conjunto | ID | Verba/dia | Público | Criativo |
|---|---|---|---|---|
| A — frio | `120254709851550007` | R$ 25 | `LAL 1% \| MC Conectaram canal ou cadastraram`, Brasil, 25–55 como sinal | MC explicador 42s |
| B — retargeting | `120254709852420007` | R$ 10 | `MC \| Conectaram canal ou cadastraram \| 180d`, **excluindo** `MC \| Lista de clientes \| set-26` | 13 anúncios em um pedido 38s |

Os dois: otimização `OFFSITE_CONVERSIONS` em `CompleteRegistration` do pixel
`626514493772417`, destino site, lance automático, atribuição 7d clique / 1d visualização,
posicionamentos Advantage+, término **21/10/2026 23:59**.

Teto natural: R$ 25 × 10 dias = R$ 250 em A, R$ 10 × 10 dias = R$ 100 em B.
**R$ 150 ficam de reserva** para jogar no vencedor nos últimos dias.

**Anúncios:** A `120254709855950007` (criativo `1784084369468901`),
B `120254709856320007` (criativo `1422505299226539`).
Ambos com CTA **"Saiba mais"** para `https://marketplaces.tiops.com.br`,
`conversion_domain = marketplaces.tiops.com.br`, identidade IG `@tiopstecnologia`.
Prévia conferida no Instagram Reels: renderiza certo.

## Campanhas antigas pausadas

`120254257708650007` (Reels novos IG), `120254257704190007` (Visitas ao perfil IG),
`120254244769390007` (Sellers 300k). Eram todas de tráfego e disputavam o mesmo público.

## Uma mudança em relação ao plano

O plano previa o Reel "2.232 ações" (GestorPro) no conjunto B. **Trocado** pelo
"13 anúncios em um pedido".

Motivo: em 7 dias de eventos do pixel, os domínios que disparam são
`marketplaces.tiops.com.br`, `tiops.com.br`, `agentes.tiops.com.br` e ambientes de
teste. **`gestorpro.tiops.com.br` não aparece nenhuma vez.** Sem evento, o Meta não tem
sinal nenhum de GestorPro e não consegue otimizar por cadastro ali. Mandar um criativo de
GestorPro para um destino sem pixel queimaria a verba às cegas.

Os dois conjuntos apontam para o Marketplace Connect, que é onde a conversão existe.

## Antes de entregar — só o Itamar faz

1. **Adicionar crédito pré-pago** (R$ 500) na conta de anúncios.
2. **Levantar o limite de gastos da conta** — é um ajuste separado do saldo; o gasto da
   conta inteira hoje é R$ 53,92 e o limite já foi batido. Sem levantar, o crédito entra
   e mesmo assim nada roda.

Feito isso, os dois conjuntos começam a entregar sozinhos.

## Declaração de IA — resolvida em 12/10

O Itamar pediu para declarar. O criativo do conjunto A foi **refeito** com
`self_ai_disclosure = OPT_IN`, porque a narração do Reel "MC explicador" foi gerada com
**Gemini TTS** — áudio de ferramenta generativa de terceiros. O campo é imutável depois de
criado, por isso exigiu criativo e anúncio novos em vez de edição.

- Criativo novo: `1869574060697836` ("A2 | MC explicador 42s | Saiba mais | declara IA")
- Anúncio novo: `120254710431920007` ("A | MC explicador 42s | declara IA"), ativado
- Anúncio antigo `120254709855950007` (criativo `1784084369468901`, sem declaração): pausado

Mídia, texto, título, CTA, destino e identidade seguem idênticos — só a declaração mudou.

O conjunto B segue sem declaração: o áudio é locução do próprio Itamar, gravada.

A declaração só produz efeito onde há regra de transparência de IA (Região Europeia,
Índia, Taiwan, Califórnia e Nova York). O alvo destes conjuntos é Brasil, então na prática
a Meta pode nem exibir o selo "Informações de IA" — a declaração fica correta de qualquer forma.

## Pendências técnicas levantadas no caminho

- **Eventos contados em dobro**: pixel e CAPI mandam o mesmo evento. Conferir `event_id`
  nos dois lados antes de confiar em qualquer CPA reportado.
- **Ambientes de teste no pixel de produção**: `localhost`, `hml-marketplaces.tiops.com.br`
  e `homolog.d2bql391upvzuj.amplifyapp.com` disparam o mesmo dataset. Isso suja o público
  de retargeting e as estatísticas. Vale separar por dataset ou bloquear fora de produção.
- **`ConectouCanal` ainda não é conversão personalizada**, então não dá para otimizar por
  ele — é o sinal mais forte que existe e precisa ser registrado no Gerenciador de Eventos.
- **ManyChat**: CONNECT e GESTOR continuam sem configuração.
