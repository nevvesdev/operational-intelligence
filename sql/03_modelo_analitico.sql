USE CATALOG workspace;
USE SCHEMA operational_intelligence;

CREATE OR REPLACE VIEW vw_fato_solicitacoes AS
SELECT
  id_solicitacao,
  data_abertura,
  data_conclusao,
  data_limite,
  departamento,
  tipo_solicitacao,
  prioridade,
  status,
  CASE
    WHEN status IN ('Aberta', 'Em andamento', 'Aguardando terceiros') THEN 'Pendente'
    WHEN status = 'Concluída' THEN 'Concluída'
    ELSE 'Cancelada'
  END AS situacao,
  solicitante,
  responsavel,
  canal_abertura,
  sla_horas,
  prazo_horas,
  tempo_atendimento_horas,
  dentro_sla,
  atrasada,
  CAST(DATE_TRUNC('month', data_abertura) AS DATE) AS mes_abertura
FROM silver_solicitacoes;