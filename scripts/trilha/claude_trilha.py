#!/usr/bin/env python3
"""Traz a pasta TREINAMENTO CLAUDE do Drive para o YouTube, não listado.

    python3 claude_trilha.py --listar      mostra o plano, não mexe em nada
    python3 claude_trilha.py --baixar      baixa os vídeos que faltam
    python3 claude_trilha.py --subir       sobe os já baixados e monta a playlist

Nunca sobe sem passar pelo baixar: a conferência visual acontece entre os dois.
"""
import json, os, subprocess, sys, unicodedata

import drive, yt

RAIZ = '1mUfVNY2nlZUT8_cscCxl0ppIR9pFOXMP'
AREA = os.path.expanduser('~/midia-tmp/claude')
ESTADO = os.path.expanduser('~/midia-tmp/trilha-claude.json')
PISO_GB = 3

# ordem didática, não a do Drive: nome do arquivo -> (número, título curto, tema)
PLANO = [
 ('Introdução ao Claude AI.mp4',  1, 'Módulo 1 — Introdução ao Ecossistema Claude',
  ['introducao', 'ecossistema']),
 ('Video_Final_Chat_1.mp4',       2, 'Módulo 2 — Chat: Conversação com Claude (1/2)',
  ['chat', 'conversacao']),
 ('Video_Final_Chat_2.mp4',       3, 'Módulo 2 — Chat: Conversação com Claude (2/2)',
  ['chat', 'projetos']),
 ('Video_Final_3_Cowork_1.mp4',   4, 'Módulo 3 — Cowork: Automação sem Código (1/2)',
  ['cowork', 'automacao']),
 ('Video_Final_3_Cowork_2.mp4',   5, 'Módulo 3 — Cowork: Automação sem Código (2/2)',
  ['cowork', 'agendamento']),
 ('Video_Final_Skills_1.mp4',     6, 'Módulo 4 — Skills: Criando Superpoderes (1/3)',
  ['skills']),
 ('Video_Final_Skills_2.mp4',     7, 'Módulo 4 — Skills: Criando Superpoderes (2/3)',
  ['skills']),
 ('Video_Final_Skills_3.mp4',     8, 'Módulo 4 — Skills: Criando Superpoderes (3/3)',
  ['skills', 'template']),
 ('Conectores MCP no claude.mov', 9, 'Módulo 5 — Conectores: MCP e Integrações',
  ['mcp', 'conector', 'integracoes']),
]
PONTE = 'Conectores MCP no claude.mov'   # entra também na trilha do Marketplace Connect


def titulo(n, curto):
    return 'Claude · ' + curto


def descricao(n, curto, link_playlist):
    kit = 'https://drive.google.com/drive/folders/1mRnzxFIWPibvLqTBCO6xiZIG6J5cxGac'
    recursos = ('\n\nMATERIAL DE APOIO\n'
                'Kit de skills — template comentado e três exemplos prontos para instalar:\n'
                + kit)
    if n == 9:
        corpo = ('Como ligar um conector MCP no Claude. É a ponte entre este treinamento e a '
                 'trilha do Marketplace Connect: o mecanismo é o mesmo, muda o que você conecta.'
                 '\n\nTrilha de Claude: ' + link_playlist +
                 '\nTrilha do Marketplace Connect: '
                 'https://www.youtube.com/playlist?list=PLW3upCIZHed4')
    else:
        corpo = ('Treinamento de Claude — formação geral na ferramenta, independente do '
                 'Marketplace Connect.\n\nTrilha completa: ' + link_playlist)
    return corpo + recursos


def estado():
    return json.load(open(ESTADO)) if os.path.exists(ESTADO) else {}


def salva(e):
    json.dump(e, open(ESTADO, 'w'), ensure_ascii=False, indent=2)


def espaco_gb():
    s = os.statvfs(os.path.expanduser('~'))
    return s.f_bavail * s.f_frsize / 1e9


def _chave(nome):
    """macOS guarda acento em NFD e o Drive devolve NFC — normaliza os dois."""
    return unicodedata.normalize('NFC', nome)


def arquivos_do_drive():
    mapa = {}
    for caminho, f in drive.arvore(RAIZ):
        if f['mimeType'].startswith('video'):
            mapa[_chave(os.path.basename(caminho))] = f
    return mapa


def baixar():
    os.makedirs(AREA, exist_ok=True)
    mapa = arquivos_do_drive()
    e = estado()
    for nome, n, curto, _ in PLANO:
        destino = os.path.join(AREA, '%02d_%s' % (n, nome))
        if os.path.exists(destino):
            print('  já tenho  %s' % os.path.basename(destino))
            continue
        if espaco_gb() < PISO_GB:
            sys.exit('disco abaixo de %d GB — parando' % PISO_GB)
        f = mapa.get(_chave(nome))
        if not f:
            print('  FALTA no Drive:', nome)
            continue
        print('  baixando  %-44s %6.1f MB' % (nome[:44], int(f.get('size', 0)) / 1e6))
        drive.baixar(f['id'], destino)
        e.setdefault(nome, {}).update({'numero': n, 'arquivo': destino,
                                       'drive_id': f['id'],
                                       'dono': f['owners'][0]['emailAddress']})
        salva(e)
    print('\nbaixados em', AREA)


def contato(caminho, saida):
    subprocess.run(['ffmpeg', '-v', 'error', '-i', caminho, '-vf',
                    'fps=1/12,scale=560:-1,tile=5x4', '-frames:v', '1', saida, '-y'],
                   check=False)


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else '--listar'
    if arg == '--listar':
        mapa = arquivos_do_drive()
        print('%-44s %6s  %s' % ('arquivo', 'MB', 'vira'))
        for nome, n, curto, _ in PLANO:
            f = mapa.get(_chave(nome))
            mb = int(f.get('size', 0)) / 1e6 if f else 0
            print('%-44s %6.1f  %s' % (nome[:44], mb, titulo(n, curto)))
    elif arg == '--baixar':
        baixar()
    elif arg == '--contato':
        for nome, n, curto, _ in PLANO:
            p = os.path.join(AREA, '%02d_%s' % (n, nome))
            if os.path.exists(p):
                s = os.path.join(AREA, 'contato_%02d.jpg' % n)
                contato(p, s)
                print('  ', s)
    else:
        sys.exit(__doc__)
