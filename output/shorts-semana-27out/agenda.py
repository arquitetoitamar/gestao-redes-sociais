#!/usr/bin/env python3
"""Agenda dos Shorts de 27/10 a 02/11 — 2 por dia, manhã e tarde.

Manhã é produto (Marketplace Connect), tarde é a Imersão de 24/10.
Os cortes do condomínio saíram a pedido do Itamar e ficam de reserva.

Horários em Brasília (UTC-3); `sobe.py` converte para UTC no publishAt.
"""
import os

DL = os.path.expanduser('~/Downloads')
AV = os.path.join(DL, 'avatar-itamar-marketplace-connect')
AQUI = os.path.dirname(os.path.abspath(__file__))

NEG = ['marketplace', 'inteligencia artificial', 'mercado livre', 'shopee',
       'ia para vendedores', 'automacao', 'ecommerce', 'vender online',
       'marketplace connect', 'tiops']
IME = ['imersao', 'inteligencia artificial', 'agentes de ia', 'marketplace',
       'mercado livre', 'tiktok shop', 'ecommerce', 'automacao',
       'marketplace connect', 'tiops']

RODAPE = '\n\nSaiba mais: marketplaces.tiops.com.br\n\n#Shorts'
IMERSAO = ('\n\nGravado na Imersao de IA para Marketplaces, 24/10 — o encontro '
           'em que os vendedores conectaram as proprias contas de marketplace '
           'a inteligencia artificial pelo Marketplace Connect.')

AGENDA = [
 ('2026-10-27', '08:00', os.path.join(DL, 'ugcmarketplaceconnect novo.mp4'),
  '12 precos atualizados em 8 segundos 🤖',
  'A IA conectada direto na sua conta de marketplace: le, calcula e '
  'atualiza o preco. Sem planilha, sem extensao.' + RODAPE, NEG),

 ('2026-10-27', '18:00', os.path.join(AQUI, 'agente-plataforma.mp4'),
  'Nao foque numa plataforma de agente de IA',
  'O que importa no agente e o contexto, a memoria e o braco que ele tem — '
  'nao a plataforma da moda.' + IMERSAO + RODAPE, IME),

 ('2026-10-28', '08:00', os.path.join(DL, 'final_com_legendas.mp4'),
  'Vende em marketplace e nao sabe por onde comecar na IA?',
  'Tem muita gente vendendo prompt por ai. O caminho e outro: conectar '
  'suas contas de marketplace a inteligencia artificial.' + RODAPE, NEG),

 ('2026-10-28', '18:00', os.path.join(AQUI, 'perdido-youtube.mp4'),
  'Eu sabia que a IA ajudava, mas me perdia',
  'Muita informacao, denso demais, tudo misturado no YouTube. A fala de '
  'um vendedor que saiu desse ponto.' + IMERSAO + RODAPE, IME),

 ('2026-10-29', '08:00', os.path.join(DL, 'ia_favorita_broll_final.mp4'),
  'Troquei de IA e nao precisei reconfigurar nada',
  'Claude, ChatGPT ou Codex: a conexao com o marketplace e a mesma. '
  'Voce escolhe o agente.' + RODAPE, NEG),

 ('2026-10-29', '18:00', os.path.join(AQUI, 'cerebro.mp4'),
  'Conectei na conta dele e travou meu computador',
  'Gerei o cerebro da operacao de um participante ao vivo — e era tanta '
  'coisa que a maquina bugou.' + IMERSAO + RODAPE, IME),

 ('2026-10-30', '08:00', os.path.join(DL, 'tiktokshop_ia_final.mp4'),
  'Qual foi a margem liquida desse pedido? 📊',
  'Receita, taxa e frete na hora, no TikTok Shop, Mercado Livre, Shopee '
  'e Magalu.' + RODAPE, NEG),

 ('2026-10-30', '18:00', os.path.join(AQUI, 'substituir.mp4'),
  'Achei que a IA ia substituir todos os meus colaboradores',
  'Depois ele descobriu que a ideia nao e essa: e dar ferramenta pra '
  'equipe trazer resultado.' + IMERSAO + RODAPE, IME),

 ('2026-10-31', '08:00', os.path.join(AV, 'clipe1_hook_invertido.mp4'),
  'Anos de automacao viraram uma ferramenta',
  'Passei anos construindo automacao para marketplace. Isso virou uma '
  'plataforma que democratiza IA para o vendedor comum.' + RODAPE, NEG),

 ('2026-10-31', '18:00', os.path.join(AQUI, 'estampa.mp4'),
  'Foto tirada na rua vira estampa pronta em 2 minutos',
  'A IA le o padrao de uma foto ruim de anuncio e devolve a arte sem '
  'costura e sem emenda, pronta pra impressao.' + IMERSAO + RODAPE, IME),

 ('2026-11-01', '08:00', os.path.join(AV, 'clipe2_fechamento_invertido.mp4'),
  'Vende online e ainda nao usa IA de verdade?',
  'Quem nao colocou inteligencia artificial no dia a dia da operacao '
  'esta ficando para tras.' + RODAPE, NEG),

 ('2026-11-01', '18:00', os.path.join(AQUI, 'ferramenta-nova.mp4'),
  'Todo dia sai uma ferramenta nova de IA',
  'Nao da pra apostar numa tecnologia que vai morrer. O que fica e '
  'entender como o agente funciona por baixo.' + IMERSAO + RODAPE, IME),

 ('2026-11-02', '08:00', os.path.join(DL, 'versiculo_final.mp4'),
  'Proverbios 1:1-2 📖',
  'Para conhecer a sabedoria e a instrucao.\n\n#Shorts',
  ['versiculo', 'proverbios', 'fe', 'devocional', 'biblia']),

 ('2026-11-02', '18:00', os.path.join(AQUI, 'tiktok-estoque.mp4'),
  'TikTok e o melhor lugar pra acabar com estoque parado',
  'Estoque que nao sai no Mercado Livre nem na Shopee, no TikTok voce '
  'queima em um dia.' + IMERSAO + RODAPE, IME),
]

# Rendem Short mas ficaram fora desta semana:
#   condominio, parcelas, solucao, empresarios, moveis-ia, canal, ostentar,
#   remoto  -> cortes do condominio, o Itamar pediu para nao postar
#   ugcmarketplaceconnect.mp4 -> quase igual ao "novo"


def confere():
    for dia, hora, arq, titulo, desc, tags in AGENDA:
        assert os.path.exists(arq), 'arquivo sumiu: %s' % arq
        assert len(titulo) <= 100, 'titulo > 100: %s' % titulo
        assert '<' not in desc and '>' not in desc, 'YouTube recusa < e >'
        # o YouTube poe aspas em tag com espaco, custando 2 caracteres a mais
        custo = sum(len(t) + (2 if ' ' in t else 0) for t in tags) + len(tags) - 1
        assert custo <= 500, 'tags > 500: %d em %s' % (custo, titulo)
        assert 'condominio' not in arq, 'corte do condominio nao vai ao ar'
    assert len(AGENDA) == 14, 'faltou slot'
    return True


if __name__ == '__main__':
    confere()
    for dia, hora, arq, titulo, *_ in AGENDA:
        print('%s %s  %-34s %s' % (dia, hora, os.path.basename(arq)[:34], titulo))
