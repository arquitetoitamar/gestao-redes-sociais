#!/usr/bin/env python3
"""Base de empresas que podem vender em marketplace (público do Marketplace Connect).

Fonte: dados abertos de CNPJ da Receita Federal (estabelecimentos ativos). A Receita não tem código de
atividade para "vende pela internet", então o filtro é por tipo de produto: varejo, atacado e fabricação de
coisas que viram anúncio no Mercado Livre e na Shopee. Alimentos, combustível, farmácia e serviços ficam de fora.

  python3 segmenta.py [arquivo.parquet]   gera dados/base-alvo.parquet e resumo.md

Os dados ficam em dados/ (fora do git: são pesados e têm telefone/e-mail). Só o resumo agregado vai para o repo.
"""
import os
import sys
import duckdb

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, 'dados')
ORIGEM = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DADOS, 'estabelecimentos_hf_2026-03.parquet')

# nicho -> códigos CNAE (7 dígitos) ou prefixos de divisão (2 dígitos, para fabricantes)
NICHOS = {
    'Moda, calçados e acessórios': [4781400, 4782201, 4782202, 4783101, 4783102, 4789001, 4755502, 4755501,
                                    4642701, 4642702, 4643501, 4643502, 4616800],
    'Autopeças e motopeças': [4530703, 4530704, 4530705, 4530701, 4530702, 4541206, 4541207, 4541205, 4763603],
    'Casa, móveis e decoração': [4754701, 4754702, 4754703, 4755503, 4759899, 4759801, 4713002, 4713004, 4649499,
                                 4649408, 4649410, 4789002],
    'Eletrônicos, informática e celulares': [4751201, 4751202, 4752100, 4753900, 4757100, 4651601, 4651602, 4652400,
                                             4649401, 4649402],
    'Ferramentas e material elétrico': [4744001, 4742300, 4741500, 4744005, 4744099, 4663000, 4672900, 4673700],
    'Beleza e cosméticos': [4772500, 4646001, 4646002, 4618401],
    'Pet': [4789004, 4771704, 4623108, 4623109],
    'Brinquedos, esporte, papelaria e livros': [4763601, 4763602, 4763604, 4763605, 4761003, 4761001, 4761002,
                                                4647801, 4649406],
    'Óptica, saúde e bem-estar': [4774100, 4773300, 4645101, 4645102, 4645103],
    'Variedades e outros produtos': [4789099, 4789005, 4789007, 4789008, 4693100, 4686902, 4789003, 4789006],
}
FABRICANTES = ['13', '14', '15', '31', '32']   # têxtil, confecção, couro/calçados, móveis, produtos diversos


def main():
    c = duckdb.connect()
    c.execute(f"create view e as select * from '{ORIGEM}'")
    casos = []
    for nicho, cods in NICHOS.items():
        casos.append(f"when cod_cnae in ({','.join(map(str, cods))}) then '{nicho}'")
    pref = ' or '.join(f"lpad(cast(cod_cnae as varchar),7,'0') like '{p}%'" for p in FABRICANTES)
    casos.append(f"when {pref} then 'Fabricantes (roupa, calçado, móvel e outros)'")
    sql_nicho = 'case ' + ' '.join(casos) + ' end'
    alvo = os.path.join(DADOS, 'base-alvo.parquet')
    c.execute(f"""copy (select *, {sql_nicho} as nicho,
                   (email is not null and email like '%@%') as tem_email,
                   (length(coalesce(telefone_1,'')) >= 10) as tem_telefone
                 from e where {sql_nicho} is not null)
                 to '{alvo}' (format parquet, compression zstd)""")
    c.execute(f"create view a as select * from '{alvo}'")

    total = c.execute("select count(*) from e").fetchone()[0]
    n_alvo, n_mail, n_tel = c.execute("select count(*), sum(tem_email::int), sum(tem_telefone::int) from a").fetchone()
    por_nicho = c.execute("""select nicho, count(*) n, sum(tem_email::int), sum(tem_telefone::int)
                             from a group by 1 order by 2 desc""").fetchall()
    por_uf = c.execute("select estado, count(*) n from a group by 1 order by 2 desc limit 12").fetchall()
    por_porte = c.execute("select porte, count(*) from a group by 1 order by 2 desc").fetchall()
    cidades = c.execute("""select municipio || ' / ' || estado, count(*) n from a
                           group by 1 order by 2 desc limit 15""").fetchall()
    dominios = c.execute("""select lower(split_part(email,'@',2)) d, count(*) n from a where tem_email
                            group by 1 order by 2 desc limit 8""").fetchall()

    fmt = lambda x: f'{x:,}'.replace(',', '.')
    pct = lambda a, b: f'{100 * a / b:.0f}%'
    L = [f'# Base de empresas para o Marketplace Connect', '',
         f'Fonte: `{os.path.basename(ORIGEM)}` (Receita Federal, estabelecimentos ativos).', '',
         f'- Estabelecimentos ativos na fonte: **{fmt(total)}**',
         f'- Vendem produto de marketplace (alvo): **{fmt(n_alvo)}**',
         f'- Com e-mail cadastrado: {fmt(n_mail)} ({pct(n_mail, n_alvo)}) · com telefone: {fmt(n_tel)} ({pct(n_tel, n_alvo)})',
         '', '## Por nicho', '', '| Nicho | Empresas | Com e-mail | Com telefone |', '|---|---:|---:|---:|']
    L += [f'| {n} | {fmt(q)} | {pct(m, q)} | {pct(t, q)} |' for n, q, m, t in por_nicho]
    L += ['', '## Estados (top 12)', '', '| UF | Empresas |', '|---|---:|']
    L += [f'| {u} | {fmt(q)} |' for u, q in por_uf]
    L += ['', '## Cidades (top 15)', '', '| Cidade | Empresas |', '|---|---:|']
    L += [f'| {m} | {fmt(q)} |' for m, q in cidades]
    L += ['', '## Porte', '', '| Porte | Empresas |', '|---|---:|']
    L += [f'| {p} | {fmt(q)} |' for p, q in por_porte]
    L += ['', '## Domínio do e-mail cadastrado (top 8)', '',
          'Muitos e-mails da Receita são do escritório de contabilidade, não do dono.', '', '| Domínio | E-mails |', '|---|---:|']
    L += [f'| {d} | {fmt(q)} |' for d, q in dominios]
    open(os.path.join(AQUI, 'resumo.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
