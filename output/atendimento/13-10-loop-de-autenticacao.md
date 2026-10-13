# 13/10/2026 — três pessoas travadas no mesmo ponto

Apareceu o mesmo sintoma em três canais no mesmo dia. Não é coincidência.

| Quem | Onde | Quando | O que disse |
|---|---|---|---|
| @alexandremiranda7376 | YouTube | 3 dias | loop na autenticação + `Failed to create authorization grant` |
| Frido Benner Junior | Instagram (aba Geral) | hoje 11:11 | "não estou conseguindo adquirir seu curso" |
| Nipônica Design | Instagram (aba Geral) | 04/10 | "onde se inscreve não consegui me conectar" |

O comentário do YouTube é o único que descreve o mecanismo:

> O Claude abre o Chrome e pede para eu autorizar. A Tiops solicita meu e-mail e
> envia um link de acesso. Quando clico no link, em vez de concluir a
> autorização, ele volta para a tela que pede meu e-mail novamente.

## Causa, pela skill `conectar-mcp`

É o primeiro dos quatro modos de falha conhecidos: **a página de autorização não
encontra a sessão.** Em produção o modo é Cognito e a sessão vive em
`localStorage['mc_cognito_sessao']`, não em `supabase.auth`. Sem sessão, não há
grant — e o `Failed to create authorization grant` é consequência, não causa.

Diagnóstico no navegador do cliente:

```js
Object.keys(localStorage).filter(k => k.includes('cognito') || k.startsWith('sb-'))
```

Vazio nos dois: ele não está logado. A saída é entrar antes em
`marketplaces.tiops.com.br`, no mesmo navegador, e só então autorizar.

## O que respondi

Ao Alexandre, o passo a passo acima mais a recomendação de conectar
`/mcp/meli` em vez da raiz. Ao Frido e à Nipônica, pedi o print da tela onde
travaram, porque ainda não dá para afirmar que é o mesmo caso.

## O que isso sugere

Se o fluxo depende de o cliente já estar logado no site antes de mandar o
cliente de IA autorizar, e nada na tela diz isso, então não é um erro de três
pessoas — é o desenho do fluxo. A página de consentimento deveria mandar para o
login e voltar sozinha, em vez de repetir o pedido de e-mail.

Vale medir quantas autorizações começam e quantas terminam antes de tratar isso
como caso isolado.
