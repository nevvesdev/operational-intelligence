import pandas as pd

from src.diagnostico import STATUS_PENDENTES
from src.tratamento import NAO_INFORMADA

CAMPOS_OBRIGATORIOS = [
    "id_solicitacao",
    "data_abertura",
    "departamento",
    "tipo_solicitacao",
    "prioridade",
    "status",
    "solicitante",
    "responsavel",
    "sla_horas",
    "prazo_horas",
    "data_limite",
    "canal_abertura",
]
STATUS_VALIDOS = ["Aberta", "Em andamento", "Aguardando terceiros", "Concluída", "Cancelada"]
FATOR_PRIORIDADE = {"Crítica": 0.5, "Alta": 0.75, "Média": 1.0, "Baixa": 1.25}


def validar(tratada, catalogo):
    falhas = []

    def verificar(condicao, mensagem):
        if not condicao:
            falhas.append(mensagem)

    verificar(tratada["id_solicitacao"].is_unique, "ids duplicados")

    nulos = tratada[CAMPOS_OBRIGATORIOS].isna().sum()
    for campo, quantidade in nulos[nulos > 0].items():
        falhas.append(f"{campo}: {quantidade} nulos")

    pares_validos = set(zip(catalogo["departamento"], catalogo["tipo_solicitacao"]))
    pares_base = set(zip(tratada["departamento"], tratada["tipo_solicitacao"]))
    verificar(pares_base <= pares_validos, "pares departamento e tipo fora do catálogo")

    verificar(tratada["status"].isin(STATUS_VALIDOS).all(), "status fora do domínio")

    sla_catalogo = tratada["tipo_solicitacao"].map(catalogo.set_index("tipo_solicitacao")["sla_horas"])
    verificar((tratada["sla_horas"] == sla_catalogo).all(), "sla_horas divergente do catálogo")

    informadas = tratada["prioridade"] != NAO_INFORMADA
    fator = tratada.loc[informadas, "prioridade"].map(FATOR_PRIORIDADE)
    esperado = (tratada.loc[informadas, "sla_horas"] * fator).round(2)
    verificar((tratada.loc[informadas, "prazo_horas"] - esperado).abs().max() < 0.01, "prazo_horas divergente da prioridade")

    concluida = tratada["status"] == "Concluída"
    verificar(tratada.loc[concluida, "data_conclusao"].notna().all(), "concluída sem data_conclusao")
    verificar(tratada.loc[~concluida, "data_conclusao"].isna().all(), "não concluída com data_conclusao")
    verificar(
        (tratada.loc[concluida, "data_conclusao"] >= tratada.loc[concluida, "data_abertura"]).all(),
        "conclusão anterior à abertura",
    )
    verificar(tratada.loc[~concluida, "dentro_sla"].isna().all(), "dentro_sla preenchido fora das concluídas")
    verificar(tratada.loc[concluida, "dentro_sla"].notna().all(), "dentro_sla vazio em concluídas")

    chaves = ["solicitante", "tipo_solicitacao", "departamento", "data_abertura"]
    com_solicitante = tratada["solicitante"] != "Não informado"
    verificar(not tratada[com_solicitante].duplicated(subset=chaves).any(), "duplicatas remanescentes")

    verificar(tratada["status"].isin(STATUS_PENDENTES + ["Concluída", "Cancelada"]).all(), "status inesperado")
    return falhas


def exigir_valida(tratada, catalogo):
    falhas = validar(tratada, catalogo)
    if falhas:
        raise ValueError("; ".join(falhas))