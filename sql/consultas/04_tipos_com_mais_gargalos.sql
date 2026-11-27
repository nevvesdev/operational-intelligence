WITH por_tipo AS (
  SELECT
    d.departamento,
    f.tipo_solicitacao,
    d.sla_horas,
    COUNT(*) AS total_solicitacoes,
    SUM(CASE WHEN f.atrasada THEN 1 ELSE 0 END) AS solicitacoes_atrasadas,
    ROUND(100.0 * SUM(CASE WHEN f.atrasada THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_atraso,
    ROUND(AVG(CASE WHEN f.situacao = 'Concluída' THEN f.tempo_atendimento_horas END), 1) AS tempo_medio_horas
  FROM vw_fato_solicitacoes f
  JOIN dim_tipo_solicitacao d ON f.tipo_solicitacao = d.tipo_solicitacao
  WHERE f.situacao <> 'Cancelada'
  GROUP BY d.departamento, f.tipo_solicitacao, d.sla_horas
)
SELECT
  RANK() OVER (ORDER BY pct_atraso DESC) AS posicao,
  departamento,
  tipo_solicitacao,
  sla_horas,
  total_solicitacoes,
  solicitacoes_atrasadas,
  pct_atraso,
  tempo_medio_horas
FROM por_tipo
ORDER BY pct_atraso DESC
LIMIT 10;