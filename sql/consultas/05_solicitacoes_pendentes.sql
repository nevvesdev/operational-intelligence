WITH resumo AS (
  SELECT
    departamento AS grupo,
    SUM(CASE WHEN status = 'Aberta' THEN 1 ELSE 0 END) AS abertas,
    SUM(CASE WHEN status = 'Em andamento' THEN 1 ELSE 0 END) AS em_andamento,
    SUM(CASE WHEN status = 'Aguardando terceiros' THEN 1 ELSE 0 END) AS aguardando_terceiros,
    COUNT(*) AS pendentes,
    SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) AS pendentes_atrasadas
  FROM vw_fato_solicitacoes
  WHERE situacao = 'Pendente'
  GROUP BY ROLLUP (departamento)
)
SELECT
  COALESCE(grupo, 'Total') AS departamento,
  abertas,
  em_andamento,
  aguardando_terceiros,
  pendentes,
  pendentes_atrasadas
FROM resumo
ORDER BY CASE WHEN grupo IS NULL THEN 1 ELSE 0 END, pendentes DESC;