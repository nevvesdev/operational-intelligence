# Qualidade e tratamento dos dados

## Como executar

```bash
python -m src.processar_base
python -m pytest
```

Entrada: `data/raw/solicitacoes_raw.csv`, `catalogo_tipos.csv` e `controle_imperfeicoes.csv`.

Saídas:

| Arquivo | Conteúdo |
|---|---|
| data/processed/solicitacoes_tratadas.csv | Base confiável, com campos derivados |
| data/processed/solicitacoes_quarentena.csv | Registros separados, com o motivo |
| reports/relatorio_qualidade.csv | Detectado contra esperado, por tipo de problema |

## Princípio

Corrigir quando o valor correto é determinável a partir dos próprios dados. Quando não é, separar o registro em quarentena em vez de adivinhar.

## Regras de tratamento

| Problema | Regra | Resultado |
|---|---|---|
| Departamento com grafia variada | Normaliza caixa, acento, espaços e pontuação e mapeia pela tabela de aliases | Padronizado |
| Tipo fora do catálogo | Mesma normalização, removendo o sufixo "urgente" | Padronizado |
| Prioridade nula | `prazo_horas / sla_horas` identifica o fator (0,5 Crítica, 0,75 Alta, 1,0 Média, 1,25 Baixa) | Inferida |
| Solicitante, responsável ou canal nulo | Preenchido com "Não informado" | Marcado |
| Duplicata | Mesmo solicitante, tipo, departamento e data de abertura; mantém o menor id | Quarentena |
| Conclusão anterior à abertura | Data impossível, sem como saber qual das datas está errada | Quarentena |
| Status inconsistente com a conclusão | Concluída sem data, ou não concluída com data | Quarentena |

Cada ajuste fica registrado na coluna `ajustes_aplicados` da base tratada.

## Campos derivados

| Campo | Regra |
|---|---|
| tempo_atendimento_horas | Conclusão menos abertura, só para concluídas |
| dentro_sla | Conclusão menor ou igual à data limite, só para concluídas |
| atrasada | Concluída fora do prazo ou pendente com data limite vencida na referência |
| mes_referencia | Mês de abertura, formato `AAAA-MM` |

## Validação

Antes de gravar, a base tratada passa por verificações: ids únicos, sem nulos em campos obrigatórios, pares departamento e tipo válidos, SLA igual ao catálogo, prazo coerente com a prioridade, regras de conclusão e ausência de duplicatas. Qualquer falha interrompe o processo.

## Avaliação contra o gabarito

O diagnóstico é comparado com `controle_imperfeicoes.csv`. Resultado: todos os problemas injetados foram detectados, sem falsos positivos.

## Impacto no SLA

| Visão | SLA |
|---|---|
| Base bruta, cálculo direto no Excel | 73,5% |
| Base tratada | 73,3% |

O efeito no total é pequeno, porque os registros problemáticos são poucos. O dano maior está na fragmentação: antes do tratamento, o campo de departamento tem 47 grafias distintas e qualquer agrupamento fica errado.