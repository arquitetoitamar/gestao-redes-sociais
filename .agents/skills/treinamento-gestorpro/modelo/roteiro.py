"""Roteiro visual da aula (exemplo real: "Promoções e Guardião de margem", 31/10/2026). Cada seção da narração (narracao.md) tem uma lista de eventos
disparados por um trecho da fala (achado no tempo por palavra do whisper) ou por segundos
desde o início da seção.

Coordenadas:
- 'pag': retângulo na página de Promoções, em pontos CSS dentro da área principal
  (x a partir da borda esquerda da área, y a partir do topo do conteúdo rolado).
- 'tela': retângulo na tela 16:9 inteira (1470 x 827 pontos), usado nos estados capturados.

Eventos: (gatilho, tipo, dados)
  foco      {'pag': r} ou {'tela': r}, opcional 'z'      move a câmera (e a rolagem) até o retângulo
  luz       {'pag'|'tela': r, 'rot': texto opcional}      escurece o resto e contorna o retângulo
  apaga     {}                                            tira a luz
  cartao    {'chap', 'tit', 'txt'}                        cartão explicativo no canto inferior esquerdo
  grande    {'chap', 'tit', 'txt', 'cor'}                 cartão grande no centro (conceito)
  fecha     {}                                            tira cartões
  estado    {'nome'} ou {'nome': None}                    troca a tela por uma captura (regras, modal...)
  clique    {'pag'|'tela': r}                             cursor vai até o ponto e clica
  geral     {} ou {'S': 0}                                câmera volta para a tela inteira (S: rolagem)
"""

# textos da abertura, da cartela final e da publicação
AULA = {
    'titulo': 'Promoções e Guardião de margem',
    'subtitulo': 'Como o GestorPro decide em quais promoções entrar, anúncio por anúncio',
    'caminho': 'Operação  ›  Promoções',
    'fecho': 'O Guardião entra quando vale e sai quando dói',
    'descricao': ('Aula do treinamento GestorPro: a tela Operação › Promoções e o Guardião de margem, o agente que '
                  'decide, anúncio por anúncio, em quais promoções do Mercado Livre e da Shopee entrar e de quais sair, '
                  'mantendo a margem com o desconto dentro da sua banda.'),
    'itens': ['A banda de margem: piso, teto e exceções por anúncio',
              'O que o Guardião fez nas últimas 24 horas e a margem medida em promoção',
              'Rebate do Mercado Livre conferido pedido a pedido',
              'Movimentação de promoções e o alerta de vaivém',
              'Central de promoções: subsidiadas, relâmpago, sem promoção e margem negativa',
              'Campanhas disponíveis e envio para aprovação',
              'Promoções no automático: entrar e sair sozinho',
              'Ações em massa: piso/teto padrão, motor de preço e catálogo'],
    'tags': ['guardião de margem', 'promoções mercado livre', 'margem de lucro', 'rebate mercado livre',
             'campanhas mercado livre', 'promoção shopee'],
}

# estados capturados além da página: 'tela' = captura da tela inteira (outra página, modal);
# 'pagina' = a mesma página com outro estado (aba, filtro), costurado na rolagem 'scroll'
# ('corte' = pixels que faltaram no topo da captura).
ESTADOS = {
    'regras': {'arquivo': 'regras-752.png', 'tipo': 'tela'},
    'modal': {'arquivo': 'modal-subsidiadas.png', 'tipo': 'tela'},
    'sugestao': {'arquivo': 'campanhas-sugestao-2326.png', 'tipo': 'pagina', 'scroll': 2326, 'corte': 36},
}

# blocos da página de Promoções (pontos CSS na área principal)
KPI = (20, 155, 1179, 145)
KPI_PROMO = (20, 155, 228, 145)
KPI_ENTR = (258, 155, 228, 145)
KPI_SAIU = (496, 155, 228, 145)
KPI_MARG = (733, 155, 228, 145)
KPI_REB = (971, 155, 228, 145)
MOV = (20, 328, 700, 400)
GRAF = (30, 380, 680, 200)
VAIVEM = (32, 594, 676, 130)
CHIP = (52, 684, 150, 28)
REGRAS = (734, 736, 465, 306)
BANDA = (749, 937, 435, 58)
VER_REGRAS = (749, 1004, 178, 23)
REBATE = (20, 1060, 1179, 860)
REB_RESUMO = (21, 1127, 1177, 91)
REB_LINHAS = (21, 1225, 1177, 230)
CENTRAL = (20, 1986, 1179, 160)
C_SUBS = (20, 1986, 287, 160)
C_RELAMP = (317, 1986, 287, 160)
C_SEM = (615, 1986, 287, 160)
C_NEG = (912, 1986, 287, 160)
ABRIR_SUBS = (255, 2118, 46, 20)
CAMP = (20, 2340, 1179, 420)
ABAS = (21, 2400, 1177, 40)
ABA_SUG = (151, 2405, 123, 30)
COLUNAS = (21, 2440, 1177, 36)
LINHAS_SUG = (21, 2476, 1177, 270)
PLANILHA = (790, 2660, 114, 28)
ENVIAR = (935, 2480, 161, 265)
AUTO = (20, 3975, 1179, 290)
AUTO_ENTRA = (35, 4084, 1149, 50)
AUTO_SAI = (35, 4148, 1149, 50)
RESULTADO = (35, 4200, 1149, 52)
MASSA = (20, 4318, 1179, 310)
M_FIXAR = (35, 4398, 1149, 54)
M_MOTOR = (35, 4460, 1149, 54)
M_CATALOGO = (35, 4524, 1149, 54)
RODAR = (1029, 4582, 155, 36)
TOPO = (0, 0, 1219, 330)

# menu e estados (pontos na tela 16:9 inteira)
MENU_PROMO = (9, 142, 216, 36)
REGRAS_CAMPOS = (268, 214, 430, 110)
MODAL = (215, 50, 1040, 600)
MODAL_DECISAO = (980, 120, 260, 520)

SECOES = {
    1: [
        (0.0, 'geral', {'S': 0}),
        ('se você entra em todas', 'grande', {'chap': 'ENTRAR EM TODAS', 'tit': 'a margem vai embora', 'cor': 'red'}),
        ('se você não entra', 'grande', {'chap': 'NÃO ENTRAR', 'tit': 'você perde venda', 'cor': 'red'}),
        ('pra isso que existe', 'grande', {'chap': 'GUARDIÃO DE MARGEM', 'tit': 'decide por você, anúncio por anúncio', 'cor': 'yel'}),
        ('com uma regra só', 'grande', {'chap': 'UMA REGRA SÓ', 'tit': 'a margem com o desconto fica dentro da sua banda', 'cor': 'green'}),
        ('nesta aula', 'fecha', {}),
        ('ela fica em operação', 'foco', {'tela': MENU_PROMO, 'z': 1.7}),
        ('ela fica em operação', 'luz', {'tela': MENU_PROMO, 'rot': 'Operação › Promoções'}),
    ],
    2: [
        (0.0, 'apaga', {}),
        ('cartão regras ativas', 'foco', {'pag': REGRAS}),
        ('cartão regras ativas', 'luz', {'pag': REGRAS, 'rot': 'Regras ativas'}),
        ('o piso aqui', 'foco', {'pag': BANDA, 'z': 1.9}),
        ('o piso aqui', 'luz', {'pag': BANDA}),
        ('o piso aqui', 'cartao', {'chap': 'PISO', 'tit': 'Margem mínima que você aceita', 'txt': 'Abaixo dele o Guardião não entra. Se já estiver dentro, ele sai.'}),
        ('o teto é o limite', 'cartao', {'chap': 'TETO', 'tit': 'O limite de cima', 'txt': 'Acima dele, o Guardião pode aceitar um desconto maior.'}),
        ('em ver regras e exceções', 'clique', {'pag': VER_REGRAS}),
        ('em ver regras e exceções', 'fecha', {}),
        ('cada anúncio pode ter', 'estado', {'nome': 'regras'}),
        ('cada anúncio pode ter', 'foco', {'tela': REGRAS_CAMPOS, 'z': 1.6}),
        ('cada anúncio pode ter', 'luz', {'tela': REGRAS_CAMPOS, 'rot': 'Piso e teto'}),
        ('a regra do anúncio sempre vence', 'cartao', {'chap': 'EXCEÇÕES', 'tit': 'Cada anúncio pode ter o seu piso', 'txt': 'A regra do anúncio sempre vence a regra da loja.'}),
        ('um ponto muito importante', 'apaga', {}),
        ('um ponto muito importante', 'grande', {'chap': 'ATENÇÃO', 'tit': 'sem custo cadastrado não existe margem', 'txt': 'o anúncio sem custo fica fora de tudo', 'cor': 'yel'}),
    ],
    3: [
        (0.0, 'fecha', {}),
        (0.0, 'estado', {'nome': None}),
        (0.0, 'geral', {'S': 0}),
        ('essa fileira de cartões', 'foco', {'pag': KPI}),
        ('essa fileira de cartões', 'luz', {'pag': KPI}),
        ('em promoção agora', 'luz', {'pag': KPI_PROMO, 'rot': 'Em promoção agora'}),
        ('entraram', 'luz', {'pag': KPI_ENTR, 'rot': 'Entraram (24 h)'}),
        ('saíram', 'luz', {'pag': KPI_SAIU, 'rot': 'Saíram (24 h)'}),
        ('e margem medida', 'luz', {'pag': KPI_MARG, 'rot': 'Margem medida'}),
        ('e margem medida', 'cartao', {'chap': 'MARGEM MEDIDA', 'tit': 'Pedidos reais com promoção', 'txt': 'Já com o custo. Não é estimativa, é o que aconteceu.'}),
        ('se num dia saiu mais', 'luz', {'pag': KPI_SAIU}),
        ('sair nesse caso', 'cartao', {'chap': 'SAIU MAIS DO QUE ENTROU?', 'tit': 'É o Guardião protegendo o lucro', 'txt': 'As promoções novas pediam desconto que levava a margem abaixo do piso.'}),
    ],
    4: [
        (0.0, 'fecha', {}),
        ('o rebate do mercado livre', 'foco', {'pag': KPI_REB, 'z': 1.8}),
        ('o rebate do mercado livre', 'luz', {'pag': KPI_REB, 'rot': 'Rebate do ML'}),
        ('o cartão verde', 'cartao', {'chap': 'REBATE', 'tit': 'O Mercado Livre paga parte do desconto', 'txt': 'O cartão verde mostra quanto ele pagou nos últimos 30 dias.'}),
        ('e a tabela', 'fecha', {}),
        ('e a tabela', 'foco', {'pag': REB_RESUMO}),
        ('e a tabela', 'luz', {'pag': REB_RESUMO, 'rot': 'Desconto dado · saiu da loja · pago pelo ML · previsto'}),
        ('a gente confere', 'cartao', {'chap': 'PEDIDO A PEDIDO', 'tit': 'Quanto o ML pagou de verdade', 'txt': 'Contra o que a promoção previa.'}),
        ('e atenção', 'apaga', {}),
        ('e atenção', 'grande', {'chap': 'JÁ ESTÁ NA SUA MARGEM', 'tit': 'o ML paga reduzindo a tarifa do pedido', 'txt': 'o cartão só mostra separado: não é contado duas vezes', 'cor': 'green'}),
        ('em cada linha', 'fecha', {}),
        ('em cada linha', 'foco', {'pag': REB_LINHAS}),
        ('em cada linha', 'luz', {'pag': REB_LINHAS, 'rot': 'Anúncio · pedidos · quanto o ML bancou'}),
    ],
    5: [
        (0.0, 'fecha', {}),
        (0.0, 'apaga', {}),
        ('movimentação de promoções', 'foco', {'pag': MOV}),
        ('movimentação de promoções', 'luz', {'pag': GRAF, 'rot': 'Últimos 14 dias'}),
        ('a barra verde', 'cartao', {'chap': 'VERDE PARA CIMA', 'tit': 'Entradas', 'txt': 'Vermelho para baixo: saídas.'}),
        ('essa caixa amarela', 'luz', {'pag': VAIVEM, 'rot': 'Alerta de vaivém'}),
        ('essa caixa amarela', 'cartao', {'chap': 'VAIVÉM', 'tit': 'Saiu 3 vezes ou mais', 'txt': 'O canal ou uma campanha da loja recoloca; o Guardião tira de novo.'}),
        ('para parar o vai e vem', 'cartao', {'chap': 'PARA PARAR O VAIVÉM', 'tit': 'Dois caminhos', 'txt': '1. Tire o anúncio da campanha automática do ML.  2. Ajuste o piso dele.'}),
        ('clicando no código', 'clique', {'pag': CHIP}),
        ('clicando no código', 'luz', {'pag': CHIP}),
    ],
    6: [
        (0.0, 'fecha', {}),
        (0.0, 'apaga', {}),
        ('central de promoções', 'foco', {'pag': CENTRAL}),
        ('central de promoções', 'luz', {'pag': CENTRAL}),
        ('subsidiadas são', 'luz', {'pag': C_SUBS, 'rot': 'Subsidiadas'}),
        ('se aparecer zero', 'cartao', {'chap': 'CABEM NA BANDA: 0', 'tit': 'Com o subsídio de hoje', 'txt': 'nenhuma fecha acima do seu piso.'}),
        ('relâmpago são', 'fecha', {}),
        ('relâmpago são', 'luz', {'pag': C_RELAMP, 'rot': 'Relâmpago'}),
        ('anúncios sem promoção são', 'luz', {'pag': C_SEM, 'rot': 'Sem promoção'}),
        ('e margem negativa', 'luz', {'pag': C_NEG, 'rot': 'Margem negativa'}),
        ('é aqui que está o dinheiro', 'cartao', {'chap': 'AQUI ESTÁ O DINHEIRO', 'tit': 'Vendendo abaixo do piso', 'txt': 'Revise o custo ou o preço desses anúncios.'}),
        ('cada cartão abre', 'fecha', {}),
        ('cada cartão abre', 'clique', {'pag': ABRIR_SUBS}),
        ('a lista já filtrada', 'estado', {'nome': 'modal'}),
        ('a lista já filtrada', 'apaga', {}),
        ('a lista já filtrada', 'foco', {'tela': MODAL, 'z': 1.15}),
    ],
    7: [
        (0.0, 'estado', {'nome': None}),
        (0.0, 'apaga', {}),
        ('campanhas disponíveis', 'foco', {'pag': CAMP}),
        ('as abas filtram', 'luz', {'pag': ABAS, 'rot': 'Todas · Com sugestão · Já dentro · Sem custo · Nenhum cabe'}),
        ('com sugestão', 'clique', {'pag': ABA_SUG}),
        ('já dentro', 'estado', {'nome': 'sugestao'}),
        ('nas colunas', 'luz', {'pag': COLUNAS, 'rot': 'Elegíveis · valem a pena · margem se entrar · sem custo'}),
        ('valem a pena ou seja', 'cartao', {'chap': 'VALEM A PENA', 'tit': 'Mantêm a margem dentro da banda', 'txt': 'E a margem que você teria se entrar.'}),
        ('esse número de sem custo', 'luz', {'pag': PLANILHA, 'rot': 'baixa a planilha'}),
        ('esse número de sem custo', 'cartao', {'chap': 'SEM CUSTO', 'tit': 'Baixe a planilha e preencha', 'txt': 'Sem custo, o anúncio fica fora da conta.'}),
        ('e o botão enviar', 'luz', {'pag': ENVIAR, 'rot': 'Enviar para aprovação'}),
        ('nada é inscrito', 'cartao', {'chap': 'SEU OK', 'tit': 'Nada é inscrito sem a sua aprovação', 'txt': 'A proposta vai para a fila.'}),
    ],
    8: [
        (0.0, 'fecha', {}),
        (0.0, 'estado', {'nome': None}),
        (0.0, 'apaga', {}),
        ('promoções no automático', 'foco', {'pag': AUTO}),
        ('entrar automaticamente', 'foco', {'pag': AUTO_ENTRA, 'z': 1.05}),
        ('entrar automaticamente', 'luz', {'pag': AUTO_ENTRA, 'rot': 'Entrar automaticamente'}),
        ('entrar automaticamente', 'cartao', {'chap': 'ENTRAR', 'tit': 'Campanhas com subsídio que cabem na banda', 'txt': 'Uma promoção por anúncio: a que deixa a maior margem.'}),
        ('sair automaticamente', 'foco', {'pag': AUTO_SAI, 'z': 1.05}),
        ('sair automaticamente', 'luz', {'pag': AUTO_SAI, 'rot': 'Sair automaticamente'}),
        ('sair automaticamente', 'cartao', {'chap': 'SAIR', 'tit': 'Margem abaixo do piso', 'txt': 'O anúncio volta ao preço cheio.'}),
        ('essa autorização', 'cartao', {'chap': 'SÓ PARA PROMOÇÕES', 'tit': 'Passa por cima da fila', 'txt': 'Tudo fica no Registro de ações. Desliga quando quiser.'}),
        ('aqui embaixo fica', 'fecha', {}),
        ('aqui embaixo fica', 'foco', {'pag': RESULTADO, 'z': 1.05}),
        ('aqui embaixo fica', 'luz', {'pag': RESULTADO, 'rot': 'Resultado desde a entrada'}),
        ('isso é medido nos pedidos', 'cartao', {'chap': 'MEDIDO', 'tit': 'Nos pedidos, não estimado', 'txt': 'Anúncios, pedidos, receita, lucro e margem realizada.'}),
    ],
    9: [
        (0.0, 'fecha', {}),
        (0.0, 'apaga', {}),
        ('as ações em massa', 'foco', {'pag': MASSA}),
        ('fixar piso e teto', 'foco', {'pag': M_FIXAR, 'z': 1.05}),
        ('fixar piso e teto', 'luz', {'pag': M_FIXAR, 'rot': 'Fixar piso/teto padrão'}),
        ('fixar piso e teto', 'cartao', {'chap': 'FIXAR', 'tit': 'Copia a banda e congela', 'txt': 'Mudar o piso do negócio depois não mexe nesses anúncios.'}),
        ('ligar o motor de preço', 'foco', {'pag': M_MOTOR, 'z': 1.05}),
        ('ligar o motor de preço', 'luz', {'pag': M_MOTOR, 'rot': 'Motor de preço'}),
        ('ligar o motor de preço', 'cartao', {'chap': 'MOTOR DE PREÇO', 'tit': 'Reprecificação, não promoção', 'txt': 'Quem dá desconto só por promoção deixa desligado.'}),
        ('priorizar catálogo', 'foco', {'pag': M_CATALOGO, 'z': 1.05}),
        ('priorizar catálogo', 'luz', {'pag': M_CATALOGO, 'rot': 'Priorizar catálogo'}),
        ('priorizar catálogo', 'cartao', {'chap': 'CATÁLOGO', 'tit': 'Preço que ganha o buy box', 'txt': 'Só quando ele cabe no seu piso.'}),
        ('e rodar o motor agora', 'foco', {'pag': RODAR, 'z': 1.6}),
        ('e rodar o motor agora', 'luz', {'pag': RODAR, 'rot': 'Rodar o motor agora'}),
        ('tudo isso vai para a fila', 'cartao', {'chap': 'FILA DE APROVAÇÃO', 'tit': 'Tudo passa pelo seu ok', 'txt': 'Rodar agora só não espera a próxima sincronização.'}),
    ],
    10: [
        (0.0, 'fecha', {}),
        (0.0, 'apaga', {}),
        (0.0, 'geral', {'S': 0}),
        ('resumindo', 'grande', {'chap': 'RESUMINDO', 'tit': 'entra quando vale, sai quando dói', 'cor': 'yel'}),
        ('você define o piso', 'grande', {'chap': 'VOCÊ', 'tit': 'define o piso, cadastra o custo e aprova a fila', 'cor': 'green'}),
        ('e cada número', 'grande', {'chap': 'GESTORPRO', 'tit': 'cada número medido nos seus pedidos', 'cor': 'yel'}),
    ],
}

CAPITULOS = {1: 'Por que o Guardião existe', 2: 'A banda: piso e teto', 3: 'O que ele fez em 24 horas',
             4: 'Rebate do Mercado Livre', 5: 'Movimentação e vaivém', 6: 'Central de promoções',
             7: 'Campanhas disponíveis', 8: 'Promoções no automático', 9: 'Ações em massa', 10: 'Resumo'}
