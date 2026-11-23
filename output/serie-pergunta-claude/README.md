# Série "Pergunta pro Claude" — motor e episódios

- `episodios/NN-slug.json`: dados do episódio (paleta, narração no padrão, cenas, legenda, Short). Exemplos completos: `01-visita-sem-venda.json`, `02-reposicao-full.json`.
- `python3 motor/gera.py episodios/NN.json` → `ep-NN-slug/videos/ep-NN.mp4`, `legenda_ig.md`, `trab/folha.jpg` (1 quadro por cena para conferir).
  Saída 3 = HeyGen sem saldo/erro de voz · 4 = narração fora do padrão de âncoras · 5 = duração fora de 25-60 s.
- `python3 motor/publica.py episodios/NN.json` → Reel no IG (agendador AWS) e Short no YouTube (privado com publishAt), mesmo horário; grava `ep-NN-slug/publicado.json` com prévia e como cancelar.
- Tarefa diária `serie-pergunta-claude-diaria` (10h): pega os episódios do dia na pauta (até 3: 16h, 18h, 20h), gera, confere, agenda cada um no horário da linha (campo `hora` do JSON) e manda uma prévia só no WhatsApp do Itamar. Autorização do Itamar em 23/11/2026: "Programe para todo dia gerar o criativo e postar" e "Sim quero 3 postagem por dia".

Padrão da narração (âncoras): gancho → "Faz assim." → "Primeiro:" "Segundo:" "Terceiro:" "Quarto:" → "Agora, fazer essa conta em <N> anúncios..." →
"Eu pergunto pro Claude, ligado no ... pelo Marketplace Connect:" <pergunta?> → "Ele ..." → "Comenta CONNECT que eu te mando o link no direct."
