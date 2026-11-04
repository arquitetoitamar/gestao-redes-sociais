# Funil do Marketplace Connect: estratégia de campanhas

Montado em 03/11/2026, 23h. Entrada do funil: **`l.tiops.com.br/comece`** (a VSL).
Conta de anúncios `1322329366662228`, pixel `626514493772417`. Público: Brasil.

## Resumo

O caminho até o pagamento funciona: link curto → VSL → planos → checkout da Stripe.
Testei deslogado, no tamanho de celular. O que não funciona é a **medição**:

- o Meta não recebe cadastro desde 09/10;
- o Meta nunca recebeu compra (0 em 28 dias);
- a origem do clique se perde no checkout.

Sem isso, dá para comprar visita barata, mas não dá para o Meta procurar quem assina.
A estratégia tem duas partes:

- **começar já** com tráfego para a VSL e remarketing;
- **trocar para campanha de conversão** quando cadastro e compra chegarem ao Meta.

## 1. Teste do funil (03/11, deslogado, celular 390 px)

| Etapa | URL | Resultado |
|---|---|---|
| Link curto | `l.tiops.com.br/comece?o=teste-funil` | ✅ 302 para `marketplaces.tiops.com.br/comece?o=teste-funil` |
| VSL | `/comece` | ✅ carrega em 0,9 s, vídeo no topo, pixel dispara PageView |
| Origem do clique | sessionStorage `tiops_funil_origem` | ✅ grava `teste-funil` e leva para os botões (`/planos?o=...`) |
| Planos | `/planos?o=...` | ✅ Plus R$ 149,90 e Pro Max R$ 297,00, botão "Assinar Plus mensal" |
| Clique em assinar | pixel | ✅ `SubscribedButtonClick` (evento automático do Meta) |
| Checkout | `buy.stripe.com/...ZC0b` | ✅ abre o checkout Plus mensal |
| Origem no checkout | link da Stripe | ❌ **não chega**: o botão abre o link sem `client_reference_id` |
| Depois de pagar | redirect da Stripe | ⚠️ volta para `marketplaces.tiops.com.br` (raiz): sem página de obrigado e sem evento de compra |
| Forma de pagamento | link da Stripe | ⚠️ só cartão (sem Pix) |
| Cadastro | home → "Conectar minha conta" | ✅ e-mail + código de 6 dígitos, e a origem continua gravada |
| Evento de cadastro | `CompleteRegistration` | ❌ **parado desde 09/10**. Correção no PR #503 da DEV-MC, ainda sem deploy |
| Origem no perfil | `customer_profiles.origem` | ❌ vazia em toda a base. A mesma correção (#503) resolve |
| Compra | `Purchase` | ❌ **nenhum evento em 28 dias**. Precisa sair do webhook da Stripe pela CAPI |
| Conexão de loja | `ConectouCanal` | ⚠️ 3.460 eventos em 28 dias: dispara a cada troca de token, não uma vez por loja |
| Isca grátis | `/avaliar-anuncio-meli-com-ia` | ✅ carrega, campo "Cole o link do seu anúncio", sem cadastro |

Eventos no pixel (últimos 28 dias, pelo conector Meta ADS):

- PageView: 35.146
- ConectouCanal: 3.460
- ViewContent: 528
- InitiateCheckout: 124
- CompleteRegistration: 71 (último em 09/10)
- Lead: 56
- Purchase: 0

## 2. Consertos antes de pôr dinheiro em conversão

Situação em 04/11, madrugada, segundo a DEV-MC
(registro em `docs/tech/2026-11-04-meta-purchase-e-conectou-canal.md`):

| # | Conserto | Situação | Depende de |
|---|---|---|---|
| 0 | **Token da API de Conversões (CAPI)** nas Lambdas `meta-capi` e `stripe-webhook` (SSM `/tiops/meta/META_CAPI_TOKEN`) | ✅ ligado em 03/11 ~23h30; evento de teste `TesteCapi` aceito (events_received 1). A fonte SERVER que já existia é a **API de Conversões hospedada pela Meta** ("Somente web", ativada em 29/09). Ela copia o pixel com o mesmo eventID e desduplica sozinha. **Na leitura do dataset, contar só BROWSER**: o total bruto soma as duas vias | DEV-MC |
| 1 | `CompleteRegistration` volta, e a origem é gravada no perfil | ✅ PR #503 mergeado, deploy em andamento. Sai também pelo navegador, então não depende do token | eu testar quando a DEV-MC avisar |
| 2 | Compra (`Purchase`) pelo webhook da Stripe na 1ª fatura paga (`event_id = stripe_inv_<fatura>`). O checkout grava ua, ip, _fbp e _fbc | ✅ #504 no ar e token ligado: a próxima assinatura paga deve aparecer no Meta | — |
| 3 | `ConectouCanal` uma vez por conta e canal (`event_id = conectou_<uid>_<canal>`) | ✅ #504 no ar | — |
| 4 | Origem do clique até a venda | ✅ Itamar aprovou a opção A. PR #505 mergeado: sem login, "Assinar" na `/planos` leva ao login (`/?login=1`) e depois aos Planos do painel (Checkout Session com conta, origem, indicador e navegador). Build do Amplify rodando em 03/11, 23h30 | eu refazer o teste do `/comece` quando subir |
| 5 | Página de obrigado com compra no navegador (mesmo `event_id`) | depois da decisão do item 4 | — |

**Item 4: por que não `client_reference_id`.** O webhook lê esse campo como id da conta, e é ele
que ativa o plano de quem paga com outro e-mail. Pôr a origem ali quebraria a ativação. Opções:

- **A: exigir cadastro (e-mail + código) antes do checkout.** O pagamento passa a sair pela
  Checkout Session, que já leva a origem e os dados do navegador.
- **B: manter o checkout sem login** e levar a origem por outro campo do Payment Link.

**Minha recomendação para o tráfego pago: A.**

- O cadastro custa um passo curto (e-mail e código, sem senha).
- Em troca, o Meta passa a ter um evento de cadastro para otimizar enquanto há poucas vendas.
- A venda fica presa à conta, e a origem chega inteira.
- Quem desiste entre o cadastro e o pagamento vira público de remarketing com e-mail.

**Pix:** assinatura na Stripe exige mandato; hoje só o pagamento avulso aceita Pix. Fica como está.

**Como gerar o token (item 0):**

1. No Gerenciador de Eventos, abra o conjunto de dados `626514493772417`.
2. Vá em Configurações → API de Conversões → "Gerar token de acesso".
3. Grave o token direto onde a DEV-MC indicar, no Secrets Manager ou na variável `META_CAPI_TOKEN`
   da Lambda. Não cole o token no chat.

Até lá, a conversão provisória para remarketing é o `SubscribedButtonClick` no `/planos`.
Ele já dispara no clique em "Assinar".

## 3. O funil

```
TOPO      Reels orgânicos (16–20h) + anúncio de vídeo + isca "Avaliar meu anúncio grátis"
            ↓  link curto com ?o=<canal>
MEIO      /comece (VSL): o que faz, o que não faz, 3 passos, depoimento, suporte
            ↓  remarketing para quem viu vídeo, visitou /comece ou avaliou anúncio
FUNDO     /planos → checkout Stripe  ·  alternativa: sessão de implantação (R$ 500)
            ↓
ATIVAÇÃO  entrar com o e-mail → conectar loja → conectar IA → 1º agente (chamado)
            ↓
INDICAÇÃO "Indique e ganhe" no painel
```

### Campanhas no Meta

| # | Campanha | Objetivo | Público | Criativo | Destino | Verba/dia |
|---|---|---|---|---|---|---|
| A | **Topo: VSL** | Tráfego, otimizando visita à página | Brasil, 25–55, interesse Mercado Livre E (admin. de página comercial OU dono de pequena empresa) | Reel explicativo PT, corte de 30 s da VSL | `l.tiops.com.br/comece?o=meta-br` | R$ 15 |
| B | **Topo: isca grátis** | Tráfego, otimizando visita à página | mesmo da A | "Seu anúncio tira quanto de 100?" + tela da nota | `.../avaliar-anuncio-meli-com-ia?o=meta-isca` | R$ 5 |
| C | **Meio: remarketing** | Tráfego, otimizando visita à página | viu 50% de vídeo (IG, 90 d) + engajou no IG (90 d) + visitou `/comece` ou a isca (30 d), excluindo quem pagou | demo "criando anúncio no ChatGPT", depoimento do Danilo, segurança (autorização oficial, nunca vemos a senha) | `/comece?o=meta-rmk` | R$ 10 |
| D | **Fundo: conversão** (depois dos consertos) | Vendas, otimizando compra (ou cadastro enquanto houver menos de 50 por semana) | visitou `/planos` e não comprou (14 d) + C | "2 meses grátis no anual", "sessão de implantação com o Itamar" | `/planos?o=meta-fundo` | R$ 10 (sai da A) |

A verba de cada campanha e o criativo usado estão em **"Orçamento de R$ 1.000"**, logo abaixo.
Nada sobe sem o seu OK, e cobrança e saldo continuam com você.

Referência de custo na conta: visita à página custou R$ 0,19 (MC Sellers 300k), R$ 0,20 (Reel
do Claude) e R$ 0,38 (Argentina). Com R$ 20/dia de topo, a expectativa é de 50 a 100 visitas por
dia na VSL.

### Orgânico (sustenta o topo de graça)

- **Reels de terça a quinta, entre 16h e 20h**, espaçados de 24 a 48 h (uma peça canibaliza a
  outra).
- Ganchos que já funcionaram: ferramenta grátis útil (viraliza) e demo na tela.
- **CTA de comentário: CONNECT** (o ManyChat já manda a DM com o link). Para a isca, a palavra
  seria **AVALIAR**, porque NOTA já é do Emissor NF-e. Precisa de automação nova, com o seu OK.
- **Números só de `sistema.json`**: 9 marketplaces, 2.484 contas conectadas, 1.116 ferramentas
  (medido em 22/10). Nada de faturamento, margem, custo de IA ou dado de cliente.
- **Objeções que apareceram nos comentários** (LGPD, certificado digital, "ilegalidade") viram
  pauta de Reel explicativo, sem citar quem comentou e sem responder no post.

### O que já converteu (só Marketplace Connect)

Anúncios da conta, histórico completo (conector Meta ADS, 04/11):

| Conteúdo | Gasto | CTR | Custo por visita | Veredito |
|---|---|---|---|---|
| **Vídeo "Claude + Mercado Livre + Shopee"** (post IG `18097413965173557`, 10/09), em 3 anúncios | R$ 25,27 | **6,6% a 9,7%** | **R$ 0,19 a R$ 0,26** | **vencedor**: vira o anúncio principal |
| Reel explica MC em espanhol (Argentina) | R$ 9,42 | 2,0% | R$ 0,39 | médio. A versão em PT entra como teste |
| Reel "Qual IA usar no meu e-commerce" | R$ 17,69 | 1,25% | R$ 0,47 | corta (além disso, promete "5 minutos") |
| Post estático "Claude trabalhando 24h" | R$ 4,88 | 6,5% | R$ 0,70 | corta: imagem não leva à página |

Orgânico (análise de 27/10, `output/instagram-insights/`):

| Conteúdo | Alcance | Compartilhamentos | Salvamentos |
|---|---|---|---|
| **Reel "Seu anúncio no Mercado Livre tem nota"** (14/08, `18020078531879388`) | **25.710** | **760** | **694** |
| Reel "Conecte o ChatGPT no seu marketplace" (18/08) | 384 | 7 | 2 |

O 2º melhor post da conta teve 1.606 de alcance. A fórmula do viral foi:

- gancho sobre algo do próprio seller;
- lista do que a ferramenta mostra;
- grátis.

**Origem dos cliques no `/comece` (60 dias):** 50 de 78 vieram do YouTube (vídeo do conector), 1
do Instagram. O YouTube orgânico é hoje o canal que mais leva gente à VSL.

### Orçamento de R$ 1.000 em 30 dias (só Marketplace Connect)

Cada campanha leva o conteúdo que já provou resultado. Os posts existentes rodam como "usar
publicação existente", para manter curtidas e comentários.

| Campanha | Criativo | Destino | Dias | Por dia | Total |
|---|---|---|---|---|---|
| A: topo, VSL | **80%** "Claude + ML + Shopee" e **20%** Reel explicativo PT (teste) | `/comece?o=meta-br` | 1 a 30 | R$ 15 | **R$ 450** |
| B: isca grátis | Reel viral "Seu anúncio no ML tem nota" | `/avaliar-anuncio-meli-com-ia?o=meta-isca` | 1 a 30 | R$ 6,70 | **R$ 200** |
| C: remarketing | demo criando anúncio no ChatGPT/Claude, segurança (autorização oficial) e depoimento do Danilo, se ele autorizar | `/comece?o=meta-rmk` | 8 a 30 | R$ 8,70 | **R$ 200** |
| D: conversão (otimizando cadastro) | o melhor de A e C até ali | `/comece?o=meta-conv` | 15 a 30 | R$ 9,40 | **R$ 150** |
| **Total** | | | | R$ 22 → 30 → 40 | **R$ 1.000** |

Ficam de fora: o Reel da NF-e (é outro produto), "Qual IA usar", posts estáticos e o curso da Udemy.

**Alcance esperado com R$ 1.000**, usando o CPM da conta (R$ 6,50 a R$ 7,60):

- 130 a 155 mil impressões;
- cerca de **70 a 90 mil contas** alcançadas, a maior parte no topo (A e B). O remarketing
  repete as mesmas pessoas;
- visitas: A, com o criativo vencedor a R$ 0,19 a R$ 0,30 cada, dá 1.500 a 2.350 visitas à VSL;
  B dá 500 a 1.000 avaliações; C dá 330 a 500 retornos.

Regra durante o mês: depois de R$ 15 gastos num criativo, se a visita passar de R$ 0,45, ele
sai e a verba vai para o vencedor.

A campanha D otimiza **cadastro**, não compra. Com R$ 1.000/mês não sai a média de 50 compras
por semana de que o Meta precisa para aprender a achar comprador. Cadastro dá volume.

Projeção. **As taxas de conversão são hipóteses**: a conta nunca mediu uma venda vinda de anúncio.

| | Pessimista | Médio | Bom |
|---|---|---|---|
| Custo por visita (história da conta: R$ 0,19 a R$ 0,47) | R$ 0,45 | R$ 0,30 | R$ 0,20 |
| Visitas à VSL (campanha A) | 1.000 | 1.500 | 2.250 |
| Visitas à isca (campanha B) | 330 | 500 | 750 |
| Clicam em "Assinar" (5% a 8% da VSL) | 50 | 100 | 180 |
| Assinaturas (0,3% a 0,7% das visitas à VSL) | 3 | 8 | 15 |
| Custo por assinante | R$ 330 | R$ 125 | R$ 67 |

No cenário médio, o custo de cada assinante (R$ 125) se paga no 1º mês do Plus (R$ 149,90).

**Pontos de parada:**

- **Por volta de R$ 150 (dia 7):**
  - se a visita custar mais de R$ 0,45, troco o criativo;
  - se menos de 5% da VSL clicar em "Assinar", o problema é a página. Pauso o topo e ajusto a
    VSL antes de gastar mais.
- **Por volta de R$ 500 (dia 18):**
  - se não houver nenhuma assinatura e menos de 15 cadastros com origem Meta, paro e reviso a
    oferta (por exemplo, sessão de implantação ou anual com 2 meses grátis em destaque).

**Antes de colocar os R$ 1.000:**

1. Crédito na conta pré-paga. A cobrança é sua, com confirmação de identidade.
2. Token da CAPI gerado e o #503 no ar, para medir cadastro e venda por origem.

Sem os dois, faz sentido começar só com R$ 300 de topo (A + B), que não dependem de medir
cadastro, e liberar o resto depois.

## 4. Links rápidos (já funcionam, testados)

Todos levam à VSL e marcam a origem. Não precisa criar link novo: basta trocar o `?o=`.

| Onde | Link |
|---|---|
| Bio do Instagram | `l.tiops.com.br/comece?o=bio` |
| Destaque "Comece" | `l.tiops.com.br/comece?o=destaque` |
| Stories (figurinha de link) | `l.tiops.com.br/comece?o=stories` |
| DM do ManyChat (CONNECT) | `l.tiops.com.br/comece?o=manychat` |
| Descrição do YouTube | `l.tiops.com.br/comece?o=youtube` |
| Grupo de WhatsApp | `l.tiops.com.br/comece?o=whatsapp` |
| Anúncio Meta (topo) | `l.tiops.com.br/comece?o=meta-br` |
| Anúncio Meta (remarketing) | `l.tiops.com.br/comece?o=meta-rmk` |
| Isca grátis | `marketplaces.tiops.com.br/avaliar-anuncio-meli-com-ia?o=<canal>` |
| Direto para os planos (quem já viu a VSL) | `marketplaces.tiops.com.br/planos?o=<canal>` |

Os cliques aparecem por origem em `link_cliques comece`. Cadastros e vendas por origem só depois
dos consertos 1 e 3.

## 5. Instagram: links e botão do site no perfil

Pesquisa de 03/11/2026, com as fontes oficiais listadas no fim.

**Não existe botão grátis de "Site" para SaaS.** Os perfis com botão abaixo da bio usam um destes:

- **botão de ação de parceiro**: Reservar agora, Reservar ou Pedir refeição;
- **"Ver loja"**: só para produto físico. A política da Meta proíbe vender assinatura e produto
  digital na loja, então o Marketplace Connect não é elegível;
- **Meta One**: recursos pagos, a página de links por R$ 59/mês e o "perfil aprimorado" por
  R$ 199/mês.

O que fazer no @tiopstecnologia, em ordem (os passos no app são seus):

1. **Link principal no perfil** (grátis, 2 minutos):
   - Editar perfil → Links → Adicionar link externo → `l.tiops.com.br/comece?o=bio`, com o
     título "Marketplace Connect – Saiba mais";
   - depois, em Links → ⋯ → **Reordenar links**, deixe esse link em 1º. Só o primeiro aparece
     direto no perfil;
   - termine a bio apontando para ele, por exemplo "👇 Conecte sua loja do ML e da Shopee à IA".
2. **Destaque "Comece"**, o mais perto de uma "aba do site" que existe de graça:
   - publique um story com a figurinha **Link** para `l.tiops.com.br/comece?o=destaque`, com o
     texto "Saiba mais";
   - salve num destaque "Comece", com capa da marca, e deixe-o em 1º lugar.
3. **Reel fixado**: o Reel explicativo do Marketplace Connect, terminando com "comente CONNECT".
   Para fixar, abra o post → ⋯ → Fixar no perfil (cabem até 3 fixados).
4. **Contato visível**: Editar perfil → Informações comerciais públicas → e-mail e WhatsApp.
5. **Não agora**:
   - botão de ação: o rótulo é "Reservar agora", só funciona com parceiros como Acuity ou
     Setmore, e o Calendly não está na lista;
   - Meta One: é pago e, com cerca de 675 seguidores, o ganho não justifica.

Fontes:

- help.instagram.com:
  - [links no perfil](https://help.instagram.com/iphone-app/362497417173378);
  - [botões de ação](https://help.instagram.com/122793804938499);
  - [parceiros](https://help.instagram.com/313280685976255).
- [Políticas Comerciais da Meta](https://www.facebook.com/policies_center/commerce).
- [Planos do Meta One](https://www.meta.com/pt-br/help/subscriptions/960854640235758/), atualizado
  no fim de outubro de 2026.

Não deu para confirmar o "formulário de cadastro" como botão de ação no Brasil (a liberação é
gradual).

## 6. Como medir (toda semana)

| Etapa | Métrica | Onde | Meta inicial |
|---|---|---|---|
| Topo | custo por visita à página | Meta | ≤ R$ 0,40 |
| VSL | % que clica em "Assinar agora" | `SubscribedButtonClick` ÷ visitas `/comece` | ≥ 8% |
| Planos | % que abre o checkout | Stripe (sessões) ÷ cliques | medir |
| Cadastro | cadastros com origem | `customer_profiles.origem` (após #503) | medir |
| Venda | assinaturas por origem | Stripe `client_reference_id` (após conserto 3) | medir |
| Ativação | loja conectada em 24 h | ConectouCanal (1 por loja) | medir |

Decisão em 7 dias com a verba de topo:

- se a VSL não levar ao menos 5% para `/planos`, o problema é a página, não a mídia;
- se levar e ninguém assinar, o problema é o checkout ou a oferta.

## 7. Calendário

| Quando | O quê | Quem |
|---|---|---|
| 04/11 | Links do perfil do IG + destaque "Comece aqui" | você (no app) |
| 04–05/11 | Deploy do #503; teste do cadastro chegando no Meta | DEV-MC + eu |
| 05/11 | Campanhas A e B no ar (R$ 20/dia) | eu, com o seu OK |
| 06/11 | Fim do anúncio da Argentina; leitura final | eu |
| até 07/11 | Compra pela CAPI + `client_reference_id` + página de obrigado | DEV-MC + eu |
| 10/11 | Remarketing C (públicos já com 7 dias de dados) | eu, com o seu OK |
| 17/11 | Se a compra e o cadastro estiverem chegando, a D substitui parte da A | eu, com o seu OK |

## 8. Pendências e cuidados

- **Depoimento do Danilo em anúncio:** confirmar com ele o uso pago. Está na página, mas
  anúncio é outro uso.
- **Cliques de teste para descontar:** `o=teste-funil` (este teste), além dos de antes.
- **Regras:** CTA "Saiba mais", nunca "teste grátis"; nada é publicado sem o seu OK; checagem de
  5 perguntas antes de cada peça.
