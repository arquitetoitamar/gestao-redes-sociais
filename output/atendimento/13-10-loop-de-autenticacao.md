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

## Causa — corrigida pelo Itamar em 13/10

**O método de login mudou: agora é por código, não mais por link de acesso.**
Quem tentou no método antigo ficou com cache velho no navegador, e é esse cache
que produz o loop. O `Failed to create authorization grant` vem depois, como
consequência.

**A saída é limpar o cache e os dados do site de `marketplaces.tiops.com.br`**
(ou abrir uma janela anônima), entrar de novo com o código e autorizar.

### O que eu tinha respondido antes, e estava errado

A skill `conectar-mcp` descrevia esse sintoma como sessão ausente e mandava o
cliente "logar antes no site". Era o diagnóstico do método anterior. Respondi o
Alexandre com isso, e em seguida publiquei a correção no mesmo comentário. A
skill foi atualizada em `~/.claude/skills/conectar-mcp/SKILL.md` para não
repetir o erro.

## Estado de cada um

| Quem | Estado |
|---|---|
| @alexandremiranda7376 | respondido e corrigido no YouTube |
| Frido Benner Junior | confirmou: "a hora de conectar a conta", com print da tela de e-mail. O Itamar entrou na conversa ao vivo às 19:46 |
| Nipônica Design | ainda sem retorno desde o pedido de print |

## O que fica

Três pessoas travaram na transição entre os dois métodos de login. Se o número
for maior do que esses três, vale um aviso no próprio site — a pessoa que pega
cache velho não tem como adivinhar que o problema é esse.
