import numpy as np
import pandas as pd
import pytest

from src import config
from src.gerador import gerar_base_limpa, montar_catalogo
from src.imperfeicoes import aplicar_imperfeicoes


@pytest.fixture(scope="module")
def catalogo():
    return montar_catalogo()


@pytest.fixture(scope="module")
def base_limpa(catalogo):
    return gerar_base_limpa(np.random.default_rng(config.SEMENTE), catalogo)


@pytest.fixture(scope="module")
def base_raw(base_limpa):
    return aplicar_imperfeicoes(base_limpa, np.random.default_rng(config.SEMENTE + 1))


def test_total_de_registros(base_limpa):
    assert len(base_limpa) == config.TOTAL_SOLICITACOES


def test_colunas_seguem_o_dicionario(base_limpa):
    assert list(base_limpa.columns) == config.COLUNAS_BASE


def test_ids_unicos(base_limpa):
    assert base_limpa["id_solicitacao"].is_unique


def test_geracao_reprodutivel(catalogo):
    primeira = gerar_base_limpa(np.random.default_rng(config.SEMENTE), catalogo)
    segunda = gerar_base_limpa(np.random.default_rng(config.SEMENTE), catalogo)
    pd.testing.assert_frame_equal(primeira, segunda)


def test_tipo_pertence_ao_departamento(base_limpa, catalogo):
    pares_validos = set(zip(catalogo["departamento"], catalogo["tipo_solicitacao"]))
    pares_base = set(zip(base_limpa["departamento"], base_limpa["tipo_solicitacao"]))
    assert pares_base <= pares_validos


def test_conclusao_apenas_para_concluidas(base_limpa):
    concluidas = base_limpa["status"] == "Concluída"
    assert base_limpa.loc[concluidas, "data_conclusao"].notna().all()
    assert base_limpa.loc[~concluidas, "data_conclusao"].isna().all()


def test_conclusao_nao_anterior_a_abertura(base_limpa):
    concluidas = base_limpa[base_limpa["status"] == "Concluída"]
    assert (concluidas["data_conclusao"] >= concluidas["data_abertura"]).all()


def test_conclusao_nao_posterior_a_referencia(base_limpa):
    referencia = pd.Timestamp(config.DATA_REFERENCIA)
    assert (base_limpa["data_conclusao"].dropna() <= referencia).all()


def test_data_limite_respeita_prazo(base_limpa):
    esperado = (
        base_limpa["data_abertura"] + pd.to_timedelta(base_limpa["prazo_horas"], unit="h")
    ).dt.round("s")
    diferenca = (base_limpa["data_limite"] - esperado).abs()
    assert (diferenca <= pd.Timedelta(seconds=1)).all()


def test_prazo_segue_fator_de_prioridade(base_limpa):
    fator = base_limpa["prioridade"].map(config.FATOR_PRIORIDADE)
    esperado = (base_limpa["sla_horas"] * fator).round(2)
    assert np.allclose(base_limpa["prazo_horas"], esperado)


def test_historico_de_doze_meses(base_limpa):
    meses = base_limpa["data_abertura"].dt.to_period("M").nunique()
    assert meses == 12


def test_todos_os_departamentos_presentes(base_limpa):
    assert set(base_limpa["departamento"]) == set(config.DEPARTAMENTOS.values())


def test_existem_pendentes_atrasadas(base_limpa):
    referencia = pd.Timestamp(config.DATA_REFERENCIA)
    pendentes = base_limpa[base_limpa["status"].isin(config.STATUS_PENDENTES)]
    assert len(pendentes) > 0
    assert (pendentes["data_limite"] < referencia).any()


def test_duplicatas_coerentes_com_o_controle(base_raw):
    raw, controle = base_raw
    ids_duplicados = set(controle.loc[controle["tipo_problema"] == "duplicata", "id_solicitacao"])
    chaves = ["solicitante", "tipo_solicitacao", "departamento", "data_abertura"]
    repetidas = raw[raw.duplicated(subset=chaves, keep=False)]
    assert ids_duplicados <= set(repetidas["id_solicitacao"])
    assert len(ids_duplicados) == round(config.TOTAL_SOLICITACOES * config.FRACAO_DUPLICATAS)


def test_raw_contem_todos_os_tipos_de_imperfeicao(base_raw):
    _, controle = base_raw
    esperados = {
        "duplicata",
        "conclusao_anterior_abertura",
        "status_inconsistente",
        "departamento_variado",
        "tipo_fora_catalogo",
    } | {f"nulo_{campo}" for campo in config.CAMPOS_COM_NULOS}
    assert esperados == set(controle["tipo_problema"])


def test_imperfeicoes_deixam_marcas_na_base(base_raw, catalogo):
    raw, controle = base_raw
    indexado = raw.set_index("id_solicitacao")

    ids = controle.loc[controle["tipo_problema"] == "conclusao_anterior_abertura", "id_solicitacao"]
    assert (indexado.loc[ids, "data_conclusao"] < indexado.loc[ids, "data_abertura"]).all()

    ids = controle.loc[controle["tipo_problema"] == "tipo_fora_catalogo", "id_solicitacao"]
    assert (~indexado.loc[ids, "tipo_solicitacao"].isin(catalogo["tipo_solicitacao"])).all()

    ids = controle.loc[controle["tipo_problema"] == "departamento_variado", "id_solicitacao"]
    assert (~indexado.loc[ids, "departamento"].isin(config.DEPARTAMENTOS.values())).all()

    ids = controle.loc[controle["tipo_problema"] == "nulo_responsavel", "id_solicitacao"]
    assert indexado.loc[ids, "responsavel"].isna().all()