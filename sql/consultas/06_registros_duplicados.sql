WITH ranqueadas AS (
  SELECT
    id_solicitacao,
    solicitante,
    tipo_solicitacao,
    departamento,
    data_abertura,
    ROW_NUMBER() OVER (
      PARTITION BY solicitante, tipo_solicitacao, departamento, data_abertura
      ORDER BY id_solicitacao
    ) AS ordem,
    FIRST_VALUE(id_solicitacao) OVER (
      PARTITION BY solicitante, tipo_solicitacao, departamento, data_abertura
      ORDER BY id_solicitacao
    ) AS id_original
  FROM bronze_solicitacoes
)
SELECT
  COUNT(*) AS registros_na_base,
  SUM(CASE WHEN solicitante IS NOT NULL AND ordem > 1 THEN 1 ELSE 0 END) AS duplicatas,
  ROUND(100.0 * SUM(CASE WHEN solicitante IS NOT NULL AND ordem > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_duplicidade
FROM ranqueadas;

WITH ranqueadas AS (
  SELECT
    id_solicitacao,
    solicitante,
    tipo_solicitacao,
    departamento,
    data_abertura,
    ROW_NUMBER() OVER (
      PARTITION BY solicitante, tipo_solicitacao, departamento, data_abertura
      ORDER BY id_solicitacao
    ) AS ordem,
    FIRST_VALUE(id_solicitacao) OVER (
      PARTITION BY solicitante, tipo_solicitacao, departamento, data_abertura
      ORDER BY id_solicitacao
    ) AS id_original
  FROM bronze_solicitacoes
)
SELECT
  id_solicitacao AS id_duplicado,
  id_original,
  solicitante,
  tipo_solicitacao,
  departamento,
  data_abertura
FROM ranqueadas
WHERE solicitante IS NOT NULL AND ordem > 1
ORDER BY data_abertura
LIMIT 20;