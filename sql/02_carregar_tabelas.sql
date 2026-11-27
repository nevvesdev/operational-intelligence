USE CATALOG workspace;
USE SCHEMA operational_intelligence;

CREATE OR REPLACE TABLE bronze_solicitacoes AS
SELECT
  id_solicitacao,
  CAST(data_abertura AS TIMESTAMP) AS data_abertura,
  CAST(data_conclusao AS TIMESTAMP) AS data_conclusao,
  departamento,
  tipo_solicitacao,
  prioridade,
  status,
  solicitante,
  responsavel,
  CAST(sla_horas AS INT) AS sla_horas,
  CAST(prazo_horas AS DOUBLE) AS prazo_horas,
  CAST(data_limite AS TIMESTAMP) AS data_limite,
  canal_abertura,
  observacao
FROM read_files(
  '/Volumes/workspace/operational_intelligence/arquivos/bronze_solicitacoes.csv',
  format => 'csv',
  header => true,
  schema => 'id_solicitacao STRING, data_abertura STRING, data_conclusao STRING, departamento STRING, tipo_solicitacao STRING, prioridade STRING, status STRING, solicitante STRING, responsavel STRING, sla_horas STRING, prazo_horas STRING, data_limite STRING, canal_abertura STRING, observacao STRING'
);

CREATE OR REPLACE TABLE silver_solicitacoes AS
SELECT
  id_solicitacao,
  CAST(data_abertura AS TIMESTAMP) AS data_abertura,
  CAST(data_conclusao AS TIMESTAMP) AS data_conclusao,
  departamento,
  tipo_solicitacao,
  prioridade,
  status,
  solicitante,
  responsavel,
  CAST(sla_horas AS INT) AS sla_horas,
  CAST(prazo_horas AS DOUBLE) AS prazo_horas,
  CAST(data_limite AS TIMESTAMP) AS data_limite,
  canal_abertura,
  observacao,
  ajustes_aplicados,
  CAST(tempo_atendimento_horas AS DOUBLE) AS tempo_atendimento_horas,
  CAST(dentro_sla AS BOOLEAN) AS dentro_sla,
  CAST(atrasada AS BOOLEAN) AS atrasada,
  mes_referencia
FROM read_files(
  '/Volumes/workspace/operational_intelligence/arquivos/solicitacoes_tratadas.csv',
  format => 'csv',
  header => true,
  schema => 'id_solicitacao STRING, data_abertura STRING, data_conclusao STRING, departamento STRING, tipo_solicitacao STRING, prioridade STRING, status STRING, solicitante STRING, responsavel STRING, sla_horas STRING, prazo_horas STRING, data_limite STRING, canal_abertura STRING, observacao STRING, ajustes_aplicados STRING, tempo_atendimento_horas STRING, dentro_sla STRING, atrasada STRING, mes_referencia STRING'
);

CREATE OR REPLACE TABLE silver_quarentena AS
SELECT
  id_solicitacao,
  CAST(data_abertura AS TIMESTAMP) AS data_abertura,
  CAST(data_conclusao AS TIMESTAMP) AS data_conclusao,
  departamento,
  tipo_solicitacao,
  prioridade,
  status,
  solicitante,
  responsavel,
  CAST(sla_horas AS INT) AS sla_horas,
  CAST(prazo_horas AS DOUBLE) AS prazo_horas,
  CAST(data_limite AS TIMESTAMP) AS data_limite,
  canal_abertura,
  observacao,
  motivo_quarentena
FROM read_files(
  '/Volumes/workspace/operational_intelligence/arquivos/solicitacoes_quarentena.csv',
  format => 'csv',
  header => true,
  schema => 'id_solicitacao STRING, data_abertura STRING, data_conclusao STRING, departamento STRING, tipo_solicitacao STRING, prioridade STRING, status STRING, solicitante STRING, responsavel STRING, sla_horas STRING, prazo_horas STRING, data_limite STRING, canal_abertura STRING, observacao STRING, motivo_quarentena STRING'
);

CREATE OR REPLACE TABLE dim_tipo_solicitacao AS
SELECT
  tipo_solicitacao,
  departamento,
  CAST(sla_horas AS INT) AS sla_horas
FROM read_files(
  '/Volumes/workspace/operational_intelligence/arquivos/catalogo_tipos.csv',
  format => 'csv',
  header => true,
  schema => 'tipo_solicitacao STRING, departamento STRING, sla_horas STRING'
);