import pandas as pd

COLUNAS_DATA = ["data_abertura", "data_conclusao", "data_limite"]


def _ler_csv(caminho, **opcoes):
    return pd.read_csv(caminho, sep=";", decimal=",", encoding="utf-8-sig", **opcoes)


def ler_solicitacoes(caminho):
    return _ler_csv(caminho, parse_dates=COLUNAS_DATA)


def ler_catalogo(caminho):
    return _ler_csv(caminho)


def ler_controle(caminho):
    return _ler_csv(caminho)


def ler_processada(caminho):
    df = pd.read_csv(caminho, parse_dates=COLUNAS_DATA)
    if "dentro_sla" in df.columns:
        df["dentro_sla"] = df["dentro_sla"].astype("boolean")
    return df