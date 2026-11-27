import numpy as np
import pandas as pd

from src import normalizacao
from src.diagnostico import (
    STATUS_PENDENTES,
    mascara_conclusao_invalida,
    mascara_duplicata,
    mascara_status_inconsistente,
)

FATOR_PARA_PRIORIDADE = {0.5: "Crítica", 0.75: "Alta", 1.0: "Média", 1.25: "Baixa"}
NAO_INFORMADO = "Não informado"
NAO_INFORMADA = "Não informada"


def derivar_campos(df, referencia):
    saida = df.copy()
    concluida = saida["status"] == "Concluída"
    pendente = saida["status"].isin(STATUS_PENDENTES)
    horas = (saida["data_conclusao"] - saida["data_abertura"]).dt.total_seconds() / 3600
    saida["tempo_atendimento_horas"] = horas.where(concluida).round(2)
    dentro = (saida["data_conclusao"] <= saida["data_limite"]).astype("boolean")
    saida["dentro_sla"] = dentro.where(concluida)
    saida["atrasada"] = np.where(
        concluida,
        saida["data_conclusao"] > saida["data_limite"],
        np.where(pendente, saida["data_limite"] < referencia, False),
    )
    saida["mes_referencia"] = saida["data_abertura"].dt.strftime("%Y-%m")
    return saida


def tratar(df, catalogo, referencia):
    base = df.sort_values("id_solicitacao").reset_index(drop=True)
    mapa = normalizacao.mapa_tipos(catalogo)
    por_tipo = catalogo.set_index("tipo_solicitacao")

    tipo = base["tipo_solicitacao"].map(lambda valor: normalizacao.canonizar_tipo(valor, mapa))
    departamento_do_tipo = tipo.map(por_tipo["departamento"])
    departamento = base["departamento"].map(normalizacao.canonizar_departamento)
    departamento = departamento.fillna(departamento_do_tipo)
    sla_catalogo = tipo.map(por_tipo["sla_horas"])

    razao = (base["prazo_horas"] / sla_catalogo).round(2)
    prioridade_inferida = razao.map(FATOR_PARA_PRIORIDADE)
    prioridade = base["prioridade"].fillna(prioridade_inferida).fillna(NAO_INFORMADA)

    ajustes = pd.DataFrame(
        {
            "tipo_padronizado": tipo.notna() & (tipo != base["tipo_solicitacao"]),
            "departamento_padronizado": departamento.notna() & (departamento != base["departamento"]),
            "prioridade_inferida": base["prioridade"].isna() & prioridade_inferida.notna(),
            "solicitante_nao_informado": base["solicitante"].isna(),
            "responsavel_nao_informado": base["responsavel"].isna(),
            "canal_nao_informado": base["canal_abertura"].isna(),
        }
    )

    motivo = pd.Series(pd.NA, index=base.index, dtype="object")

    def marcar(mascara, nome):
        motivo[mascara & motivo.isna()] = nome

    marcar(mascara_duplicata(base, tipo, departamento), "duplicata")
    marcar(tipo.isna(), "tipo_desconhecido")
    marcar(departamento.isna() | (departamento != departamento_do_tipo), "departamento_incompativel_com_tipo")
    marcar(mascara_conclusao_invalida(base), "conclusao_anterior_abertura")
    marcar(mascara_status_inconsistente(base), "status_inconsistente")

    em_quarentena = motivo.notna()
    quarentena = base[em_quarentena].copy()
    quarentena["motivo_quarentena"] = motivo[em_quarentena]

    tratada = base[~em_quarentena].copy()
    tratada["tipo_solicitacao"] = tipo[~em_quarentena]
    tratada["departamento"] = departamento[~em_quarentena]
    tratada["prioridade"] = prioridade[~em_quarentena]
    tratada["sla_horas"] = sla_catalogo[~em_quarentena].astype(int)
    for campo in ["solicitante", "responsavel", "canal_abertura"]:
        tratada[campo] = tratada[campo].fillna(NAO_INFORMADO)
    nomes = ajustes.columns.to_numpy()
    tratada["ajustes_aplicados"] = [
        ";".join(nomes[linha]) for linha in ajustes[~em_quarentena].to_numpy()
    ]
    tratada = derivar_campos(tratada, referencia).reset_index(drop=True)
    return tratada, quarentena.reset_index(drop=True)