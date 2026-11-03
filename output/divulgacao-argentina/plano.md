# Plano de divulgação na Argentina e no México: Instagram, YouTube e Meta Ads

**Data:** 03/11/2026 · Pedido do Itamar, também encaminhado pela sessão DEV-MC.
Base: `meli-oauth-buddy/docs/tech/2026-11-03-plano-expansao-america-do-sul.md` e
`docs/sistema.json`. É plano: nada foi publicado, criado ou pago.

## Onde estamos

- O Mercado Libre Argentina (MLA) está no ar com o mesmo app. O primeiro cliente
  argentino pagou o Plus em 03/11. **Não temos autorização dele para conteúdo.**
- A landing está em espanhol: o navegador `es-*` abre em espanhol sozinho. Isso
  ainda é tradução por IA, sem revisão humana.
- **Ainda em português:** cadastro, planos, login, autorização e painel.
- **Loja para gravar:** o usuário de teste MLA `3804950010`
  (`TESTUSER2455806134963366364`) já está conectado na sua chave. Tem 1
  publicação pausada ("Taza de cerámica"), sem vendas e sem reputação.
- **Calendário:**
  - CyberMonday AR: de 2 a 4/11, ou seja, agora. Não dá tempo de entrar.
  - Black Friday: 27/11. É o próximo gancho.
  - Depois vêm as vendas de fim de ano.
- **O que sabemos do @tiopstecnologia** (análise de 27/10):
  - O público é brasileiro: 35–44 anos, 71% homens, SP na frente.
  - 85% do alcance de 30 dias veio de anúncio.
  - Reels das 16h às 20h é o que funciona.
  - O que escala é ferramenta grátis, útil e salvável.

## Concorrente direto: @ignaciooleo (Ignacio Leo, marca TRAID)

O Itamar indicou como o único serviço parecido na Argentina. Visto em 03/11 no
Instagram (você já segue o perfil):

- **Perfil:**
  - verificado, 4.154 seguidores, 8 posts;
  - bio: "Ayudo a sellers Platinum en Mercado Libre a automatizar toda su
    cuenta · Consultor y desarrollador certificado";
  - link `traidai.com/optin-recursos-page`;
  - destaques "CLIENTES 1–6".
- **Reel de 29/07** ("Claude + Mercado Libre: Publique +10K productos en un
  DIA!"):
  - 1.602 curtidas, 2.019 comentários, 38 compartilhamentos;
  - legenda só com "Comenta VIDEO y te mando el video para configurar todo";
  - rosto na câmera e logos do Claude e do Mercado Libre no topo.
- **Outros posts:**
  - "Claude se conecta con Mercado Libre";
  - "Cómo conectar Claude a Mercado Libre";
  - "+230 agentes de IA GRATIS para Mercado Libre";
  - "Armé mi propio equipo de IA para Mercado Libre";
  - um sobre as skills de Claude da equipe do Galperin.

### O que isso ensina

1. **A demanda existe.** Argentino já procura "Claude + Mercado Libre". Não é
   preciso explicar a ideia, só mostrar que funciona.
2. **Isca de comentário com tutorial na DM é o motor.** Uma conta de 4 mil
   seguidores tirou 2 mil comentários com "Comenta VIDEO".
   - No BR, "Comenta X" não mudou alcance. Lá, o comentário é o lead.
   - Por isso o ManyChat em espanhol passa a ser **prioridade**, não opcional.
3. **Recurso grátis** ("+230 agentes gratis") também puxa, como a extensão do
   Chrome aqui.
4. **Ele vende consultoria para Platinum.** Nós vendemos produto que o próprio
   vendedor conecta.

### Posicionamento contra ele (sem citar o nome)

- "Sin consultor: conectalo vos mismo, con una autorización."
- "Para cualquier vendedor, no solo Platinum."
- "Con Claude y con ChatGPT."
- **Não copiar números dele** ("+10K productos en un día"): não são medidos
  por nós.
- **Palavra-chave diferente da dele:** CONECTAR, não VIDEO.

### Também é possível parceiro

Consultor certificado que atende Platinum pode usar o Marketplace Connect como
infraestrutura. Ele pode recusar, porque tem produto próprio (TRAID), mas uma
DM sua de fundador para fundador custa pouco. Só com o seu OK.

## México (liberado no código em 03/11)

**Situação:**

- `_shared/meli-paises.ts` já tem `MLM: "MX"`: mesmo app, login no domínio do
  país.
- O México é o maior Mercado Libre depois do Brasil.
- Com AR e MX, o plano vale para os dois e ganha estas mudanças.

### Idioma: base em espanhol neutro com "tú"

- Mexicano não fala "vos". "Conectá" soa argentino para ele.
- A base passa a ser espanhol neutro com "tú", que serve ao México e à onda 1
  (Chile, Colômbia, Peru).
- O "vos" fica só nas versões da Argentina: anúncio AR e narração e legenda AR.
- **Gravação de tela:** uma vez só, com o pedido à IA em espanhol neutro ("lista
  mis publicaciones sin stock").
- **Narração e texto na tela:** duas versões, `-ar` (vos) e `-mx` (tú). A
  narração por TTS custa centavos.
- **Vocabulário MX:** "meses sin intereses" (AR: "cuotas sin interés"), Buen
  Fin, "Mercado Envíos Full".

### Datas do México

| Data | Evento | Peça |
|---|---|---|
| 13 a 17/11 (sex a ter; 16/11 é feriado) | **Buen Fin** | **R4-MX "Buen Fin: revisa tu tienda antes"**, publicar até qua 11/11 |
| 27/11 | Black Friday | R4 e L3 servem aos dois países |

**Horário:** Cidade do México é UTC-6, então 18h lá = 21h em Brasília. O
orgânico para o México sai das 18h às 20h no horário deles. O anúncio a Meta
entrega no fuso de quem vê.

### Concorrência no México (busca em 03/11)

- Só servidores MCP técnicos:
  - comunitário (lumile/mercadolibre-mcp, instala por `npx` e pede `SITE_ID`);
  - AnythingMCP (cola credenciais);
  - Vinkius (só pedidos).
- Nenhum é pensado para o vendedor comum.
- **Mensagem:** "Sin instalar nada y sin credenciales de desarrollador: una
  autorización y tu IA ya opera tu tienda."
- **Não dizer** que somos "el único" ou "el oficial".

### Canal

- Com o México, o perfil próprio em espanhol (`@tiops.latam`, com "tú") fica
  mais justificado, porque a audiência potencial dobra.
- Mesmas condições da etapa 2 (seção 1).
- O YouTube continua no mesmo canal, com os vídeos longos em espanhol neutro:
  a busca serve aos dois países.

### Outros canais no México

- Amazon MX, TikTok Shop MX e Shein MX existem.
- **Não prometer** antes de testar conta mexicana em cada um. O plano de
  expansão marca "médio" nos outros canais.
- No conteúdo do México, só Mercado Libre por enquanto.

### Pendências para o México

| Item | Quem |
|---|---|
| Página em espanhol para o México (`/es/mercado-libre-mexico-ia.html`, "tú", hreflang es-MX ↔ es-AR ↔ pt-BR): **no ar desde 03/11**: 200 sem redirecionar, "tú" conferido no texto (conecta, puedes), hreflang es-MX/es-AR/pt-BR | DEV-MC |
| Espanhol do site: **decidido em 03/11 que o padrão é neutro com "tú"** para os 19 países (conversão do `es.ts` em andamento). Só a página da Argentina mantém "vos" | DEV-MC |
| Usuário de teste MLM conectado + publicações em MXN para as demos: **criado `3813915584` em 03/11**; falta autorizar e criar as publicações | DEV-MC |
| Login `auth.mercadolibre.com.mx`, card Brasil/Argentina/México, tag `mexico` no CRM (PR #496, a caminho do ar) | DEV-MC |
| Slug `mx` → `/es/mercado-libre-mexico-ia.html` (página já no ar) | esta sessão, com OK |
| Moeda e cobrança: o primeiro cartão mexicano no Stripe em BRL ainda não foi testado | Itamar |

## 1. Canal: mesma conta ou perfil próprio em espanhol?

### Instagram

| | Usar o @tiopstecnologia | Criar perfil em espanhol (ex. `@tiops.latam`) |
|---|---|---|
| Prós | Já tem histórico, verificação, ManyChat e Gerenciador de Anúncios ligados. Anúncio roda com essa identidade sem custo extra. | Público limpo, tudo em espanhol: bio, destaques e DM. Quem chega pelo anúncio vê um perfil "para mim". |
| Contras | Seguidores BR recebem Reel em espanhol: engajamento cai e o algoritmo distribui pior os dois idiomas. Perfil em português afasta o argentino que clica. | Começa do zero (perfil vazio também afasta). Exige um segundo ManyChat (R$ 149/mês depois do teste) e ritmo próprio de postagem. |

**Recomendação: fase em duas etapas.**

1. **Agora, sem perfil novo.**
   - Na Argentina, o canal principal é o anúncio pago. Orgânico de perfil
     brasileiro não chega lá, e o histórico da conta confirma isso.
   - O anúncio roda com a identidade do @tiopstecnologia.
   - Na bio, um link extra "🇦🇷 Español" (o Instagram aceita até 5 links).
   - Reels em espanhol entram como **Reel de teste**, se a opção aparecer no app:
     vai só para não seguidores e não suja o feed dos brasileiros.
2. **Criar o perfil em espanhol quando estas três coisas estiverem prontas:**
   - cadastro e autorização em espanhol;
   - alguém respondendo DM e chamado em espanhol;
   - 8 a 10 peças em espanhol prontas e ritmo de 3 por semana.

   Sugestão de nome: `@tiops.latam`, que serve também para a onda 1 (Chile,
   Colômbia, Uruguai, Peru). Para esses países, a legenda troca "vos" por "tú".

### YouTube

**Recomendação: mesmo canal (@tiopstecnologia).**

- O YouTube distribui por idioma e por busca, não pelo país do canal.
- **Não é preciso mudar a região do canal.** "País de residência" (Studio →
  Configurações → Canal) é para monetização e impostos. Deixe Brasil.
- O que faz o vídeo aparecer na Argentina:
  - **Idioma do vídeo:** "Español (Latinoamérica)", ou seja,
    `defaultAudioLanguage` e `defaultLanguage` = `es-419`.
  - **Título, descrição e legenda em espanhol**, escritos para a busca
    argentina: "cómo conectar Mercado Libre con ChatGPT", "Claude Mercado
    Libre", "MCP Mercado Libre".
  - **Áudio em espanhol.** O vídeo em português legendado rende pouco.
  - **Playlist "En español: Mercado Libre con IA".**
  - **Nome e descrição do canal traduzidos para espanhol** (Studio → Idiomas).
- Conferir em Analytics → Público → Geografia, filtrando Argentina, 7 dias
  depois de cada vídeo.
- Canal separado só se o espanhol virar metade da produção.

## 2. Pilares de conteúdo

**Regra de idioma (decisão de 03/11):** espanhol neutro com "tú" no México e
no conteúdo geral (YouTube, perfil em espanhol). "Vos" só no conteúdo
exclusivo da Argentina (anúncio AR, versão `-ar`). Os exemplos abaixo estão em
"vos" porque nasceram para a Argentina; a versão `-mx` troca para "tú".

| Pilar | Mensagem | Por quê |
|---|---|---|
| **Tu IA opera tu tienda** | "Pedile a Claude o ChatGPT y lo hace dentro de tu Mercado Libre" | É a diferença central do `sistema.json`: o agente executa, não só mostra. |
| **Pedile a la IA que…** | Série curta: uma tarefa por vídeo (pausar sem stock, ajustar precio, crear publicación) | Formato salvável, como o que viralizou no BR. |
| **Fechas que venden** | Black Friday, fim de ano: revisá tu tienda antes | Gancho de calendário argentino. |
| **Experiencia de compra y reputación** | "Tu publicación tiene nota. ¿La viste?" | Repete a fórmula do Reel viral. **Só com loja real e consentimento** (o usuário de teste não tem vendas). |
| **Quiénes somos** | "Plataforma brasileña; tu asistente es Claude o ChatGPT" | Confiança. Respeita o `nao_dizer`: nunca "IA brasileña". |

### Regras de número e texto (valem para toda peça)

- **Pode:** só números de `narrativa.provas`, com data.
  - Na Argentina vale "más de 2.400 cuentas de tiendas conectadas (oct. 2026)".
  - Evitar "9 marketplaces" e "1.116 herramientas": no país só existe o
    Mercado Libre, e parte das ferramentas é fiscal brasileira.
- **Não pode:**
  - preço (ARS/USD ainda não decidido);
  - as 243 vendas do cliente;
  - "5 minutos": não está medido. Cronometrar a conexão no usuário de teste
    antes de usar, ou dizer "con una sola autorización";
  - "prueba gratis": o CTA é "Más información" ou palavra de comentário.
- **Só mostrar na tela fluxo que funcionou no usuário de teste MLA.**
  - Fiscal, CPF/CNPJ, frete e promoções podem devolver erro na Argentina.
  - Gravar a conversa do Claude/ChatGPT em espanhol: a própria conversa é o
    conteúdo.
- **Revisão de espanhol por nativo antes de publicar.** O plano de expansão
  lista "espanhol de máquina" como risco.

### Quem fala nos vídeos (decisão sua)

- **A.** Você na câmera, no seu espanhol, assumindo ser brasileiro. Autêntico,
  mas precisa de revisão do roteiro.
- **B.** Tela com texto e narração da voz clonada (c463ef5b) em espanhol. É
  barato (TTS ≈ US$ 0,003/s), mas tem que ser testado e marcado como voz
  sintética.
- **C.** Criador argentino gravando (ver seção 5).

**Sugestão:** B para as demos de tela e A só no vídeo "Quiénes somos".

## 3. Os 10 primeiros conteúdos

**Link de destino de todos:** `https://l.tiops.com.br/ar?o=<origem>`.

- **Slug a criar:** `ar`, campanha `argentina-nov26`. Destino:
  - `https://marketplaces.tiops.com.br/es/mercado-libre-argentina-ia.html`, a
    página em espanhol da DEV-MC (PR #495, com FAQ e hreflang);
  - **no ar desde 03/11:** conferido 200 sem redirecionar, título "Cómo
    conectar ChatGPT o Claude a Mercado Libre Argentina", hreflang `es-AR`,
    `es` e `pt-BR`;
  - quando o cadastro estiver em espanhol, dá para trocar o destino sem mudar
    o link: é só editar o slug.
- **Origens:** `meta-ar`, `ig-ar`, `yt-ar`, `bio-ar`, `manychat-ar`.

**CTA orgânico.**

- Enquanto não houver ManyChat em espanhol: "Link en la bio" ou "en la
  descripción".
- Depois: "Comentá CONECTAR y te lo mando por privado". Exige automação nova
  com DM em espanhol. O teste do ManyChat acaba em 14/11.

### Reels/Shorts (30–45 s, 9:16)

**Isca principal**, no modelo que funcionou para o concorrente:

- **CTA:** "Comentá CONECTAR y te mando el video para conectar Claude o
  ChatGPT a tu Mercado Libre".
- **DM com:**
  - o L1;
  - o link `l.tiops.com.br/ar?o=manychat-ar`;
  - botão "Más información".
- **Pré-requisito:** a automação em espanhol no ManyChat (o teste acaba em
  14/11).

**R1 · Tu Mercado Libre por chat**

- **Gancho:** "Le pedí a Claude que revise mi Mercado Libre… y lo hizo
  adentro de mi cuenta."
- **Roteiro:**
  - Tela do Claude em espanhol: "listá mis publicaciones sin stock".
  - Vem a lista.
  - "pausalas".
  - Confirma.
  - Corte para a publicação pausada no ML.
- **Fecho:** "No es un panel más. Tu IA opera tu tienda."
- **CTA:** Más información → `?o=meta-ar` (anúncio) / `?o=ig-ar`.

**R2 · Publicación desde una foto**

- **Gancho:** "Mandé una foto y la IA armó la publicación de Mercado Libre."
- **Roteiro:**
  - Foto de produto.
  - "creá la publicación en Mercado Libre Argentina".
  - A IA escolhe categoria, atributos e título.
  - Publicação criada (usuário de teste).
- **CTA:** link en la bio.

**R3 · Precio y stock sin abrir Mercado Libre**

- **Gancho:** "¿Cuántas pestañas abrís para cambiar un precio?"
- **Roteiro:**
  - "subí 10% el precio de las tazas y poné 20 de stock".
  - Feito.
  - Mostrar a publicação atualizada.
- **CTA:** Más información.

**R4 · Black Friday: revisá tu tienda antes** (publicar ~19/11)

- **Gancho:** "Faltan X días para Black Friday. ¿Tu tienda está lista?"
- **Roteiro:** checklist pedido à IA:
  - publicaciones sin stock;
  - títulos cortos;
  - fotos de baja calidad;
  - publicaciones pausadas.

  A IA devolve a lista do que arrumar.
- **CTA:** "Guardá este video". Salvar é o que escala.

**R5 · Preguntas que se pierden**

- **Gancho:** "Una pregunta sin responder es una venta que se fue."
- **Roteiro:**
  - Pergunta feita por um segundo usuário de teste MLA.
  - "respondé las preguntas pendientes, mostrame antes".
  - A IA sugere, você aprova e ela responde.
- **CTA:** Más información.
- **Pré-requisito:** criar o segundo usuário de teste MLA.

**R6 · Conectá tu cuenta con una autorización**

- **Gancho:** "Así conectás tu Mercado Libre a ChatGPT o Claude."
- **Roteiro:**
  - Caminho na tela nova (PR #496): Conectar → Mercado Livre → Argentina (ou
    México).
  - Autorizar.
  - Primeira pergunta à IA.
- **Quando:** só depois que cadastro e autorização estiverem em espanhol.
  Antes disso o vídeo mostraria tela em português.

**R7 · Somos brasileños (cara do Itamar)**

- **Gancho:** "Soy brasileño y te voy a contar por qué llegamos a Argentina."
- **Roteiro:**
  - O Mercado Libre é o mesmo app nos dois países.
  - "Más de 2.400 cuentas de tiendas conectadas (oct. 2026)."
  - Tu asistente sigue siendo Claude o ChatGPT; nosotros conectamos tu
    tienda.
- **CTA:** link en la bio.

**R0 · Extensão do Chrome: fora por enquanto**

- A DEV-MC conferiu em 03/11: o manifest só casa `*.mercadolivre.com.br` e
  `*.mercadolibre.com`, então ela não roda em `mercadolibre.com.ar`.
- O repositório é público e está somente leitura por decisão do Itamar.
- Só vira peça ("Tu publicación tiene nota. ¿La viste?") se ele decidir
  liberar o `.com.ar`.

### Vídeos longos (YouTube)

**L1 · Cómo conectar Mercado Libre con ChatGPT y Claude (paso a paso)** (8–12 min)

- Feito para a busca.
- **Capítulos:** qué es MCP · crear cuenta · Conectar → Mercado Livre → país ·
  conectar en Claude · conectar en ChatGPT · primeras 5 preguntas.
- **Quando:** depois do espanhol no cadastro. Até lá, gravar com legenda
  explicando a tela em português.
- **Link:** `?o=yt-ar`.

**L2 · Gestioná tu Mercado Libre con IA: una tarde de trabajo en una conversación** (12–15 min)

- Junta R1, R2, R3 e R5 numa sessão real no usuário de teste.

**L3 · Black Friday en Mercado Libre: preparala con IA** (8–10 min, publicar até 21/11)

- Checklist completo do R4, com prompts na descrição para copiar.

### Calendário sugerido (horário de Buenos Aires = Brasília)

O espanhol fica fora do feed BR: vai como anúncio, Reel de teste e YouTube.
Assim não colide com os cortes da live no @tiopstecnologia.

| Dia | Peça | Onde |
|---|---|---|
| ter 10/11 18h | R1 | anúncio AR + Short ES + Reel de teste |
| qui 12/11 18h | R2 | Short + Reel de teste |
| sáb 14/11 | L1 (versão com legenda) | YouTube |
| ter 17/11 18h | R3 | Short + Reel de teste (+ anúncio se R1 cansar) |
| qui 19/11 18h | R4 | Short + Reel de teste + anúncio |
| sáb 21/11 | L3 | YouTube |
| ter 24/11 18h | R5 | Short + Reel de teste |
| qui 26/11 18h | R7 | Reel de teste |
| sáb 28/11 | L2 | YouTube |
| quando o cadastro em ES estiver no ar | R6 | todos |

## 4. Mídia paga (Meta: Instagram e Facebook)

### Passo a passo da campanha

No Gerenciador de Anúncios, pelo Chrome, com `business_id` na URL. Conta
pré-paga `1322329366662228`; recarga pede o seu 2FA.

**1. Campanha**

- **Criar → objetivo Tráfego.**
- Nome: `AR | Trafego | Connect | nov26`.
- Sem categoria especial.

**2. Conjunto de anúncios**

- **Local da conversão:** Site.
- **Meta:**
  - "Maximizar visualizações da página de destino" se o site tiver Pixel da
    Meta;
  - senão, "Maximizar cliques no link". A DEV-MC confere o Pixel.
- **Orçamento:** R$ 30/dia por 14 dias = **R$ 420** (teste).
- **Localização:** Argentina, opção "Pessoas que moram neste local".
- **Idade:** 25–55.
- **Idioma:** espanhol.
- **Segmentação detalhada**, como sugestão ao Advantage+:
  - interesses Mercado Libre, Mercado Pago, Tiendanube, comércio eletrônico,
    empreendedorismo, pequenas empresas;
  - comportamento "Administradores de página de empresa".
- **Posicionamentos:** Advantage+ (Reels e Feed do Instagram e Facebook,
  Stories).

**3. Anúncio**

- **Identidade:** página da Tiops + @tiopstecnologia.
- **Vídeo:** R1 (depois testar R2 e R3).
- **Texto principal:** "Tu IA ya puede operar tu tienda de Mercado Libre:
  listá publicaciones, ajustá precios y pausá lo que no tiene stock, todo
  desde una conversación con ChatGPT o Claude."
- **Título:** "Conectá tu Mercado Libre a tu IA".
- **Botão:** **Más información**.
- **URL:** `https://l.tiops.com.br/ar?o=meta-ar`.

**4. Revisar → Publicar.** Só com o seu OK, porque é gasto.

### México: segundo conjunto de anúncios

Pode ficar na mesma campanha: `MX | Trafego | Connect | nov26`.

- **Localização:** México, opção "Pessoas que moram neste local".
- **Idade:** 25–55. **Idioma:** espanhol.
- **Interesses:** os mesmos, trocando Tiendanube por Mercado Libre México e
  e-commerce.
- **Orçamento:** R$ 30/dia por 14 dias = R$ 420 (o mesmo da AR, para comparar
  os países).
- **Vídeo:** versão `-mx` do R1.
- **Texto principal:** "Tu IA ya puede operar tu tienda de Mercado Libre: lista
  tus publicaciones, ajusta precios y pausa lo que no tiene stock, todo desde
  una conversación con ChatGPT o Claude."
- **Título:** "Conecta tu Mercado Libre a tu IA". **Botão:** Más información.
- **URL:** `https://l.tiops.com.br/mx?o=meta-mx`.
- **Mesma regra de parada da Argentina**, contando lojas com
  `site_id = MLM`.

**Total dos dois testes: R$ 840 em 14 dias.** Se quiser gastar menos, roda AR
primeiro e o México só depois do checkpoint do dia 5.

### Métricas e regra de parada

- **Métrica de sucesso (a que importa):** lojas MLA novas conectadas no
  período, contadas por `metadata.site_id = MLA` e pela tag argentina do CRM.
- **De apoio:**
  - cliques humanos no `l.tiops.com.br/ar?o=meta-ar`;
  - custo por clique;
  - taxa de cliques.

  Comparar com a campanha BR do Reel do Claude.
- **Seguidor não é métrica.** Anúncio não trouxe seguidor no BR (+126 em 30
  dias).
- **Dia 5:** se a taxa de cliques estiver muito abaixo da campanha BR, trocar o
  vídeo (R2 ou R3).
- **Fim dos R$ 420 sem nenhuma loja MLA conectada:** pausar e consertar o funil
  (cadastro em espanhol) antes de gastar mais.

**Atenção:** enquanto o cadastro estiver em português, quem clica cai na landing
em espanhol e depois num formulário em português. Por isso o teste é pequeno.
Escalar só depois da fase 2 dos idiomas.

**Mais tarde:**

- **Google/YouTube Ads** na busca "conectar Mercado Libre ChatGPT", na
  Argentina, depois que o L1 estiver no ar.
- **Campanha "Mensagens" (Direct)** quando o ManyChat em espanhol existir.

## 5. Parcerias

O que achamos (03/11/2026):

- **YouTube Shopping chegou à Argentina com o Mercado Libre** (jun/2026).
  - Criadores que falam de ML agora ganham comissão por vídeo e estão
    produzindo mais.
  - São o alvo para integração paga.
  - Não conseguimos nomes verificados na busca. **Não citar nenhum criador sem
    conferir o canal.**
- **Mercado Libre Experience Argentina:** evento de vendedores do ML. Conferir a
  data da próxima edição; serve para estande, palestra ou só para encontrar
  agências.
- **Programa de parceiros do ML (Developer Partner Program):** exige faturamento
  mensal mínimo com vendedores de USD 1,5 milhão na Argentina. Não é para agora.
- **Consultorias "certificadas" de ML na Argentina existem.** Exemplo:
  Algoritmo Digital, que se apresenta assim (não confirmado em fonte oficial).
- **Ferramentas argentinas do ecossistema:** Nubimetrics, Real Trends,
  Producteca, Tiendanube. Conferir, porque são em parte concorrentes. Servem de
  referência de linguagem e preço, não de parceiro imediato.

### Como montar

1. **Criadores.**
   - **Busca no YouTube e no Instagram:** "vender en Mercado Libre Argentina",
     "Mercado Libre emprendedores".
   - **Critério:** 5 mil a 50 mil inscritos, postou nos últimos 30 dias,
     público argentino.
   - **Oferta:** integração paga de valor fixo, com o criador gravando na
     própria loja (o consentimento vem junto) e roteiro revisado por nós.
   - Comissão por cupom só depois de corrigir o cupom de afiliado, que hoje não
     registra a indicação.
2. **Agências:** 1 ou 2 agências que operam contas de ML na Argentina, pela
   central do parceiro (cupom de 5% + comissão), com o mesmo bloqueio do cupom.
3. **Primeiro cliente:** pedir ao cliente argentino:
   - revisão do espanhol das peças;
   - autorização para um caso, com dados mascarados.

   Só com o "sim" dele por escrito.

## Dependências e quem faz

| Item | Quem |
|---|---|
| Revisor nativo de espanhol (peças + landing) | Itamar decide quem |
| Cadastro, planos e autorização em espanhol (fase 2 dos idiomas) | DEV-MC |
| Pixel da Meta na landing e evento "conta conectada" | DEV-MC |
| Extensão do Chrome em `.com.ar`: não funciona hoje; repositório somente leitura | Itamar decide se libera |
| Página em espanhol `/es/mercado-libre-argentina-ia.html` + llms.txt em espanhol (PR #495) | DEV-MC, publicando |
| Segundo usuário de teste MLA + 4 ou 5 publicações realistas | DEV-MC ou esta sessão |
| Slug `ar` no encurtador | esta sessão, com OK |
| ManyChat em espanhol (palavra CONECTAR) — **prioridade**, é a isca que funcionou para o concorrente; exige decidir o plano pago (teste acaba 14/11) | esta sessão, com OK |
| Quem atende DM e chamado em espanhol | Itamar |
| Preço em USD | Itamar |

## Decisões do Itamar

1. Perfil em espanhol agora ou na etapa 2 (recomendado: etapa 2).
2. Quem fala nos vídeos: A, B ou C.
3. Teste de anúncio de R$ 420 (R$ 30/dia × 14 dias) começando em 10/11.
4. Revisor de espanhol.
5. Criar o slug `ar` e preparar o ManyChat em espanhol (e manter o ManyChat
   pago depois de 14/11).
6. Mandar DM ao @ignaciooleo propondo parceria, ou tratá-lo só como
   concorrente.
7. México em paralelo com a Argentina (R$ 840 no total) ou depois do
   checkpoint da Argentina.
8. Produzir a peça do Buen Fin para o México até 11/11.
