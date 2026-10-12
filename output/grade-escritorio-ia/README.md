# Grade do escritório de agentes — Instagram · 12/10/2026

Arte 3×2 do Itamar, fatiada em 6 quadros de 1080×1080 e publicada em
@tiopstecnologia **do 6 para o 1**, porque o perfil empilha de trás pra frente:
o último publicado fica no canto superior esquerdo e a grade lê 1-2-3 / 4-5-6.

As células da arte original (1536×1024) já eram quadradas — 512×512 cada — então
o corte saiu limpo, sem tarja preta e sem perder texto.

| Quadro | Função | Post |
|---|---|---|
| 1 | Pesquisa e oportunidades | https://www.instagram.com/p/DeZP05ulWAO/ |
| 2 | Criação de anúncios | https://www.instagram.com/p/DeZPwYeFShS/ |
| 3 | Atendimento e pós-venda | https://www.instagram.com/p/DeZPrUklQLH/ |
| 4 | Análise e rentabilidade | https://www.instagram.com/p/DeZPmL5FY_R/ |
| 5 | Operação e logística | https://www.instagram.com/p/DeZPhAqFU00/ |
| 6 | Planejamento e crescimento | https://www.instagram.com/p/DeZPb6BlQ61/ |

Cada legenda abre com a dor concreta daquela função, não com o nome dela — é o
padrão que separa 45 mil de 169 views nas contas do Itamar. As hashtags foram no
primeiro comentário de cada um. O quadro 1, último a sair, carrega o fecho da
sequência e o "Saiba mais".

## Decisões registradas

- **Os seis saíram juntos**, contra a regra de espaçar 24-48 h. Grade só funciona
  completa: com um quadro faltando o perfil mostra um buraco. Foi escolha do
  Itamar ("organizar post tudo").
- **Receita e lucro no quadro 4 ficaram visíveis.** As regras de publicação dizem
  para não mostrar faturamento nem lucro; o Itamar liberou explicitamente para
  esta arte ("não se preocupe com o faturamento e lucro"). São números de
  ilustração, não de conta real.

## Para refazer com outra arte

```bash
python3 fatiar.py <arte_3x2.png>
```

Gera os 6 JPG. Depois publicar na ordem inversa — sempre do último quadro para o
primeiro.
