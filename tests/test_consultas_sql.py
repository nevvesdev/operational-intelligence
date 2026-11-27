from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pytest

from src import config
from src.gerador import gerar_base_limpa, montar_catalogo
from src.imperfeicoes import aplicar_imperfeicoes
from src.tratamento import tratar

DIR_SQL = Path(__file__).resolve().parent.parent / "sql"
STATUS_PENDENTES = ["Aberta", "Em andamento", "Aguardando terceiros"]


@pytest.fixture(scope="module")
def dados():
    catalogo_completo = montar_catalogo()
    catalogo = catalogo_completo[["tipo_solicitacao", "departamento", "sla_horas"]]
    base = gerar_base_limpa(np.random.default_rng(config.SEMENTE), catalogo_completo)
    raw, _ = aplicar_imperfeicoes(base, np.random.default_rng(config.SEMENTE + 1))
    tratada, quarentena = tratar(raw, catalogo, pd.Timestamp(config.DATA_REFERENCIA))
    return raw, tratada, quarentena, catalogo


@pytest.fixture(scope="module")
def conexao(dados):
    raw, tratada, quarentena, catalogo = dados
    con = duckdb.connect()
    for nome, tabela in [
        ("bronze_solicitacoes", raw),
        ("silver_solicitacoes", tratada),
        ("silver_quarentena", quarentena),
        ("dim_tipo_solicitacao", catalogo),
    ]:
        con.register("origem", tabela)
        con.execute(f"CREATE TABLE {nome} AS SELECT * FROM origem")
        con.unregister("origem")
    modelo = (DIR_SQL / "03_modelo_analitico.sql").read_text(encoding="utf-8")
    comandos = [linha for linha in modelo.splitlines() if not linha.startswith("USE ")]
    con.execute("\n".join(comandos))
    return con


def executar(conexao, arquivo):
    texto = (DIR_SQL / "consultas" / arquivo).read_text(encoding="utf-8")
    comandos = [comando.strip() for comando in texto.split(";") if comando.strip()]
    return [conexao.execute(comando).df() for comando in comandos]


def test_atrasos_por_departamento(conexao, dados):
    _, tratada, _, _ = dados
    resultado = executar(conexao, "01_departamento_com_mais_atrasos.sql")[0]
    ativas = tratada[tratada["status"] != "Cancelada"]
    esperado = ativas.groupby("departamento")["atrasada"].sum()
    obtido = resultado.set_index("departamento")["solicitacoes_atrasadas"]
    assert (obtido.sort_index() == esperado.sort_index()).all()


def test_sla_geral_e_por_departamento(conexao, dados):
    _, tratada, _, _ = dados
    resultado = executar(conexao, "02_cumprimento_de_sla.sql")[0].set_index("departamento")
    concluidas = tratada[tratada["status"] == "Concluída"]
    geral = round(100 * concluidas["dentro_sla"].astype(bool).mean(), 1)
    assert resultado.loc["Geral", "pct_sla"] == geral
    por_departamento = (100 * concluidas.groupby("departamento")["dentro_sla"].apply(lambda s: s.astype(bool).mean())).round(1)
    for departamento, valor in por_departamento.items():
        assert resultado.loc[departamento, "pct_sla"] == valor


def test_tempo_medio_geral(conexao, dados):
    _, tratada, _, _ = dados
    resultado = executar(conexao, "03_tempo_medio_de_atendimento.sql")[0].set_index("departamento")
    esperado = round(tratada.loc[tratada["status"] == "Concluída", "tempo_atendimento_horas"].mean(), 1)
    assert resultado.loc["Geral", "tempo_medio_horas"] == esperado


def test_gargalos_ordenados_por_taxa_de_atraso(conexao):
    resultado = executar(conexao, "04_tipos_com_mais_gargalos.sql")[0]
    assert len(resultado) == 10
    assert resultado["pct_atraso"].is_monotonic_decreasing
    assert resultado.loc[0, "posicao"] == 1


def test_pendentes_batem_com_a_base(conexao, dados):
    _, tratada, _, _ = dados
    resultado = executar(conexao, "05_solicitacoes_pendentes.sql")[0].set_index("departamento")
    pendentes = tratada[tratada["status"].isin(STATUS_PENDENTES)]
    assert resultado.loc["Total", "pendentes"] == len(pendentes)
    assert resultado.loc["Total", "pendentes_atrasadas"] == pendentes["atrasada"].sum()
    assert resultado.index[-1] == "Total"


def test_duplicidade_encontra_as_duplicatas_injetadas(conexao):
    resumo, amostra = executar(conexao, "06_registros_duplicados.sql")
    esperado = round(config.TOTAL_SOLICITACOES * config.FRACAO_DUPLICATAS)
    assert resumo.loc[0, "duplicatas"] == esperado
    assert len(amostra) == 20


def test_evolucao_mensal_cobre_doze_meses(conexao, dados):
    _, tratada, _, _ = dados
    resultado = executar(conexao, "07_evolucao_mensal.sql")[0]
    assert len(resultado) == 12
    assert resultado["solicitacoes"].sum() == len(tratada)
    assert pd.isna(resultado.loc[0, "variacao_volume"])