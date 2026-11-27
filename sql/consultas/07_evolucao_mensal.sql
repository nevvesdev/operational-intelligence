WITH mensal AS (
  SELECT
    mes_abertura,
    COUNT(*) AS solicitacoes,
    SUM(CASE WHEN situacao = 'Concluída' THEN 1 ELSE 0 END) AS concluidas,
    ROUND(
      100.0 * SUM(CASE WHEN dentro_sla THEN 1 ELSE 0 END)
      / NULLIF(SUM(CASE WHEN situacao = 'Concluída' THEN 1 ELSE 0 END), 0),
      1
    ) AS pct_sla,
    ROUND(AVG(tempo_atendimento_horas), 1) AS tempo_medio_horas
  FROM vw_fato_solicitacoes
  GROUP BY mes_abertura
)
SELECT
  mes_abertura,
  solicitacoes,
  solicitacoes - LAG(solicitacoes) OVER (ORDER BY mes_abertura) AS variacao_volume,
  ROUND(
    100.0 * (solicitacoes - LAG(solicitacoes) OVER (ORDER BY mes_abertura))
    / LAG(solicitacoes) OVER (ORDER BY mes_abertura),
    1
  ) AS variacao_pct,
  concluidas,
  pct_sla,
  tempo_medio_horas
FROM mensal
ORDER BY mes_abertura;