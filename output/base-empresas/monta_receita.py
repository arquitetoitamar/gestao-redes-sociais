#!/usr/bin/env python3
"""Monta a base atual de empresas-alvo direto dos dados abertos de CNPJ da Receita Federal, com MEI.

Baixa um arquivo por vez do compartilhamento público da Receita, descompacta em fluxo (curl | tar -xO)
e o DuckDB lê do fluxo: nada bruto fica no disco. Guarda só estabelecimentos ATIVOS dos nichos de
segmenta.py, depois junta razão social/porte (Empresas) e a opção pelo MEI (Simples).

  python3 monta_receita.py [AAAA-MM]     gera dados/receita-AAAA-MM-alvo.parquet

Fonte: https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9 (dados abertos, sem login).
"""
import os
import subprocess
import sys
import tempfile
import time
import duckdb

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, 'dados')
sys.path.insert(0, AQUI)
from segmenta import NICHOS, FABRICANTES  # noqa: E402

TOKEN = 'YggdBLfdninEJX9'
DAV = 'https://arquivos.receitafederal.gov.br/public.php/webdav'
MES = sys.argv[1] if len(sys.argv) > 1 else '2026-10'
TMP = os.path.join(DADOS, f'tmp-{MES}')

COLS = {
    'estab': ['cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'matriz_filial', 'nome_fantasia', 'situacao', 'data_situacao',
              'motivo', 'cidade_exterior', 'pais', 'data_inicio', 'cnae_principal', 'cnae_secundaria', 'tipo_logradouro',
              'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf', 'municipio', 'ddd1', 'telefone1', 'ddd2',
              'telefone2', 'ddd_fax', 'fax', 'email', 'situacao_especial', 'data_situacao_especial'],
    'empresa': ['cnpj_basico', 'razao_social', 'natureza_juridica', 'qualificacao', 'capital_social', 'porte', 'ente'],
    'simples': ['cnpj_basico', 'opcao_simples', 'data_opcao_simples', 'data_exclusao_simples', 'opcao_mei',
                'data_opcao_mei', 'data_exclusao_mei'],
    'cod': ['codigo', 'descricao'],
}


def csv(fonte, cols):
    tipos = '{' + ', '.join(f"'{c}': 'VARCHAR'" for c in cols) + '}'
    return (f"read_csv('{fonte}', delim=';', quote='\"', header=false, columns={tipos}, "
            f"ignore_errors=true, parallel=false)")


def fluxo(nome):
    """Abre curl | tar -xO para um zip da Receita e devolve (fifo, processo)."""
    fifo = os.path.join(tempfile.mkdtemp(), 'f.csv')
    os.mkfifo(fifo)
    cmd = (f"curl -sfL --retry 5 --retry-delay 10 -u '{TOKEN}:' '{DAV}/{MES}/{nome}' "
           f"| tar -xOf - | iconv -f ISO-8859-1 -t UTF-8 | tr -d '\\000' > '{fifo}'")
    return fifo, subprocess.Popen(['bash', '-o', 'pipefail', '-c', cmd])


def etapa(c, nome, sql_fn, cols, saida):
    if os.path.exists(saida):
        print('já feito:', os.path.basename(saida), flush=True)
        return
    t = time.time()
    fifo, p = fluxo(nome)
    parcial = saida + '.parcial'
    c.execute(f"copy ({sql_fn(csv(fifo, cols))}) to '{parcial}' (format parquet, compression zstd)")
    if p.wait() != 0:
        raise SystemExit(f'falhou o download de {nome}')
    os.rename(parcial, saida)
    n = c.execute(f"select count(*) from '{saida}'").fetchone()[0]
    print(f'{nome}: {n:,} linhas em {time.time() - t:.0f}s', flush=True)


def main():
    os.makedirs(TMP, exist_ok=True)
    c = duckdb.connect()
    c.execute("set preserve_insertion_order=false")
    cods = sorted({str(x) for v in NICHOS.values() for x in v})
    filtro = (f"situacao = '02' and (cnae_principal in ({','.join(repr(x) for x in cods)}) or "
              + ' or '.join(f"cnae_principal like '{p}%'" for p in FABRICANTES) + ')')

    for i in range(10):
        etapa(c, f'Estabelecimentos{i}.zip', lambda src: f"select * from {src} where {filtro}",
              COLS['estab'], os.path.join(TMP, f'estab{i}.parquet'))
    alvo_ids = os.path.join(TMP, 'estab*.parquet')
    c.execute(f"create or replace temp table ids as select distinct cnpj_basico from '{alvo_ids}'")
    print('cnpj básicos no alvo:', c.execute('select count(*) from ids').fetchone()[0], flush=True)

    for i in range(10):
        etapa(c, f'Empresas{i}.zip', lambda src: f"select * from {src} semi join ids using (cnpj_basico)",
              COLS['empresa'], os.path.join(TMP, f'empresa{i}.parquet'))
    etapa(c, 'Simples.zip', lambda src: f"select * from {src} semi join ids using (cnpj_basico)",
          COLS['simples'], os.path.join(TMP, 'simples.parquet'))
    etapa(c, 'Cnaes.zip', lambda src: f"select * from {src}", COLS['cod'], os.path.join(TMP, 'cnaes.parquet'))
    etapa(c, 'Municipios.zip', lambda src: f"select * from {src}", COLS['cod'], os.path.join(TMP, 'municipios.parquet'))

    final = os.path.join(DADOS, f'receita-{MES}-alvo.parquet')
    c.execute(f"""copy (
      select e.cnpj_basico || e.cnpj_ordem || e.cnpj_dv as cnpj,
             emp.razao_social, e.nome_fantasia,
             case e.matriz_filial when '1' then 'matriz' when '2' then 'filial' else 'nao informado' end as matriz_filial,
             case when s.opcao_mei = 'S' then 'mei' when emp.porte = '01' then 'micro empresa'
                  when emp.porte = '03' then 'empresa de pequeno porte' when emp.porte = '05' then 'demais portes'
                  else 'nao informado' end as porte,
             try_cast(replace(emp.capital_social, ',', '.') as decimal(20,2)) as capital_social,
             e.uf as estado, m.descricao as municipio, e.bairro, e.cep,
             trim(coalesce(e.tipo_logradouro,'') || ' ' || coalesce(e.logradouro,'') || ', ' || coalesce(e.numero,'')) as endereco,
             cast(e.cnae_principal as integer) as cod_cnae, upper(cn.descricao) as cnae_principal,
             try_strptime(e.data_inicio, '%Y%m%d')::date as data_inicio,
             nullif(coalesce(e.ddd1,'') || coalesce(e.telefone1,''), '') as telefone_1,
             nullif(coalesce(e.ddd2,'') || coalesce(e.telefone2,''), '') as telefone_2,
             lower(nullif(trim(e.email), '')) as email
      from '{alvo_ids}' e
      left join '{os.path.join(TMP, 'empresa*.parquet')}' emp using (cnpj_basico)
      left join '{os.path.join(TMP, 'simples.parquet')}' s using (cnpj_basico)
      left join '{os.path.join(TMP, 'cnaes.parquet')}' cn on cn.codigo = e.cnae_principal
      left join '{os.path.join(TMP, 'municipios.parquet')}' m on m.codigo = e.municipio
    ) to '{final}' (format parquet, compression zstd)""")
    n, mei = c.execute(f"select count(*), count(*) filter (where porte = 'mei') from '{final}'").fetchone()
    print(f'PRONTO {final}: {n:,} estabelecimentos ativos no alvo, {mei:,} MEI', flush=True)


if __name__ == '__main__':
    main()
