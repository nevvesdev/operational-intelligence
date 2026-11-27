import pandas as pd

from src import normalizacao

CAMPOS_COM_NULOS = ["solicitante", "responsavel", "prioridade", "canal_abertura"]
STATUS_PENDENTES = ["Aberta", "Em andamento", "Aguardando terceiros"]


def mascara_duplicata(base, tipo, departamento):
    chaves = pd.DataFrame(
        {
            "solicitante": base["solicitante"],
            "tipo": tipo,
            "departamento": departamento,
            "data_abertura": base["data_abertura"],
        }
    )
    return chaves.duplicated(keep="first") & base["solicitante"].notna()


def mascara_conclusao_invalida(base):
    concluida = base["status"] == "Concluída"
    conclusao = base["data_conclusao"]
    return concluida & conclusao.notna() & (conclusao < base["data_abertura"])


def mascara_status_inconsistente(base):
    concluida = base["status"] == "Concluída"
    conclusao = base["data_conclusao"]
    return (concluida & conclusao.isna()) | (~concluida & conclusao.notna())


def diagnosticar(df, catalogo):
    base = df.sort_values("id_solicitacao").reset_index(drop=True)
    mapa = normalizacao.mapa_tipos(catalogo)
    departamento = base["departamento"].map(normalizacao.canonizar_departamento)
    tipo = base["tipo_solicitacao"].map(lambda valor: normalizacao.canonizar_tipo(valor, mapa))
    ids = base["id_solicitacao"]
    canonicos = set(catalogo["departamento"])

    detectados = {
        "duplicata": set(ids[mascara_duplicata(base, tipo, departamento)]),
        "conclusao_anterior_abertura": set(ids[mascara_conclusao_invalida(base)]),
        "status_inconsistente": set(ids[mascara_status_inconsistente(base)]),
        "departamento_variado": set(
            ids[base["departamento"].notna() & ~base["departamento"].isin(canonicos)]
        ),
        "tipo_fora_catalogo": set(
            ids[base["tipo_solicitacao"].notna() & ~base["tipo_solicitacao"].isin(catalogo["tipo_solicitacao"])]
        ),
    }
    for campo in CAMPOS_COM_NULOS:
        detectados[f"nulo_{campo}"] = set(ids[base[campo].isna()])
    return detectados