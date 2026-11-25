# Regras de negócio

## Empresa fictícia

Nexus Serviços Corporativos. Cada departamento abre solicitações que precisam ser atendidas dentro de um prazo (SLA).

## Departamentos

| Código | Departamento |
|---|---|
| FIN | Financeiro |
| SUP | Suprimentos |
| OPE | Operações |
| LOG | Logística |
| ADM | Administrativo |
| TEC | Tecnologia |
| ATV | Gestão de Ativos |

## Tipos de solicitação e SLA

O SLA é definido pelo tipo de solicitação, em horas corridas.

| Departamento | Tipo de solicitação | SLA (h) |
|---|---|---|
| Financeiro | Emissão de nota fiscal | 24 |
| Financeiro | Conciliação de pagamento | 48 |
| Financeiro | Ajuste de faturamento | 72 |
| Financeiro | Estorno | 96 |
| Suprimentos | Cotação de fornecedor | 72 |
| Suprimentos | Pedido de compra | 48 |
| Suprimentos | Cadastro de fornecedor | 96 |
| Suprimentos | Reposição de estoque | 24 |
| Operações | Registro de pesagem | 8 |
| Operações | Correção de apontamento | 24 |
| Operações | Liberação de carga | 12 |
| Operações | Revisão de procedimento | 120 |
| Logística | Agendamento de transporte | 24 |
| Logística | Roteirização | 48 |
| Logística | Ocorrência de entrega | 12 |
| Logística | Devolução de mercadoria | 96 |
| Administrativo | Solicitação de material | 72 |
| Administrativo | Contrato e documentos | 120 |
| Administrativo | Reembolso de despesa | 96 |
| Tecnologia | Acesso a sistema | 8 |
| Tecnologia | Incidente em sistema | 12 |
| Tecnologia | Nova funcionalidade | 240 |
| Tecnologia | Extração de relatório | 48 |
| Gestão de Ativos | Manutenção corretiva | 48 |
| Gestão de Ativos | Manutenção preventiva | 120 |
| Gestão de Ativos | Baixa de ativo | 168 |

## Prioridade

| Prioridade | Efeito |
|---|---|
| Crítica | Prazo efetivo = 50% do SLA do tipo |
| Alta | Prazo efetivo = 75% do SLA do tipo |
| Média | Prazo efetivo = 100% do SLA do tipo |
| Baixa | Prazo efetivo = 125% do SLA do tipo |

`prazo_horas = sla_horas_tipo * fator_prioridade`

`data_limite = data_abertura + prazo_horas`

## Status

| Status | Descrição |
|---|---|
| Aberta | Registrada, ainda não iniciada |
| Em andamento | Em atendimento |
| Aguardando terceiros | Dependente de outra área ou fornecedor |
| Concluída | Atendida, com data de conclusão |
| Cancelada | Encerrada sem atendimento |

## Regras de cálculo

1. `tempo_atendimento_horas = data_conclusao - data_abertura`, apenas para solicitações concluídas.
2. Concluída dentro do prazo: `data_conclusao <= data_limite`.
3. Concluída fora do prazo: `data_conclusao > data_limite`, contada como SLA descumprido.
4. Pendente: status Aberta, Em andamento ou Aguardando terceiros.
5. Pendente atrasada: pendente com `data_referencia > data_limite`.
6. Canceladas ficam fora dos indicadores de SLA e de tempo médio.
7. `data_referencia` é a data de corte da extração e é fixa por base.

## Regras de consistência

- `data_conclusao` é obrigatória para Concluída e vazia para os demais status.
- `data_conclusao` não pode ser anterior a `data_abertura`.
- O departamento deve ser coerente com o tipo de solicitação.
- O identificador da solicitação é único.
- Duplicata: mesmo solicitante, tipo, departamento e data de abertura, com identificadores diferentes.

## Volume e período

- Entre 5.000 e 10.000 registros.
- Histórico de 12 meses, com sazonalidade (picos no fim de mês para Financeiro e na safra para Operações).
- Departamentos com perfis diferentes de volume e de atraso, para gerar gargalos analisáveis.

## Imperfeições propositais (Fase 2)

A base bruta terá problemas controlados, para exercitar a qualidade de dados:

- Duplicatas (cerca de 1% a 2%).
- Datas de conclusão anteriores à abertura.
- Status inconsistente com a data de conclusão.
- Departamento escrito de formas diferentes (caixa, espaços, abreviações).
- Valores nulos em campos obrigatórios.
- Tipo de solicitação fora do catálogo.