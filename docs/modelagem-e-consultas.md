# Modelagem e consultas analíticas

## Ambiente

Databricks, catálogo `workspace`, schema `operational_intelligence`. Os arquivos são enviados a um volume do Unity Catalog e carregados com `read_files`.

## Preparação dos arquivos

```bash
python -m src.preparar_databricks
```

Gera em `data/processed/databricks/`: `bronze_solicitacoes.csv`, `solicitacoes_tratadas.csv`, `solicitacoes_quarentena.csv` e `catalogo_tipos.csv`, em CSV padrão (vírgula, ponto decimal, UTF-8).

## Camadas

| Objeto | Tipo | Origem |
|---|---|---|
| bronze_solicitacoes | Tabela | Base bruta (8.120) |
| silver_solicitacoes | Tabela | Base tratada com campos derivados (7.888) |
| silver_quarentena | Tabela | Registros separados, com o motivo (232) |
| dim_tipo_solicitacao | Tabela | Catálogo de tipos e SLAs |
| vw_fato_solicitacoes | Visão | Silver com `situacao` e `mes_abertura` |

## Ordem de execução

1. `sql/01_criar_estrutura.sql`
2. Envio dos 4 CSVs ao volume `arquivos`
3. `sql/02_carregar_tabelas.sql`
4. `sql/03_modelo_analitico.sql`
5. `sql/consultas/01` a `07`

## Perguntas e consultas

| Pergunta | Consulta |
|---|---|
| Qual departamento possui mais solicitações atrasadas? | 01_departamento_com_mais_atrasos |
| Qual é o percentual de cumprimento dos SLAs? | 02_cumprimento_de_sla |
| Qual é o tempo médio de atendimento? | 03_tempo_medio_de_atendimento |
| Quais tipos apresentam mais gargalos? | 04_tipos_com_mais_gargalos |
| Quantas solicitações estão pendentes? | 05_solicitacoes_pendentes |
| Existem registros duplicados? | 06_registros_duplicados |
| Qual foi a evolução nos últimos meses? | 07_evolucao_mensal |

## Definições

- Atrasada: concluída fora do prazo ou pendente com data limite vencida na data de referência.
- Cancelada fica fora dos indicadores de atraso.
- SLA e tempo médio consideram apenas solicitações concluídas.
- A consulta de duplicidade roda sobre a camada bronze, antes do tratamento.

## Validação

As consultas são testadas no DuckDB (`tests/test_consultas_sql.py`) contra o Pandas. O SQL usa um subconjunto compatível com Databricks, mas os scripts de carga dependem do ambiente e são executados manualmente.

## Limitações conhecidas

- Os pendentes consideram apenas a base tratada. Registros com status inconsistente ficam na quarentena e não entram na contagem.
- O último mês da base é parcial (até 25/11), então a variação mensal dele não indica queda real.