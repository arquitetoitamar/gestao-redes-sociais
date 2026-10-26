#!/usr/bin/env python3
"""Agenda dos Shorts de 27/10 a 02/11 — 2 por dia, manhã e tarde.

Nada aqui sobe sozinho: `sobe.py` lê esta lista e só age quando chamado.
Manhã é negócio (Marketplace Connect / IA aplicada), tarde é história
pessoal (cortes do vlog da casa nova). Os dois do mesmo dia nunca falam
do mesmo assunto, pra um não comer o outro.
"""
import os

DL = os.path.expanduser('~/Downloads')
AV = os.path.join(DL, 'avatar-itamar-marketplace-connect')
CORTES = os.path.dirname(os.path.abspath(__file__))

TAGS_NEG = ['marketplace', 'inteligencia artificial', 'mercado livre',
            'shopee', 'ia para vendedores', 'automacao', 'ecommerce',
            'vender online', 'marketplace connect', 'tiops']
TAGS_PES = ['empreendedorismo', 'inteligencia artificial', 'trabalho remoto',
            'mudanca de vida', 'interior de sao paulo', 'tecnologia',
            'historia de vida', 'tiops']

# dia, hora, arquivo, titulo, descricao, tags
AGENDA = [
 ('2026-10-27', '08:00', os.path.join(DL, 'ugcmarketplaceconnect novo.mp4'),
  '12 precos atualizados em 8 segundos 🤖',
  'A IA conectada direto na sua conta de marketplace: ela le, calcula e '
  'atualiza o preco. Sem planilha, sem extensao.\n\nSaiba mais: '
  'marketplaces.tiops.com.br\n\n#Shorts', TAGS_NEG),

 ('2026-10-27', '18:00', os.path.join(CORTES, 'condominio.mp4'),
  'Eu perguntava como essas pessoas conseguiam 🏡',
  'Durante anos eu olhava esses condominios e nao entendia a conta. '
  'Hoje eu moro em um.\n\n#Shorts', TAGS_PES),

 ('2026-10-28', '08:00', os.path.join(DL, 'final_com_legendas.mp4'),
  'Vende em marketplace e nao sabe por onde comecar na IA?',
  'Tem muita gente vendendo prompt por ai. O caminho e outro: conectar '
  'suas contas de marketplace na inteligencia artificial.\n\n'
  'Saiba mais: marketplaces.tiops.com.br\n\n#Shorts', TAGS_NEG),

 ('2026-10-28', '18:00', os.path.join(CORTES, 'parcelas.mp4'),
  'Comprei a casa e ainda nao morei nela',
  'Paguei parcelas de uma casa que eu ainda nao habitava, pensando em '
  'ate onde a inteligencia artificial leva a gente.\n\n#Shorts', TAGS_PES),

 ('2026-10-29', '08:00', os.path.join(DL, 'ia_favorita_broll_final.mp4'),
  'Troquei de IA e nao precisei reconfigurar nada',
  'Claude, ChatGPT ou Codex: a conexao com o marketplace e a mesma. '
  'Voce escolhe o agente.\n\nSaiba mais: marketplaces.tiops.com.br\n\n'
  '#Shorts', TAGS_NEG),

 ('2026-10-29', '18:00', os.path.join(CORTES, 'solucao.mp4'),
  'Pare de olhar o problema',
  'Quando voce passa a trabalhar em solucoes em vez de ficar girando em '
  'volta do problema, o resultado aparece.\n\n#Shorts', TAGS_PES),

 ('2026-10-30', '08:00', os.path.join(DL, 'tiktokshop_ia_final.mp4'),
  'Qual foi a margem liquida desse pedido? 📊',
  'Receita, taxa e frete na hora, no TikTok Shop, Mercado Livre, Shopee '
  'e Magalu.\n\nSaiba mais: marketplaces.tiops.com.br\n\n#Shorts', TAGS_NEG),

 ('2026-10-30', '18:00', os.path.join(CORTES, 'empresarios.mp4'),
  'O que os donos de empresa realmente querem',
  'Conversando com empresarios no evento: eles estao dispostos a '
  'investir em quem traz solucao.\n\n#Shorts', TAGS_PES),

 ('2026-10-31', '08:00', os.path.join(AV, 'clipe1_hook_invertido.mp4'),
  'Anos de automacao viraram uma ferramenta',
  'Passei anos construindo automacao para marketplace. Isso virou uma '
  'plataforma que democratiza IA para o vendedor comum.\n\n'
  'Saiba mais: marketplaces.tiops.com.br\n\n#Shorts', TAGS_NEG),

 ('2026-10-31', '18:00', os.path.join(AV, 'clipe2_fechamento_invertido.mp4'),
  'Vende online e ainda nao usa IA de verdade?',
  'Quem nao colocou inteligencia artificial no dia a dia da operacao '
  'esta ficando para tras.\n\nSaiba mais: marketplaces.tiops.com.br\n\n'
  '#Shorts', TAGS_NEG),

 ('2026-11-01', '08:00', os.path.join(CORTES, 'moveis-ia.mp4'),
  'Usei IA ate para projetar os moveis da casa',
  'Nao e so no trabalho: usei inteligencia artificial para fazer os '
  'projetos dos moveis da casa nova.\n\n#Shorts', TAGS_PES),

 ('2026-11-01', '18:00', os.path.join(CORTES, 'canal.mp4'),
  'Nao sou do marketing digital, estou aprendendo',
  'Sou professor e arquiteto de solucoes. Fazer video e novo pra mim e '
  'o canal comecou a ter relevancia agora.\n\n#Shorts', TAGS_PES),

 ('2026-11-02', '08:00', os.path.join(DL, 'versiculo_final.mp4'),
  'Proverbios 1:1-2 📖',
  'Para conhecer a sabedoria e a instrucao.\n\n#Shorts',
  ['versiculo', 'proverbios', 'fe', 'devocional', 'biblia']),

 ('2026-11-02', '18:00', os.path.join(CORTES, 'ostentar.mp4'),
  'Nao e ostentacao',
  'Condominio simples, no interior. A gente paga para ter uma vida '
  'melhor — o que deveria ser o normal.\n\n#Shorts', TAGS_PES),
]


def confere():
    """Falha cedo se algum arquivo sumiu ou se um limite do YouTube estourou."""
    for dia, hora, arq, titulo, desc, tags in AGENDA:
        assert os.path.exists(arq), 'arquivo sumiu: %s' % arq
        assert len(titulo) <= 100, 'titulo > 100: %s' % titulo
        assert '<' not in desc and '>' not in desc, 'YouTube recusa < e >'
        # o YouTube poe aspas em tag com espaco, custando 2 caracteres a mais
        custo = sum(len(t) + (2 if ' ' in t else 0) for t in tags) + len(tags) - 1
        assert custo <= 500, 'tags > 500: %d em %s' % (custo, titulo)
    assert len(AGENDA) == 14, 'faltou slot'
    return True


if __name__ == '__main__':
    confere()
    for dia, hora, arq, titulo, *_ in AGENDA:
        print('%s %s  %-34s %s' % (dia, hora, os.path.basename(arq), titulo))
