import numpy as np
import pandas as pd
import pytest

from src import config
from src.gerador import gerar_base_limpa, montar_catalogo
from src.imperfeicoes import aplicar_imperfeicoes
from src.indicadores import (
    LIMITE_ATENCAO,
    META_SLA,
    adicionar_situacao,
    calcular_todos,
    classificar_sla,
)
from src.tratamento import tratar


@pytest.fixture(scope="module")
def cenario():
    catalogo_completo = montar_catalogo()
    catalogo = catalogo_completo[["tipo_solicitacao", "departamento", "sla_horas"]]
    base = gerar_base_limpa(np.random.default_rng(config.SEMENTE), catalogo_completo)
    raw, _ = aplicar_imperfeicoes(base, np.random.default_rng(config.SEMENTE + 1))
    tratada, quarentena = tratar(raw, catalogo, pd.Timestamp(config.DATA_REFERENCIA))
    return raw, tratada, quarentena


@pytest.fixture(scope="module")
def indicadores(cenario):
    _, tratada, quarentena = cenario
    return calcular_todos(tratada, quarentena)


def test_classificacao_de_sla():
    pcts = np.array([95.0, META_SLA, 85.0, LIMITE_ATENCAO, 79.9, np.nan])
    esperado = ["Dentro da meta", "Dentro da meta", "Atenção", "Atenção", "Crítico", "Crítico"]
    assert list(classificar_sla(pcts)) == esperado


def test_geral_bate_com_a_base(cenario, indicadores):
    _, tratada, _ = cenario
    geral = indicadores["geral"].iloc[0]
    concluidas = tratada[tratada["status"] == "Concluída"]
    assert geral["solicitacoes"] == len(tratada)
    assert geral["concluidas"] == len(concluidas)
    assert geral["pct_sla"] == round(100 * concluidas["dentro_sla"].astype(bool).mean(), 1)
    assert geral["tempo_medio_horas"] == round(concluidas["tempo_atendimento_horas"].mean(), 1)


def test_pendentes_e_pendentes_atrasadas(cenario, indicadores):
    _, tratada, _ = cenario
    pendentes = tratada[tratada["status"].isin(["Aberta", "Em andamento", "Aguardando terceiros"])]
    geral = indicadores["geral"].iloc[0]
    assert geral["pendentes"] == len(pendentes)
    assert geral["pendentes_atrasadas"] == pendentes["atrasada"].sum()


def test_taxa_de_atraso_usa_concluidas_e_pendentes(cenario, indicadores):
    _, tratada, _ = cenario
    base = adicionar_situacao(tratada)
    ativas = base[base["situacao"] != "Cancelada"]
    esperado = round(100 * ativas["atrasada"].mean(), 1)
    assert indicadores["geral"].iloc[0]["taxa_atraso"] == esperado


def test_departamentos_somam_o_geral(indicadores):
    departamento = indicadores["departamento"]
    geral = indicadores["geral"].iloc[0]
    assert len(departamento) == 7
    assert departamento["solicitacoes"].sum() == geral["solicitacoes"]
    assert departamento["atrasadas"].sum() == geral["atrasadas"]


def test_tipos_somam_o_geral_e_trazem_posicao(indicadores):
    tipo = indicadores["tipo"]
    assert len(tipo) == 26
    assert tipo["solicitacoes"].sum() == indicadores["geral"].iloc[0]["solicitacoes"]
    assert tipo["posicao_gargalo"].min() == 1
    assert tipo["taxa_atraso"].is_monotonic_decreasing


def test_mensal_tem_doze_meses_e_marca_o_parcial(indicadores):
    mensal = indicadores["mensal"]
    assert len(mensal) == 12
    assert mensal["mes_parcial"].sum() == 1
    assert bool(mensal["mes_parcial"].iloc[-1])
    assert pd.isna(mensal["variacao_volume_pct"].iloc[0])


def test_qualidade_fecha_a_conta(cenario, indicadores):
    raw, _, _ = cenario
    qualidade = indicadores["qualidade"].set_index("indicador")["valor"]
    assert qualidade["registros_brutos"] == len(raw)
    assert qualidade["registros_tratados"] + qualidade["registros_em_quarentena"] == len(raw)
    assert qualidade["quarentena_duplicata"] == round(config.TOTAL_SOLICITACOES * config.FRACAO_DUPLICATAS)