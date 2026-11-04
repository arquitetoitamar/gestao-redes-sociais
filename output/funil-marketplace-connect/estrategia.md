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

Em ordem. Os itens 1, 2, 3 e 5 são da DEV-MC; o 4 é meu.

1. **Deploy do PR #503**, que volta a enviar o `CompleteRegistration` e grava a origem no perfil.
   Depois disso, eu testo o evento chegando no Meta.
2. **Compra pela CAPI no webhook da Stripe** (`checkout.session.completed` e
   `invoice.paid`), com `event_id` igual ao do navegador para deduplicar. Mandar valor e moeda.
3. **Levar a origem até a Stripe.** Nos botões do `/planos`, acrescentar
   `?client_reference_id=<origem>` (e `prefilled_email` quando o cliente já estiver logado).
   Com isso, cada venda fica atribuída ao canal.
4. **Página de obrigado.** Mudar o redirect dos 4 links de plano para
   `marketplaces.tiops.com.br/?checkout=sucesso&plano=plus` (já existe esse padrão em outro
   link). A página orienta o próximo passo, que é entrar com o mesmo e-mail e conectar a loja, e
   dispara a compra no navegador.
5. **ConectouCanal uma vez por loja**, para servir de conversão "loja conectada".

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

**Total: R$ 30/dia** (R$ 900/mês), igual ao ritmo do anúncio da Argentina. Nada sobe sem o seu
OK, e cobrança e saldo continuam com você.

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

## 4. Links rápidos (já funcionam, testados)

Todos levam à VSL e marcam a origem. Não precisa criar link novo: basta trocar o `?o=`.

| Onde | Link |
|---|---|
| Bio do Instagram | `l.tiops.com.br/comece?o=bio` |
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

(preenchido na próxima seção, a partir da pesquisa)

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
- **Pix no plano:** os links de assinatura aceitam só cartão. Vale avaliar com a DEV-MC.
- **Cliques de teste para descontar:** `o=teste-funil` (este teste), além dos de antes.
- **Regras:** CTA "Saiba mais", nunca "teste grátis"; nada é publicado sem o seu OK; checagem de
  5 perguntas antes de cada peça.
