"""Roteiro do vídeo "Treinamento do Marketplace Connect do zero" (tempos no BRUTO, em s).

Coordenadas de zoom são do quadro cheio do Vids (1920x1080); a tela gravada
fica em SCREEN e o balão da câmera em CAM_IN.
"""

SCREEN = (63, 75, 1648, 966)
CAM_IN = (1625, 786, 1862, 1023)

CAPITULOS = [
    (0.0, 'Novo: treinamento do zero com IA'),
    (24.6, 'Instalando o conector no ChatGPT'),
    (84.0, 'Trilha, ranking e medalhas'),
    (120.4, 'Iniciando o Treino MAC'),
    (183.9, 'O ambiente gamificado'),
    (236.98, 'Abrindo o app e as missões'),
    (287.7, 'Ranking dos sellers'),
    (315.6, 'Conquistas e habilidades'),
    (334.7, 'Por que treinar na prática'),
    (403.8, 'Funciona no celular'),
    (433.7, 'Prêmios, certificação e embaixador'),
    (483.0, 'Indique e ganhe'),
]

# (ini, fim, cx, cy, zoom) — centro no quadro cheio
ZOOMS = [
    (33.8, 35.5, 300, 360, 1.7),       # Plugins na barra lateral
    (35.5, 38.4, 1480, 290, 1.9),      # Adicionar > servidor MCP personalizado
    (38.4, 41.6, 860, 560, 1.35),      # janela do servidor MCP
    (51.5, 55.5, 330, 520, 1.6),       # Conectar a IA / Agentes IA
    (56.0, 67.0, 930, 600, 1.6),       # URLs dos conectores e Copiar
    (70.0, 79.0, 860, 480, 1.8),       # nome "Treino MAC" e URL
    (79.0, 86.5, 860, 700, 1.5),       # OAuth e "Entendo e quero continuar"
    (93.0, 99.5, 860, 700, 1.4),
    (100.0, 104.5, 855, 564, 1.5),     # Conectar a Treino MAC
    (104.5, 110.5, 850, 564, 1.55),    # Autorizar acesso
    (125.5, 140.5, 1030, 690, 1.6),    # @Treino MAC no chat
    (141.0, 146.0, 1105, 330, 1.8),    # mensagem enviada
    (184.6, 191.5, 856, 527, 1.45),    # tela do Claude
    (191.5, 200.8, 560, 420, 2.0),     # Força
    (200.8, 209.9, 560, 560, 1.9),     # Estoque
    (209.9, 214.3, 840, 540, 1.9),     # Vendas
    (214.3, 219.3, 1180, 600, 1.9),    # Estúdio
    (243.5, 249.8, 460, 400, 2.0),     # "Aberto: Treino MAC" + expandir
    (251.0, 262.0, 1100, 800, 1.45),   # missões
    (262.0, 286.5, 1120, 760, 1.35),
    (288.5, 300.5, 1100, 780, 1.7),    # ranking
    (300.5, 307.0, 1000, 330, 1.9),    # nome no ranking
    (307.0, 313.5, 1100, 780, 1.5),
    (317.5, 326.0, 1090, 760, 1.8),    # medalhas
    (326.0, 333.5, 1000, 860, 1.6),    # habilidades
    (345.0, 356.5, 1100, 880, 1.6),    # missão com o prompt
    (414.5, 429.0, 590, 580, 1.3),     # celular (DevTools)
    (484.0, 489.5, 400, 600, 1.9),     # Indique e ganhe
    (490.5, 500.5, 690, 440, 1.7),     # cupom
    (500.5, 511.0, 1150, 480, 2.0),    # comissão
    (515.0, 528.5, 880, 760, 1.35),    # link para divulgar
    (528.5, 536.5, 1200, 420, 2.0),    # cliques
]

# (ini, fim, chapéu, texto, ícone)
TAGS = [
    (12.9, 17.6, 'NOVO CONECTOR', 'Funciona no ChatGPT e no Claude', 'estrela'),
    (167.0, 174.5, 'JÁ TESTADO', 'No Claude a trilha já está completa', 'check'),
    (184.6, 191.5, 'TREINO MAC', 'Um ambiente gamificado', 'controle'),
    (192.3, 200.8, 'NÍVEL 1', 'Força: o início de tudo', 'raio'),
    (201.5, 210.0, 'NÍVEL 2', 'Estoque mais avançado', 'cadeado'),
    (210.5, 214.5, 'NÍVEIS SEGUINTES', 'Pedidos e vendas avançados', 'cadeado'),
    (214.6, 219.3, 'ATÉ O FIM DA TRILHA', 'Estúdio de criação de anúncios', 'estrela'),
    (243.5, 250.0, 'DICA', 'Abra o app em tela cheia no ↗', 'raio'),
    (250.5, 257.5, 'PROGRESSO SALVO', 'A trilha fica gravada na sua conta', 'check'),
    (268.7, 278.0, 'MISSÕES', 'Cada etapa concluída libera a próxima', 'cadeado'),
    (278.2, 286.5, 'PASSO A PASSO', 'A IA mostra o caminho completo', 'estrela'),
    (289.0, 297.0, 'RANKING', 'Sellers reais que já fizeram o treino', 'trofeu'),
    (302.0, 307.0, 'PERSONALIZE', 'Troque o seu nome no ranking', 'estrela'),
    (327.0, 333.5, 'NÍVEL 1', 'As habilidades que você ganhou', 'check'),
    (345.0, 356.5, 'EM CADA MISSÃO', 'O prompt exato para você usar', 'raio'),
    (357.4, 364.8, 'PRÉ-REQUISITO', 'Marketplace Connect configurado', 'check'),
    (384.0, 393.5, 'PARA TODOS', 'Do básico ao avançado', 'estrela'),
    (404.0, 413.0, 'NOVIDADE', 'Funciona no celular', 'celular'),
    (419.5, 428.5, 'NO CELULAR', 'O treino completo no app do ChatGPT', 'celular'),
    (434.0, 442.5, 'TREINE COM A IA', 'Brinque à vontade para aprender', 'controle'),
    (485.0, 490.8, 'INDIQUE E GANHE', 'Já está no Marketplace Connect', 'presente'),
    (491.0, 500.5, 'SEU CUPOM', 'Desconto para quem assinar com você', 'presente'),
    (501.5, 511.0, 'COMISSÃO', 'Ganhe na recorrência da indicação', 'moeda'),
    (529.2, 536.5, 'ACOMPANHE', 'Os cliques no seu link aparecem aqui', 'link'),
]

# medalhas: (ini, troca, fim)
MEDALHA = (316.0, 322.6, 326.0)
XP = (297.2, 300.8, '+800 XP')

# passos no rodapé: (ini, fim, chapéu, texto)
PASSOS = [
    (33.6, 37.0, 'PASSO 1', 'No ChatGPT, abra Plugins'),
    (37.0, 44.0, 'PASSO 2', 'Adicionar servidor MCP personalizado'),
    (46.5, 56.0, 'PASSO 3', 'No Marketplace Connect: Conectores de IA'),
    (56.0, 66.0, 'PASSO 4', 'Copie a URL de um conector'),
    (66.0, 82.0, 'PASSO 5', 'Cole no ChatGPT e dê o nome Treino MAC'),
    (100.0, 108.5, 'PASSO 6', 'Conecte e autorize o acesso'),
    (516.0, 520.4, 'PASSO 1', 'Gere o seu cupom'),
    (520.4, 524.6, 'PASSO 2', 'Gere o link do plano'),
    (524.6, 529.0, 'PASSO 3', 'Copie o link curto e mande'),
]

PROMPT = (129.5, 140.6, 'DIGITE NO CHAT', '@Treino MAC iniciar treinamento')

# painel lateral: (ini, fim, título, [(t, item, detalhe), ...])
PAINEIS = [
    (87.0, 119.6, 'TRILHA DE TREINAMENTO', [
        (87.5, 'NÍVEL 1', 'Bem básico: o início de tudo'),
        (94.0, 'RANKING', 'Você sobe conforme avança'),
        (96.5, 'HABILIDADES', 'Ganhas ao longo das trilhas'),
        (102.3, 'CONQUISTAS', 'E a sua medalha'),
        (106.0, 'BRINDES E DESCONTOS', 'Para quem junta medalhas'),
        (113.5, 'NÍVEL EXPERT', 'Avançado, vale até mentoria'),
    ]),
    (443.5, 482.8, 'O QUE VEM POR AÍ', [
        (444.5, 'TOPO DO RANKING', 'Eu acompanho quem lidera'),
        (449.5, 'BRINDES', 'Para quem completar as trilhas'),
        (452.6, 'DESCONTO', 'Na mensalidade, por exemplo'),
        (462.5, 'TRILHA EXPERT', 'Do nível 3 ao 5'),
        (471.2, 'CERTIFICAÇÃO', 'Do Marketplace Connect'),
        (475.5, 'EMBAIXADOR', 'Indique e crie o seu cupom'),
    ]),
]

# cartões de tela cheia: (ini, fim, tipo)
INTERLUDIOS = [
    (18.0, 24.4, 'titulo'),
    (146.5, 155.2, 'zero'),
    (336.0, 344.2, 'versus'),
    (394.5, 403.0, 'programador'),
]
