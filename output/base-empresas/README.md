# Base de empresas que podem vender em marketplace

Pedido do Itamar em 04/11/2026: "encontra tudo, monte a base de dados público e vamos fazer campanhas para
encontrar todas as empresas".

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `segmenta.py` | Classifica estabelecimentos ativos por nicho de produto de marketplace e gera `resumo.md` |
| `monta_receita.py` | Monta a base atual, com MEI, direto dos dados abertos da Receita (um arquivo por vez, sem guardar o bruto) |
| `resumo.md` | Números agregados (sem contato de ninguém) |
| `dados/` | Parquets com telefone e e-mail. **Fora do git** (`.gitignore`): pesados e com dado pessoal |

Fontes:

- Receita Federal, dados abertos de CNPJ: `arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9`, mês 2026-10.
- Versão pronta sem MEI (março/2026), do projeto `fabiofachini/receita-federal` no Hugging Face (`fabiofachini/receitafederal`).

```bash
python3 monta_receita.py 2026-10                      # ~8 GB de download, pico de disco ~1 GB
python3 segmenta.py dados/receita-2026-10-alvo.parquet
```

## Limites

- A Receita não tem código de atividade para "vende pela internet". O filtro é por tipo de produto, então a
  base mistura sellers e lojas só físicas.
- Muitos e-mails cadastrados são do contador, não do dono.

## Como usar (e como não usar)

**Usar para:**

- medir o mercado por nicho, estado e cidade;
- escolher nicho e região dos anúncios e do conteúdo;
- prospecção pequena, um a um, com opção de sair.

**Não usar para:**

- disparo em massa por WhatsApp: derruba os números do Chatiops;
- disparo em massa por e-mail: o Resend proíbe lista comprada ou raspada e queima o domínio `tiops.com.br`;
- subir a lista como público personalizado no Meta: os termos exigem consentimento das pessoas na lista.

Telefone e e-mail de MEI e de pequena empresa são dado pessoal (LGPD).

**Alcance pago:** no Meta, usar públicos semelhantes, sem lista:

| Público | ID | Criado em |
|---|---|---|
| LAL 1% clientes do Connect | `120254244919600007` | set/2026 |
| Engajaram com @tiopstecnologia 365d | `120255079746430007` | 04/11 |
| LAL 1% desse público de engajamento | `120255079748090007` | 04/11 |
