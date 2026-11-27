# Indicadores

## Como gerar

```bash
python -m src.gerar_indicadores
```

Saídas:

| Arquivo | Conteúdo |
|---|---|
| data/processed/indicadores/kpi_*.csv | Uma tabela por visão, em CSV padrão |
| reports/indicadores_operacionais.xlsx | As mesmas tabelas em abas, para Excel e dashboard |

No Databricks, as mesmas visões existem como views em `sql/04_camada_gold.sql`: `gold_kpi_geral`, `gold_kpi_departamento`, `gold_kpi_tipo`, `gold_kpi_mensal` e `gold_qualidade`. Os testes garantem que SQL e Python produzem os mesmos valores.

## Definições

| Indicador | Definição | Universo |
|---|---|---|
| solicitacoes | Contagem de registros da base tratada | Todas, incluindo canceladas |
| pct_sla | Concluídas dentro do prazo / concluídas | Concluídas |
| tempo_medio_horas | Média de conclusão menos abertura | Concluídas |
| pendentes | Abertas, em andamento e aguardando terceiros | Pendentes |
| pendentes_atrasadas | Pendentes com data limite vencida na referência | Pendentes |
| taxa_atraso | (Concluídas fora do prazo + pendentes atrasadas) / (concluídas + pendentes) | Concluídas e pendentes |
| posicao_gargalo | Posição do tipo pela taxa de atraso, do maior para o menor | Tipos |
| variacao_volume_pct | Variação do volume em relação ao mês anterior | Mensal |
| mes_parcial | Marca o último mês quando a base não o cobre por inteiro | Mensal |
| taxa_duplicidade_pct | Duplicatas / registros brutos | Base bruta |
| pct_quarentena | Registros em quarentena / registros brutos | Base bruta |

Canceladas ficam fora do SLA, do tempo médio e da taxa de atraso.

## Meta e status do SLA

| Status | Regra |
|---|---|
| Dentro da meta | SLA maior ou igual a 90% |
| Atenção | SLA de 80% a 89,9% |
| Crítico | SLA abaixo de 80% |

Os limites são parâmetros de negócio. Para alterá-los: `META_SLA` e `LIMITE_ATENCAO` em `src/indicadores.py` e os valores 90 e 80 em `sql/04_camada_gold.sql`.

## Limitações conhecidas

- Os indicadores consideram apenas a base tratada. Registros em quarentena não entram nas contagens e aparecem em `kpi_qualidade`.
- O último mês é parcial (a base termina em 25/11). Use `mes_parcial` para sinalizar a variação no dashboard.