SELECT
  departamento,
  COUNT(*) AS total_solicitacoes,
  SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) AS solicitacoes_atrasadas,
  ROUND(100.0 * SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_atrasadas,
  RANK() OVER (ORDER BY SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) DESC) AS posicao_por_volume,
  RANK() OVER (ORDER BY SUM(CASE WHEN atrasada THEN 1 ELSE 0 END) * 1.0 / COUNT(*) DESC) AS posicao_por_taxa
FROM vw_fato_solicitacoes
WHERE situacao <> 'Cancelada'
GROUP BY departamento
ORDER BY solicitacoes_atrasadas DESC;