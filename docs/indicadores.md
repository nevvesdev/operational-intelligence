# Indicadores

| KPI | Definição | Universo |
|---|---|---|
| Cumprimento de SLA (%) | Concluídas dentro do prazo / total de concluídas | Concluídas |
| Tempo médio de atendimento (h) | Média de `tempo_atendimento_horas` | Concluídas |
| Solicitações pendentes | Contagem por status pendente | Pendentes |
| Pendentes atrasadas | Pendentes com `data_limite` vencida na data de referência | Pendentes |
| Taxa de atraso (%) | (Concluídas fora do prazo + pendentes atrasadas) / (concluídas + pendentes) | Concluídas e pendentes |
| Volume por departamento | Contagem de solicitações abertas | Todas, exceto duplicatas |
| Gargalo por tipo | Tipos com maior taxa de atraso e maior tempo médio | Concluídas e pendentes |
| Taxa de duplicidade (%) | Registros duplicados / total bruto | Base bruta |
| Evolução mensal | Volume, SLA e tempo médio por `mes_referencia` | Todas |

Meta de SLA de referência: 90%.