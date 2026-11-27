import unicodedata

import numpy as np
import pandas as pd

from src import config


def _sem_acento(texto):
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(caractere for caractere in normalizado if unicodedata.category(caractere) != "Mn")


def _selecionar(rng, candidatos, fracao, total, tocados):
    disponiveis = np.array([indice for indice in candidatos if indice not in tocados], dtype=int)
    quantidade = min(int(round(total * fracao)), len(disponiveis))
    escolhidos = rng.choice(disponiveis, size=quantidade, replace=False)
    tocados.update(escolhidos.tolist())
    return escolhidos


def _registrar(registros, base, indices, problema):
    for indice in indices:
        registros.append((base.at[indice, "id_solicitacao"], problema))


def _variar_tipo(rng, tipo):
    opcoes = {
        tipo.lower(),
        tipo.upper(),
        _sem_acento(tipo),
        f"{tipo} - urgente",
        tipo.replace(" ", "_"),
    }
    opcoes.discard(tipo)
    return rng.choice(sorted(opcoes))


def aplicar_imperfeicoes(base, rng):
    df = base.copy()
    total = len(base)
    registros = []
    tocados = set()

    quantidade_duplicatas = int(round(total * config.FRACAO_DUPLICATAS))
    originais = rng.choice(df.index.to_numpy(), size=quantidade_duplicatas, replace=False)
    copias = df.loc[originais].copy()
    copias["id_solicitacao"] = [
        f"SOL-{total + posicao + 1:06d}" for posicao in range(quantidade_duplicatas)
    ]
    df = pd.concat([df, copias], ignore_index=True)
    novos = np.arange(total, total + quantidade_duplicatas)
    tocados.update(originais.tolist())
    tocados.update(novos.tolist())
    _registrar(registros, df, novos, "duplicata")

    concluidas = df.index[df["status"] == "Concluída"]
    indices = _selecionar(rng, concluidas, config.FRACAO_CONCLUSAO_INVALIDA, total, tocados)
    atraso = pd.to_timedelta(rng.integers(1, 49, len(indices)), unit="h")
    df.loc[indices, "data_conclusao"] = df.loc[indices, "data_abertura"] - atraso
    _registrar(registros, df, indices, "conclusao_anterior_abertura")

    indices = _selecionar(rng, concluidas, config.FRACAO_STATUS_INCONSISTENTE / 2, total, tocados)
    df.loc[indices, "data_conclusao"] = pd.NaT
    _registrar(registros, df, indices, "status_inconsistente")

    pendentes = df.index[df["status"].isin(config.STATUS_PENDENTES)]
    indices = _selecionar(rng, pendentes, config.FRACAO_STATUS_INCONSISTENTE / 2, total, tocados)
    deslocamento = pd.to_timedelta(
        df.loc[indices, "prazo_horas"].to_numpy() * rng.uniform(0.3, 1.5, len(indices)),
        unit="h",
    ).round("s")
    df.loc[indices, "data_conclusao"] = df.loc[indices, "data_abertura"] + deslocamento
    _registrar(registros, df, indices, "status_inconsistente")

    indices = _selecionar(rng, df.index, config.FRACAO_DEPARTAMENTO_VARIADO, total, tocados)
    for indice in indices:
        opcoes = config.VARIACOES_DEPARTAMENTO[df.at[indice, "departamento"]]
        df.at[indice, "departamento"] = str(rng.choice(opcoes))
    _registrar(registros, df, indices, "departamento_variado")

    for campo in config.CAMPOS_COM_NULOS:
        indices = _selecionar(rng, df.index, config.FRACAO_NULOS_POR_CAMPO, total, tocados)
        df.loc[indices, campo] = np.nan
        _registrar(registros, df, indices, f"nulo_{campo}")

    indices = _selecionar(rng, df.index, config.FRACAO_TIPO_FORA_CATALOGO, total, tocados)
    for indice in indices:
        df.at[indice, "tipo_solicitacao"] = str(_variar_tipo(rng, df.at[indice, "tipo_solicitacao"]))
    _registrar(registros, df, indices, "tipo_fora_catalogo")

    df = df.sort_values("id_solicitacao").reset_index(drop=True)
    controle = pd.DataFrame(registros, columns=["id_solicitacao", "tipo_problema"])
    return df, controle