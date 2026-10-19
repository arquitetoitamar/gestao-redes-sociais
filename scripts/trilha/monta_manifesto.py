#!/usr/bin/env python3
"""Reescreve o manifesto da trilha básica a partir desta tabela.

Nome, descrição e tags de TODA aula saem daqui — é o que garante padrão único.
Rodar de novo é seguro: preserva o que já está publicado (video_id, posição).
"""
import json, os, sys

PL_B, PL_A = 'PLW3upCIZHed4', 'PLavmDN-e4LEE'
PL_ADOCAO = 'PLGhRDamQTH7o'   # 'Comece por aqui': demo + a trilha, espelhada
LINK = 'https://www.youtube.com/playlist?list=' + PL_B
GUIA = 'https://claude.ai/code/artifact/53bebbdf-0a74-4309-9c3c-ea591be370f9'
BASE = ['marketplace connect', 'trilha basica']

# numero, módulo, título curto, uma linha do que resolve, tags extras
AULAS = [
 (1, 'Entender', 'O que é o Marketplace Connect',
  'O que o Marketplace Connect é, o que ele não é, e por que ele fica entre a sua IA e as suas contas de marketplace.',
  ['o que e', 'ia para marketplace']),
 (2, 'Entender', 'O que dá pra fazer com ele',
  'Uma volta pelo que a IA passa a fazer direto na sua conta: consultar, criar, corrigir e acompanhar anúncio e pedido.',
  ['ia para marketplace', 'demonstracao']),
 (3, 'Entender', 'Com o que ele integra',
  'Os canais em produção, um por um, e o que dá para fazer em cada um deles.',
  ['integracao', 'mercado livre', 'shopee']),
 (4, 'Ligar', 'Como contratar e ativar',
  'Da contratação ao primeiro acesso: onde ativar e o que aparece na tela quando deu certo.',
  ['ativacao', 'primeiro acesso']),
 (5, 'Ligar', 'Autorizar sua loja do marketplace',
  'Tela a tela, com Mercado Livre — inclusive o consentimento do marketplace, que é onde a dúvida costuma aparecer.',
  ['autorizacao', 'mercado livre']),
 (6, 'Ligar', 'Qual endereço conectar: raiz ou conector do canal',
  'Raiz ou conector do canal: por que a lista de ferramentas trunca no cliente de IA e qual endereço resolve.',
  ['conector', 'mcp']),
 (7, 'Ligar', 'Conectar no Claude',
  'Como ligar o Marketplace Connect no Claude, do endereço do conector até a autorização.',
  ['claude', 'conector']),
 (8, 'Ligar', 'Conectar no ChatGPT',
  'Como ligar o Marketplace Connect no ChatGPT, com um conector separado para cada canal.',
  ['chatgpt', 'conector']),
 (9, 'Operar', 'Listar suas contas e conferir o que entrou',
  'Como pedir a lista de contas, ler o que volta e o que fazer quando a conta autorizada não aparece.',
  ['contas', 'conferencia']),
 (10, 'Operar', 'Várias lojas na mesma conta',
  'Como operar mais de uma loja e mais de um canal pela mesma IA, sem misturar o que é de quem.',
  ['multi loja', 'escala']),
 (11, 'Operar', 'Seu primeiro anúncio pela IA',
  'Do dado do produto ao anúncio criado com variações, sem sair da conversa com a IA. A IA acha a categoria certa, '
  'puxa os atributos obrigatórios daquela categoria, monta o rascunho e sobe o anúncio.',
  ['mercado livre', 'anuncio']),
 (12, 'Operar', 'Como criar um agente',
  'Como montar um agente que responde pergunta de comprador sozinho, com o contexto da sua operação.',
  ['agente', 'atendimento']),
 (13, 'Crescer', 'Equipe: convidar e liberar loja por loja',
  'Convidar por e-mail, liberar loja a loja, leitura contra escrita, e quem pode conectar loja nova.',
  ['equipe', 'permissao']),
 (14, 'Crescer', 'Plano, limites e onde pedir ajuda',
  'O que o seu plano cobre, onde ficam os limites e por onde pedir ajuda quando travar.',
  ['plano', 'suporte']),
]

# Apoio: entram no fim da playlist, sem renomear. Vídeo de terceiro a gente não
# edita; o nosso a gente padroniza só a descrição, mantendo o título original.
RECURSOS = [
 {'video_id': 'IIKA4VkXCoM',
  'titulo': 'Claude MCP: Como Integrar o Claude Com Qualquer Coisa',
  'autor': 'André Arcas',
  'dura': '8m47',
  'nota': 'Vídeo de terceiro, público. Entra no fim da trilha como apoio para quem '
          'quer entender MCP por fora do nosso produto. Não dá para renomear nem tirar '
          'o CTA do autor, e some da trilha se ele apagar ou tornar privado — conferir '
          'de vez em quando.'},
 {'video_id': '-sjtfEfCekY',
  'titulo': 'Como integrar sistema com Marketplace Connect | Vibe Coding',
  'autor': 'Itamar Rocha',
  'dura': '4m58',
  'nota': 'Nosso, não listado. Público é dev, não lojista — por isso entra como apoio '
          'e não como aula numerada, e o título fica como está. Faz par com o guia de '
          'integração (REST + MCP): ' + GUIA},
]

CAMINHO = os.path.expanduser('~/midia-tmp/manifesto-trilha-basica.json')
ESPELHO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', '..', 'output', 'trilha-basica', 'manifesto-trilha-basica.json')

antigo = {}
if os.path.exists(CAMINHO):
    for a in json.load(open(CAMINHO, encoding='utf-8'))['aulas']:
        antigo[a['numero']] = a

aulas = []
for n, modulo, curto, resolve, extra in AULAS:
    a = antigo.get(n, {})
    aulas.append({
        'numero': n,
        'modulo': modulo,
        'titulo_curto': curto,
        'titulo': 'MC · Básico · Aula %02d — %s' % (n, curto),
        'descricao': resolve + '\n\nTrilha básica completa: ' + LINK,
        'tags': BASE + extra + ['aula %d' % n],
        'categoria': '27',
        'playlist': PL_B,
        'video_id_na_playlist': a.get('video_id_na_playlist'),
        'publicado_por_este_script': a.get('publicado_por_este_script', False),
        'status': a.get('status', 'voce grava'),
        'video_origem': a.get('video_origem'),
        'inicio': a.get('inicio'),
        'fim': a.get('fim'),
        'nota': a.get('nota', ''),
    })

m = {
    'gerado_em': '2026-10-13',
    'canal': 'UC4mEWT48J1erkqlbHqfHpEg',
    'playlists': {'basica': PL_B, 'avancada': PL_A, 'adocao': PL_ADOCAO},
    'regras': {
        'visibilidade': 'unlisted',
        'descricao_sem_sinal_de_maior_menor': 'o YouTube recusa < e > na descrição (invalidDescription)',
        'titulo': 'MC · Básico · Aula NN — <título curto>',
        'descricao': 'uma linha do que a aula resolve + link da playlist',
        'tags': 'marketplace connect, trilha basica, <tema>, aula <n>',
        'categoria': 'Educação (27)',
        'vinheta': 'nenhuma',
        'piso_disco_gb': 3,
    },
    'aulas': aulas,
    'abertura_adocao': 'KDjLvwLEbrQ',
    'recursos': RECURSOS,
    'guia_integracao': GUIA,
}
for destino in (CAMINHO, ESPELHO):
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
print('manifesto reescrito:', len(aulas), 'aulas')
