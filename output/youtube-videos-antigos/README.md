# Vídeos antigos marcados no YouTube (09/11/2026)

Pedido do Itamar: avisar quem chega nos vídeos antigos que já existe versão nova.

- **O que mudou**: primeira linha da descrição de 32 vídeos públicos de abr a ago/2026
  (IA, marketplace, GestorPro, Chatiops, Claude):
  `⚠️ Vídeo de <mês>/2026, versão antiga. Veja o que mudou: https://youtu.be/e5RfKvZPLL4`
- **Título e tags intactos**, de propósito: entre eles estão os 3 maiores do canal
  (IiPvKDJ0gMo 67 mil, gARgaonZkj8 31 mil, WvLiFFl5pAE 18 mil views) e mexer no título
  derruba clique enquanto o canal ainda busca as 4.000 h de exibição.
- **Link de destino**: live de 02/11 "IA para Marketplace em 2026" (e5RfKvZPLL4). Quando a
  regravação do live de 02/11 subir, dá para trocar o link nos 32 de uma vez.
- **Backup**: `originais.json` tem título, descrição e tags de antes. Para desfazer, regravar a
  descrição de cada id com o valor do backup (`videos.update`, `part=snippet`, reenviando
  título, tags e categoryId).
- Scripts: `listar.py` (lista o canal) e `marcar.py dry|apply <backup> [ids]` (idempotente:
  pula quem já tem o aviso).
