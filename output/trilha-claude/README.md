# Trilha de Claude — treinamento geral

Separada da trilha do Marketplace Connect de propósito: esta ensina a
ferramenta, aquela ensina o produto. O único ponto de contato é o Módulo 5.

Playlist (não listada): https://www.youtube.com/playlist?list=PLRRzEvlO7GjU

## Os nove vídeos

Vieram da pasta TREINAMENTO CLAUDE no Drive, produzidos por Lucas H. e
guilhermeorugian. Os títulos saíram dos slides de abertura de cada um, não de
palpite.

| # | Módulo | Vídeo |
|---|---|---|
| 1 | 1 — Introdução ao Ecossistema Claude | `_BY6TBUj4go` |
| 2 | 2 — Chat: Conversação com Claude (1/2) | `5ttFkKZ-tGk` |
| 3 | 2 — Chat: Conversação com Claude (2/2) | `xREoW-hG4B8` |
| 4 | 3 — Cowork: Automação sem Código (1/2) | `57J7F4xjWxY` |
| 5 | 3 — Cowork: Automação sem Código (2/2) | `e1TizzV0cGU` |
| 6 | 4 — Skills: Criando Superpoderes (1/3) | `s8JCcyRAr0g` |
| 7 | 4 — Skills: Criando Superpoderes (2/3) | `i-nxK5Gjwqg` |
| 8 | 4 — Skills: Criando Superpoderes (3/3) | `c4JQo8l4YS0` |
| 9 | 5 — Conectores: MCP e Integrações | `05_PDmdk6DA` |

## O que foi feito com o material bruto

**Áudio nivelado.** Os originais vinham entre −32,7 e −37,2 LUFS, quando o
YouTube normaliza para −14. Na prática o aluno não escutava, subia o volume do
sistema no talo, e o próximo vídeo estourava. Havia ainda 4,5 dB de diferença
entre o módulo mais alto e o mais baixo, então o volume pulava a cada troca de
aula. Todos foram para −14 LUFS com `loudnorm`. **Só nível** — sem denoise, sem
EQ, sem música.

**Capa própria** em cada um, no padrão escuro, com número do módulo, título e
a parte quando o módulo é dividido. Antes a capa era o primeiro quadro, que
costuma ser tela preta ou slide ilegível no tamanho da grade.

**Material de apoio** na descrição dos nove: o kit de skills.

## Kit de skills

https://drive.google.com/drive/folders/1mRnzxFIWPibvLqTBCO6xiZIG6J5cxGac

Escrito do zero, em `kit-skills/`: template comentado e três exemplos que
funcionam — resumo de reunião, revisor de texto e planilha para Markdown.

**Nada saiu de `~/.claude/skills/`.** Aquela pasta tem skill de produção com
nome de segredo da AWS, id de instância e endpoint interno; publicar seria
vazamento. Os exemplos aqui são genéricos e não tocam em sistema nenhum.

## A ponte com a outra trilha

O Módulo 5 é o único vídeo que serve às duas: ensina conector MCP no Claude, que
é o mesmo mecanismo da Aula 07 do Marketplace Connect. A descrição dele aponta
para as duas playlists.

## Lacunas

Três pastas do Drive estão vazias: **Modulo Claude Code**, **Modulo Plugins** e
**Modulo Claude Design**. Se era para ter vídeo ali, o arquivo não está no
Drive.
