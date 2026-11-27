import pandas as pd

ACAO_POR_PROBLEMA = {
    "duplicata": "quarentena",
    "conclusao_anterior_abertura": "quarentena",
    "status_inconsistente": "quarentena",
    "departamento_variado": "padronizado",
    "tipo_fora_catalogo": "padronizado",
    "nulo_prioridade": "inferido pelo prazo",
    "nulo_solicitante": "marcado como não informado",
    "nulo_responsavel": "marcado como não informado",
    "nulo_canal_abertura": "marcado como não informado",
}


def comparar_com_gabarito(detectados, controle):
    linhas = []
    for problema in sorted(ACAO_POR_PROBLEMA):
        esperado = set(controle.loc[controle["tipo_problema"] == problema, "id_solicitacao"])
        encontrado = detectados.get(problema, set())
        linhas.append(
            {
                "problema": problema,
                "esperado": len(esperado),
                "detectado": len(encontrado),
                "acertos": len(esperado & encontrado),
                "falsos_positivos": len(encontrado - esperado),
                "nao_detectados": len(esperado - encontrado),
                "acao": ACAO_POR_PROBLEMA[problema],
            }
        )
    return pd.DataFrame(linhas)


def sla_ingenuo(df):
    com_data = df[df["data_conclusao"].notna()]
    dentro = int((com_data["data_conclusao"] <= com_data["data_limite"]).sum())
    fora = len(com_data) - dentro
    return dentro, fora, len(df) - len(com_data)