import numpy as np
import pandas as pd

from src.diagnostico import STATUS_PENDENTES

META_SLA = 90.0
LIMITE_ATENCAO = 80.0


def adicionar_situacao(base):
    saida = base.copy()
    saida["situacao"] = np.select(
        [saida["status"].isin(STATUS_PENDENTES), saida["status"] == "Concluída"],
        ["Pendente", "Concluída"],
        default="Cancelada",
    )
    saida["mes_abertura"] = saida["data_abertura"].dt.to_period("M").dt.to_timestamp().dt.date
    return saida


def classificar_sla(pct_sla):
    return np.select(
        [pct_sla >= META_SLA, pct_sla >= LIMITE_ATENCAO],
        ["Dentro da meta", "Atenção"],
        default="Crítico",
    )


def calcular_kpis(base, chave):
    dados = base.assign(
        concluida=(base["situacao"] == "Concluída").astype(int),
        pendente=(base["situacao"] == "Pendente").astype(int),
        dentro=base["dentro_sla"].fillna(False).astype(int),
        atrasada_int=base["atrasada"].astype(int),
        pendente_atrasada=((base["situacao"] == "Pendente") & base["atrasada"]).astype(int),
    )
    kpis = dados.groupby(chave).agg(
        solicitacoes=("id_solicitacao", "size"),
        concluidas=("concluida", "sum"),
        pendentes=("pendente", "sum"),
        dentro_do_prazo=("dentro", "sum"),
        atrasadas=("atrasada_int", "sum"),
        pendentes_atrasadas=("pendente_atrasada", "sum"),
        tempo_medio_horas=("tempo_atendimento_horas", "mean"),
    ).reset_index()
    ativas = kpis["concluidas"] + kpis["pendentes"]
    kpis["tempo_medio_horas"] = kpis["tempo_medio_horas"].round(1)
    kpis["pct_sla"] = (100 * kpis["dentro_do_prazo"] / kpis["concluidas"].replace(0, np.nan)).round(1)
    kpis["taxa_atraso"] = (100 * kpis["atrasadas"] / ativas.replace(0, np.nan)).round(1)
    kpis["status_sla"] = classificar_sla(kpis["pct_sla"])
    return kpis


def kpis_geral(base):
    return calcular_kpis(base.assign(escopo="Geral"), ["escopo"])


def kpis_departamento(base):
    return calcular_kpis(base, ["departamento"]).sort_values("taxa_atraso", ascending=False).reset_index(drop=True)


def kpis_tipo(base):
    kpis = calcular_kpis(base, ["departamento", "tipo_solicitacao", "sla_horas"])
    kpis["posicao_gargalo"] = kpis["taxa_atraso"].rank(method="min", ascending=False).astype(int)
    return kpis.sort_values(["posicao_gargalo", "tipo_solicitacao"]).reset_index(drop=True)


def kpis_mensal(base):
    kpis = calcular_kpis(base, ["mes_abertura"]).sort_values("mes_abertura").reset_index(drop=True)
    kpis["variacao_volume_pct"] = (100 * kpis["solicitacoes"].pct_change()).round(1)
    ultimo_dia = base["data_abertura"].max().normalize()
    ultimo_mes = ultimo_dia.to_period("M").to_timestamp().date()
    kpis["mes_parcial"] = (kpis["mes_abertura"] == ultimo_mes) & (ultimo_dia.day < ultimo_dia.days_in_month)
    return kpis


def kpis_qualidade(tratada, quarentena):
    total = len(tratada) + len(quarentena)
    motivos = quarentena["motivo_quarentena"].value_counts()
    duplicatas = int(motivos.get("duplicata", 0))
    linhas = [
        ("registros_brutos", float(total)),
        ("registros_tratados", float(len(tratada))),
        ("registros_em_quarentena", float(len(quarentena))),
        ("pct_quarentena", round(100 * len(quarentena) / total, 2)),
        ("taxa_duplicidade_pct", round(100 * duplicatas / total, 2)),
    ]
    linhas += [(f"quarentena_{motivo}", float(qtd)) for motivo, qtd in motivos.items()]
    return pd.DataFrame(linhas, columns=["indicador", "valor"])


def calcular_todos(tratada, quarentena):
    base = adicionar_situacao(tratada)
    return {
        "geral": kpis_geral(base),
        "departamento": kpis_departamento(base),
        "tipo": kpis_tipo(base),
        "mensal": kpis_mensal(base),
        "qualidade": kpis_qualidade(tratada, quarentena),
    }