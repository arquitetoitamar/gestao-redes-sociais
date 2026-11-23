# Reel Chatiops + Claude (23/11/2026)

Pedido do Itamar: vídeo no formato do Reel DexEa_cOnsb (@igao.ia, "O Claude agora atende seu WhatsApp", sobre Kapso), trocando por Chatiops + Claude, fundo branco.
Feito com a MESMA ESTRUTURA (gancho → o que é → como liga → 3 etapas → resultado → CTA), mas texto, cenas e visual nossos (cores do Chatiops); nada copiado do vídeo original.

Status: STORYBOARD (tempos estimados). Falta a narração HeyGen (voz c463ef5b, ~US$ 0,14) — aguardando o Itamar recarregar a HeyGen.

Fatos conferidos (chatiops.com, chatiops.com/mcp e conector MCP do Chatiops):
- Servidor MCP com 96 ferramentas, URL `https://api.chatiops.tiops.com.br/mcp?token=...`, sem instalar nada; Claude Desktop/Code, ChatGPT, Cursor.
- Confirmado pela sessão DEV ATEND no código e no banco (23/11): pelo MCP o Claude cria filas com saudação e chatbot (create_queue, create_queue_option), agentes e configura a IA (configure_ai), dispara campanhas em massa (sem data) e lista tickets. NÃO agenda mensagens pelo MCP (só na tela web) → tirado do roteiro.
- A IA do atendente roda na chave da OpenAI do cliente (paga à parte) → o vídeo NÃO diz que "o Claude atende"; diz que o Claude MONTA e OPERA o atendimento. Aviso na tela.
- Conexão padrão por QR Code (Baileys); também suporta a API oficial (Meta Cloud API, exige conta WABA). Enquadramento: "conecta por QR Code em segundos; também aceita a API oficial".
- Starter R$ 29,90 com 90 dias grátis (trial permanente do plano, não promoção com prazo). Cadastro em chatiops.tiops.com.br — link do direct a confirmar com o Itamar.

Gerar: `node ../../.agents/skills/media-use/audio/scripts/heygen-tts.mjs ./narracao.txt -o trab/voz.wav --words trab/voz.words.json --voice c463ef5bf11146d49bf754fa1e515401`,
depois `python3 cronograma.py` (passa a usar os tempos reais), `python3 motion.py todos 4`, áudio e montagem como em `../reel-pergunta-claude-02/`.
CTA "Comenta WHATSAPP": criar automação no ManyChat antes de postar (link do Starter 90 dias).
