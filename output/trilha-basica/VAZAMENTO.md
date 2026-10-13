# Achado em 13/10/2026 — credencial e ids de conta em vídeo público

Encontrado ao varrer por OCR os vídeos que entrariam na trilha básica. Nenhum
valor de credencial está escrito aqui de propósito.

## O grave

**`e6YZbIU3oK8` — "Como ativar o Marketplace connect", PÚBLICO desde 23/06.**

Por volta de **1:56** a tela mostra a URL do conector MCP inteira, com a chave
de produção (`mc_live_…`) legível e um botão "Copiar" ao lado. Quem pausar o
vídeo copia a chave.

Entre **1:12 e 1:50** o mesmo vídeo mostra quatro ids de conta (dois do Mercado
Livre, um da Shopee, mais um) e um identificador em UUID.

## O resto

| Vídeo | Estado | O que aparece | Quando |
|---|---|---|---|
| `f1t_OJZBrxg` | público | ids de conta (ML, Shopee) | 1:34 – 1:46 |
| `k1b8TMwiwg0` | público | id de conta do Mercado Livre | ~0:40 |
| `LtifaBOjLRQ` | não listado | nada encontrado | — |
| `oE3QT7Ze3VM` (aula 11) | não listado | nada — já mascarado | — |

## O que foi feito

- As cópias `O_AJyA9bOgE` (aula 4) e `usU38GZmJ8s` (aula 5) tinham acabado de
  subir para a trilha. Foram **retiradas da playlist e deixadas privadas** assim
  que o achado apareceu. Nenhuma das duas chegou a ficar acessível por link.
- **Nenhum vídeo público foi alterado.** Mudar visibilidade de peça pública é
  decisão do Itamar.

## O que falta — nesta ordem

1. **Girar a chave `mc_live_` que aparece no vídeo.** É o único passo que fecha
   o buraco de verdade: o vídeo está público há quase quatro meses, e tirar do
   ar agora não desfaz quem já copiou. Conferir também o log de uso dessa chave.
2. Decidir o que fazer com `e6YZbIU3oK8` enquanto isso — deixar não listado,
   privado, ou substituir pela versão mascarada.
3. Mascarar os três e republicar as cópias da trilha. O mesmo caminho da aula 11
   serve: OCR acha, `drawbox` tapa, OCR confere.
