# Geração da base sintética

## Como gerar

```bash
python -m src.gerar_base
python -m pytest
```

Saídas em `data/raw/`:

| Arquivo | Conteúdo |
|---|---|
| solicitacoes_raw.csv | Base bruta com imperfeições propositais |
| catalogo_tipos.csv | Tipos de solicitação, departamento e SLA |
| controle_imperfeicoes.csv | Gabarito: id e tipo de cada problema injetado |
| base_operacional_raw.xlsx | Mesma base em Excel, para exploração e controles |

Os CSVs usam separador `;`, decimal `,` e codificação UTF-8 com BOM. Leitura em Pandas:

```python
pd.read_csv("data/raw/solicitacoes_raw.csv", sep=";", decimal=",", encoding="utf-8-sig")
```

## Parâmetros

- Semente fixa (42): a base é reproduzível.
- 8.000 solicitações limpas, mais 1,5% de duplicatas.
- Período: 01/12/2025 a 25/11/2026. Data de referência: 26/11/2026 00:00.
- Volume por departamento: Operações 22%, Financeiro 20%, Suprimentos 17%, Logística 14%, Tecnologia 12%, Administrativo 8%, Gestão de Ativos 7%.

## Comportamento operacional

- Aberturas concentradas em dias úteis e horário comercial, com crescimento de 2% ao mês.
- Financeiro: volume dobrado a partir do dia 25 de cada mês.
- Operações e Logística: pico entre abril e outubro (safra).
- Probabilidade de atraso por departamento, de 15% (Operações) a 40% (Gestão de Ativos), com acréscimo em tipos gargalo: cotação de fornecedor, baixa de ativo, manutenção corretiva, devolução de mercadoria, estorno e nova funcionalidade.
- Prioridade Crítica aumenta a chance de atraso em 6 pontos percentuais.
- Cancelamento aleatório de 3%.
- Solicitações cujo atendimento termina depois da data de referência ficam pendentes.
- Backlog antigo: solicitações com mais de 30 dias que nunca foram concluídas (1,2%, ou 3% em Administrativo e Gestão de Ativos).

## Imperfeições propositais

| Problema | Proporção | Tratamento na Fase 2 |
|---|---|---|
| Duplicata | 1,5% | Remover mantendo o primeiro id |
| Conclusão anterior à abertura | 0,6% | Marcar como inválida |
| Status inconsistente com a conclusão | 0,8% | Reconciliar status e data |
| Departamento escrito de formas diferentes | 3% | Padronizar |
| Nulo em solicitante, responsável, prioridade ou canal | 0,5% cada | Tratar conforme o campo |
| Tipo fora do catálogo | 0,7% | Mapear para o catálogo |

Cada registro afetado aparece em `controle_imperfeicoes.csv`, o que permite medir se a limpeza da Fase 2 encontrou tudo.