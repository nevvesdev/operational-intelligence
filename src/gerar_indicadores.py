from src import config
from src.exportacao import salvar_csv_padrao, salvar_excel
from src.indicadores import calcular_todos
from src.leitura import ler_processada


def main():
    tratada = ler_processada(config.DIR_PROCESSED / "solicitacoes_tratadas.csv")
    quarentena = ler_processada(config.DIR_PROCESSED / "solicitacoes_quarentena.csv")
    indicadores = calcular_todos(tratada, quarentena)

    destino = config.DIR_PROCESSED / "indicadores"
    for nome, tabela in indicadores.items():
        salvar_csv_padrao(tabela, destino / f"kpi_{nome}.csv")
    salvar_excel(indicadores, config.RAIZ / "reports" / "indicadores_operacionais.xlsx")

    geral = indicadores["geral"].iloc[0]
    print(f"Solicitações: {geral['solicitacoes']}")
    print(f"SLA geral: {geral['pct_sla']}% ({geral['status_sla']})")
    print(f"Tempo médio: {geral['tempo_medio_horas']} h")
    print(f"Taxa de atraso: {geral['taxa_atraso']}%")
    print(f"Pendentes: {geral['pendentes']} ({geral['pendentes_atrasadas']} atrasadas)")
    print()
    print(indicadores["departamento"][["departamento", "solicitacoes", "pct_sla", "taxa_atraso", "status_sla"]].to_string(index=False))
    print()
    print(indicadores["qualidade"].to_string(index=False))


if __name__ == "__main__":
    main()