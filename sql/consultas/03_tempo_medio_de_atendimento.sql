WITH concluidas AS (
  SELECT departamento, tempo_atendimento_horas, prazo_horas
  FROM vw_fato_solicitacoes
  WHERE situacao = 'Concluída'
)
SELECT
  'Geral' AS departamento,
  COUNT(*) AS concluidas,
  ROUND(AVG(tempo_atendimento_horas), 1) AS tempo_medio_horas,
  ROUND(AVG(prazo_horas), 1) AS prazo_medio_horas,
  ROUND(AVG(tempo_atendimento_horas) / AVG(prazo_horas), 2) AS razao_tempo_prazo
FROM concluidas
UNION ALL
SELECT
  departamento,
  COUNT(*) AS concluidas,
  ROUND(AVG(tempo_atendimento_horas), 1) AS tempo_medio_horas,
  ROUND(AVG(prazo_horas), 1) AS prazo_medio_horas,
  ROUND(AVG(tempo_atendimento_horas) / AVG(prazo_horas), 2) AS razao_tempo_prazo
FROM concluidas
GROUP BY departamento
ORDER BY razao_tempo_prazo DESC;