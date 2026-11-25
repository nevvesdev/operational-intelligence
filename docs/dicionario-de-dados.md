# Dicionário de dados

Tabela: `solicitacoes`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| id_solicitacao | texto | Sim | Identificador único, formato `SOL-000001` |
| data_abertura | datetime | Sim | Data e hora de abertura |
| data_conclusao | datetime | Condicional | Preenchida apenas quando Concluída |
| departamento | texto | Sim | Departamento solicitante |
| tipo_solicitacao | texto | Sim | Tipo conforme catálogo |
| prioridade | texto | Sim | Crítica, Alta, Média ou Baixa |
| status | texto | Sim | Aberta, Em andamento, Aguardando terceiros, Concluída ou Cancelada |
| solicitante | texto | Sim | Código do solicitante, formato `USR-0001` |
| responsavel | texto | Sim | Código do analista responsável, formato `ANL-001` |
| sla_horas | inteiro | Sim | SLA base do tipo, em horas |
| prazo_horas | decimal | Sim | SLA ajustado pela prioridade |
| data_limite | datetime | Sim | `data_abertura + prazo_horas` |
| canal_abertura | texto | Sim | E-mail, Sistema, Telefone ou Planilha |
| observacao | texto | Não | Texto livre |

Tabela: `catalogo_tipos`

| Campo | Tipo | Descrição |
|---|---|---|
| tipo_solicitacao | texto | Nome do tipo |
| departamento | texto | Departamento dono do tipo |
| sla_horas | inteiro | SLA base em horas |

Campos derivados (calculados nas Fases 2 e 3)

| Campo | Descrição |
|---|---|
| tempo_atendimento_horas | Conclusão menos abertura |
| dentro_sla | Booleano, apenas para concluídas |
| atrasada | Booleano, para pendentes vencidas e concluídas fora do prazo |
| mes_referencia | Mês de abertura, formato `AAAA-MM` |