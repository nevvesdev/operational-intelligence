import numpy as np
import pandas as pd
import pytest

from src import config
from src.avaliacao import comparar_com_gabarito
from src.diagnostico import diagnosticar
from src.gerador import gerar_base_limpa, montar_catalogo
from src.imperfeicoes import aplicar_imperfeicoes
from src.tratamento import tratar
from src.validacao import validar


@pytest.fixture(scope="module")
def referencia():
    return pd.Timestamp(config.DATA_REFERENCIA)


@pytest.fixture(scope="module")
def catalogo_completo():
    return montar_catalogo()


@pytest.fixture(scope="module")
def catalogo(catalogo_completo):
    return catalogo_completo[["tipo_solicitacao", "departamento", "sla_horas"]]


@pytest.fixture(scope="module")
def base_limpa(catalogo_completo):
    return gerar_base_limpa(np.random.default_rng(config.SEMENTE), catalogo_completo)


@pytest.fixture(scope="module")
def cenario(base_limpa):
    raw, controle = aplicar_imperfeicoes(base_limpa, np.random.default_rng(config.SEMENTE + 1))
    return raw, controle


@pytest.fixture(scope="module")
def tratamento(cenario, catalogo, referencia):
    raw, _ = cenario
    return tratar(raw, catalogo, referencia)


def test_diagnostico_encontra_todas_as_imperfeicoes(cenario, catalogo):
    raw, controle = cenario
    relatorio = comparar_com_gabarito(diagnosticar(raw, catalogo), controle)
    assert (relatorio["acertos"] == relatorio["esperado"]).all()
    assert (relatorio["falsos_positivos"] == 0).all()
    assert (relatorio["nao_detectados"] == 0).all()


def test_base_tratada_passa_na_validacao(tratamento, catalogo):
    tratada, _ = tratamento
    assert validar(tratada, catalogo) == []


def test_tratada_mais_quarentena_igual_ao_bruto(cenario, tratamento):
    raw, _ = cenario
    tratada, quarentena = tratamento
    assert len(tratada) + len(quarentena) == len(raw)


def test_quarentena_bate_com_o_gabarito(cenario, tratamento):
    _, controle = cenario
    _, quarentena = tratamento
    contagem = quarentena["motivo_quarentena"].value_counts().to_dict()
    for problema in ["duplicata", "conclusao_anterior_abertura", "status_inconsistente"]:
        esperado = (controle["tipo_problema"] == problema).sum()
        assert contagem[problema] == esperado
    assert set(contagem) == {"duplicata", "conclusao_anterior_abertura", "status_inconsistente"}


def test_departamentos_e_tipos_voltam_ao_catalogo(tratamento, catalogo):
    tratada, _ = tratamento
    assert set(tratada["departamento"]) == set(catalogo["departamento"])
    assert set(tratada["tipo_solicitacao"]) <= set(catalogo["tipo_solicitacao"])


def test_tratamento_recupera_os_valores_originais(tratamento, base_limpa):
    tratada, _ = tratamento
    original = base_limpa.set_index("id_solicitacao").loc[tratada["id_solicitacao"]].reset_index()
    assert (tratada["departamento"] == original["departamento"]).all()
    assert (tratada["tipo_solicitacao"] == original["tipo_solicitacao"]).all()
    assert (tratada["sla_horas"] == original["sla_horas"]).all()


def test_prioridade_inferida_confere_com_a_original(cenario, tratamento, base_limpa):
    _, controle = cenario
    tratada, _ = tratamento
    ids = set(controle.loc[controle["tipo_problema"] == "nulo_prioridade", "id_solicitacao"])
    recuperadas = tratada[tratada["id_solicitacao"].isin(ids)].set_index("id_solicitacao")
    originais = base_limpa.set_index("id_solicitacao").loc[recuperadas.index]
    assert len(recuperadas) == len(ids)
    assert (recuperadas["prioridade"] == originais["prioridade"]).all()


def test_campos_nulos_ficam_marcados(tratamento):
    tratada, _ = tratamento
    assert tratada[["solicitante", "responsavel", "canal_abertura", "prioridade"]].notna().all().all()
    assert (tratada["solicitante"] == "Não informado").sum() == 40


def test_campos_derivados(tratamento):
    tratada, _ = tratamento
    concluida = tratada["status"] == "Concluída"
    assert (tratada.loc[concluida, "tempo_atendimento_horas"] >= 0).all()
    assert tratada.loc[~concluida, "tempo_atendimento_horas"].isna().all()
    assert tratada.loc[concluida, "dentro_sla"].notna().all()
    assert tratada.loc[~concluida, "dentro_sla"].isna().all()
    assert tratada["mes_referencia"].str.fullmatch(r"\d{4}-\d{2}").all()


def test_atrasada_considera_pendentes_vencidas(tratamento, referencia):
    tratada, _ = tratamento
    pendentes = tratada[tratada["status"].isin(["Aberta", "Em andamento", "Aguardando terceiros"])]
    esperado = pendentes["data_limite"] < referencia
    assert (pendentes["atrasada"] == esperado).all()
    cancelada = tratada[tratada["status"] == "Cancelada"]
    assert not cancelada["atrasada"].any()


def test_validacao_detecta_problemas(tratamento, catalogo):
    tratada, _ = tratamento
    quebrada = tratada.copy()
    quebrada.loc[0, "departamento"] = "Fin."
    quebrada.loc[1, "id_solicitacao"] = quebrada.loc[2, "id_solicitacao"]
    falhas = validar(quebrada, catalogo)
    assert any("catálogo" in falha for falha in falhas)
    assert any("ids duplicados" in falha for falha in falhas)