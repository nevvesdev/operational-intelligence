WITH concluidas AS (
  SELECT departamento, dentro_sla
  FROM vw_fato_solicitacoes
  WHERE situacao = 'Concluída'
)
SELECT
  'Geral' AS departamento,
  COUNT(*) AS concluidas,
  SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) AS dentro_do_prazo,
  ROUND(100.0 * SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_sla
FROM concluidas
UNION ALL
SELECT
  departamento,
  COUNT(*) AS concluidas,
  SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) AS dentro_do_prazo,
  ROUND(100.0 * SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_sla
FROM concluidas
GROUP BY departamento
ORDER BY pct_sla;