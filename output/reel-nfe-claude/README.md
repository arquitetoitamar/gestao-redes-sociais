# Reel "emiti uma NF-e conversando com o Claude" (31/10/2026)

Gravação real no claude.ai com o conector **Nfe** (Emissor NF-e Tiops), em **homologação**:
pedido 2071 da loja virtual → prévia (`nfe_simular`) com alertas → "pode emitir" → NF-e nº 10 autorizada
(protocolo 135260009729169). Cliente e endereço de teste (Ana Souza, CPF-exemplo 111.444.777-35).
Conversa: https://claude.ai/chat/1fc613ab-f5df-4e61-9a90-3444c1623429

- `reel_nfe_claude.mp4` (fora do git): 36,8 s, voz clonada do Itamar (HeyGen), -14 LUFS.
- A chave de acesso (tem o CNPJ do emitente) é pixelada em `monta.py` (`Fonte.quadro`, quadros a partir de 164 s).
- Agendado na AWS para **31/10/2026 18:00** (`scripts/ig-agendado`, id `reel-nfe-claude-20261031`), legenda em `legenda.md`.

## Como foi gravado
1. Janela popup separada (`window.open` a partir de uma aba do Claude in Chrome) na tela retina do notebook,
   sem barra lateral (ela mostra os chats do Itamar).
2. `grava_janela.py <window_id> <seg> <pasta> 10` com `RETINA=1` captura só essa janela (CGWindowListCreateImage).
3. A digitação e o envio rodam por JS dentro do popup (`execCommand('insertText')`), sem o brilho da extensão.
4. O claude.ai **não rola sozinho** enquanto a resposta chega: a prévia foi regravada rolando a conversa pronta (`rolagem/`).
5. `python3 monta.py` monta tudo (títulos, legenda palavra a palavra, cartões finais, áudio).
