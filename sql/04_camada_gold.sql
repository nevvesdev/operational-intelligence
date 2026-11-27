USE CATALOG workspace;
USE SCHEMA operational_intelligence;

CREATE OR REPLACE VIEW gold_kpi_geral AS
WITH agregado AS (
  SELECT
    'Geral' AS escopo,
    COUNT(*) AS solicitacoes,
    SUM(CASE WHEN situacao = 'Concluída' THEN 1 ELSE 0 END) AS concluidas,
    SUM(CASE WHEN situacao = 'Pendente' THEN 1 ELSE 0 END) AS pendentes,
    SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) AS dentro_do_prazo,
    SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) AS atrasadas,
    SUM(CASE WHEN situacao = 'Pendente' AND atrasada THEN 1 ELSE 0 END) AS pendentes_atrasadas,
    ROUND(AVG(tempo_atendimento_horas), 1) AS tempo_medio_horas
  FROM vw_fato_solicitacoes
),
calculado AS (
  SELECT
    *,
    ROUND(100.0 * dentro_do_prazo / NULLIF(concluidas, 0), 1) AS pct_sla,
    ROUND(100.0 * atrasadas / NULLIF(concluidas + pendentes, 0), 1) AS taxa_atraso
  FROM agregado
)
SELECT
  *,
  CASE WHEN pct_sla >= 90 THEN 'Dentro da meta' WHEN pct_sla >= 80 THEN 'Atenção' ELSE 'Crítico' END AS status_sla
FROM calculado;

CREATE OR REPLACE VIEW gold_kpi_departamento AS
WITH agregado AS (
  SELECT
    departamento,
    COUNT(*) AS solicitacoes,
    SUM(CASE WHEN situacao = 'Concluída' THEN 1 ELSE 0 END) AS concluidas,
    SUM(CASE WHEN situacao = 'Pendente' THEN 1 ELSE 0 END) AS pendentes,
    SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) AS dentro_do_prazo,
    SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) AS atrasadas,
    SUM(CASE WHEN situacao = 'Pendente' AND atrasada THEN 1 ELSE 0 END) AS pendentes_atrasadas,
    ROUND(AVG(tempo_atendimento_horas), 1) AS tempo_medio_horas
  FROM vw_fato_solicitacoes
  GROUP BY departamento
),
calculado AS (
  SELECT
    *,
    ROUND(100.0 * dentro_do_prazo / NULLIF(concluidas, 0), 1) AS pct_sla,
    ROUND(100.0 * atrasadas / NULLIF(concluidas + pendentes, 0), 1) AS taxa_atraso
  FROM agregado
)
SELECT
  *,
  CASE WHEN pct_sla >= 90 THEN 'Dentro da meta' WHEN pct_sla >= 80 THEN 'Atenção' ELSE 'Crítico' END AS status_sla
FROM calculado;

CREATE OR REPLACE VIEW gold_kpi_tipo AS
WITH agregado AS (
  SELECT
    departamento,
    tipo_solicitacao,
    sla_horas,
    COUNT(*) AS solicitacoes,
    SUM(CASE WHEN situacao = 'Concluída' THEN 1 ELSE 0 END) AS concluidas,
    SUM(CASE WHEN situacao = 'Pendente' THEN 1 ELSE 0 END) AS pendentes,
    SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) AS dentro_do_prazo,
    SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) AS atrasadas,
    SUM(CASE WHEN situacao = 'Pendente' AND atrasada THEN 1 ELSE 0 END) AS pendentes_atrasadas,
    ROUND(AVG(tempo_atendimento_horas), 1) AS tempo_medio_horas
  FROM vw_fato_solicitacoes
  GROUP BY departamento, tipo_solicitacao, sla_horas
),
calculado AS (
  SELECT
    *,
    ROUND(100.0 * dentro_do_prazo / NULLIF(concluidas, 0), 1) AS pct_sla,
    ROUND(100.0 * atrasadas / NULLIF(concluidas + pendentes, 0), 1) AS taxa_atraso
  FROM agregado
)
SELECT
  *,
  CASE WHEN pct_sla >= 90 THEN 'Dentro da meta' WHEN pct_sla >= 80 THEN 'Atenção' ELSE 'Crítico' END AS status_sla,
  RANK() OVER (ORDER BY taxa_atraso DESC) AS posicao_gargalo
FROM calculado;

CREATE OR REPLACE VIEW gold_kpi_mensal AS
WITH agregado AS (
  SELECT
    mes_abertura,
    COUNT(*) AS solicitacoes,
    SUM(CASE WHEN situacao = 'Concluída' THEN 1 ELSE 0 END) AS concluidas,
    SUM(CASE WHEN situacao = 'Pendente' THEN 1 ELSE 0 END) AS pendentes,
    SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) AS dentro_do_prazo,
    SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) AS atrasadas,
    SUM(CASE WHEN situacao = 'Pendente' AND atrasada THEN 1 ELSE 0 END) AS pendentes_atrasadas,
    ROUND(AVG(tempo_atendimento_horas), 1) AS tempo_medio_horas
  FROM vw_fato_solicitacoes
  GROUP BY mes_abertura
),
calculado AS (
  SELECT
    *,
    ROUND(100.0 * dentro_do_prazo / NULLIF(concluidas, 0), 1) AS pct_sla,
    ROUND(100.0 * atrasadas / NULLIF(concluidas + pendentes, 0), 1) AS taxa_atraso
  FROM agregado
),
limite AS (
  SELECT CAST(MAX(data_abertura) AS DATE) AS ultimo_dia
  FROM vw_fato_solicitacoes
)
SELECT
  c.*,
  CASE WHEN c.pct_sla >= 90 THEN 'Dentro da meta' WHEN c.pct_sla >= 80 THEN 'Atenção' ELSE 'Crítico' END AS status_sla,
  ROUND(
    100.0 * (c.solicitacoes - LAG(c.solicitacoes) OVER (ORDER BY c.mes_abertura))
    / LAG(c.solicitacoes) OVER (ORDER BY c.mes_abertura),
    1
  ) AS variacao_volume_pct,
  (c.mes_abertura = CAST(DATE_TRUNC('month', l.ultimo_dia) AS DATE) AND l.ultimo_dia < LAST_DAY(l.ultimo_dia)) AS mes_parcial
FROM calculado c
CROSS JOIN limite l;

CREATE OR REPLACE VIEW gold_qualidade AS
SELECT 'registros_brutos' AS indicador, CAST(COUNT(*) AS DOUBLE) AS valor
FROM bronze_solicitacoes
UNION ALL
SELECT 'registros_tratados', CAST(COUNT(*) AS DOUBLE)
FROM silver_solicitacoes
UNION ALL
SELECT 'registros_em_quarentena', CAST(COUNT(*) AS DOUBLE)
FROM silver_quarentena
UNION ALL
SELECT
  'pct_quarentena',
  ROUND(100.0 * (SELECT COUNT(*) FROM silver_quarentena) / (SELECT COUNT(*) FROM bronze_solicitacoes), 2)
UNION ALL
SELECT
  'taxa_duplicidade_pct',
  ROUND(
    100.0 * (SELECT COUNT(*) FROM silver_quarentena WHERE motivo_quarentena = 'duplicata')
    / (SELECT COUNT(*) FROM bronze_solicitacoes),
    2
  )
UNION ALL
SELECT CONCAT('quarentena_', motivo_quarentena), CAST(COUNT(*) AS DOUBLE)
FROM silver_quarentena
GROUP BY motivo_quarentena;