from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pytest

from src import config
from src.gerador import gerar_base_limpa, montar_catalogo
from src.imperfeicoes import aplicar_imperfeicoes
from src.indicadores import calcular_todos
from src.tratamento import tratar

DIR_SQL = Path(__file__).resolve().parent.parent / "sql"
COLUNAS_NUMERICAS = [
    "solicitacoes",
    "concluidas",
    "pendentes",
    "dentro_do_prazo",
    "atrasadas",
    "pendentes_atrasadas",
    "tempo_medio_horas",
    "pct_sla",
    "taxa_atraso",
]


@pytest.fixture(scope="module")
def cenario():
    catalogo_completo = montar_catalogo()
    catalogo = catalogo_completo[["tipo_solicitacao", "departamento", "sla_horas"]]
    base = gerar_base_limpa(np.random.default_rng(config.SEMENTE), catalogo_completo)
    raw, _ = aplicar_imperfeicoes(base, np.random.default_rng(config.SEMENTE + 1))
    tratada, quarentena = tratar(raw, catalogo, pd.Timestamp(config.DATA_REFERENCIA))
    return raw, tratada, quarentena, catalogo


@pytest.fixture(scope="module")
def python_kpis(cenario):
    _, tratada, quarentena, _ = cenario
    return calcular_todos(tratada, quarentena)


@pytest.fixture(scope="module")
def conexao(cenario):
    raw, tratada, quarentena, catalogo = cenario
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
    for arquivo in ["03_modelo_analitico.sql", "04_camada_gold.sql"]:
        texto = (DIR_SQL / arquivo).read_text(encoding="utf-8")
        comandos = [linha for linha in texto.splitlines() if not linha.startswith("USE ")]
        for comando in "\n".join(comandos).split(";"):
            if comando.strip():
                con.execute(comando)
    return con


def comparar(sql, python, chave):
    sql = sql.sort_values(chave).reset_index(drop=True)
    python = python.sort_values(chave).reset_index(drop=True)
    assert list(sql[chave]) == list(python[chave])
    for coluna in COLUNAS_NUMERICAS:
        diferenca = (sql[coluna].astype(float) - python[coluna].astype(float)).abs()
        assert (diferenca.fillna(0) <= 0.1).all(), coluna
        assert sql[coluna].isna().equals(python[coluna].isna()), coluna
    assert list(sql["status_sla"]) == list(python["status_sla"])


def test_geral_sql_igual_ao_python(conexao, python_kpis):
    comparar(conexao.execute("SELECT * FROM gold_kpi_geral").df(), python_kpis["geral"], "escopo")


def test_departamento_sql_igual_ao_python(conexao, python_kpis):
    comparar(conexao.execute("SELECT * FROM gold_kpi_departamento").df(), python_kpis["departamento"], "departamento")


def test_tipo_sql_igual_ao_python(conexao, python_kpis):
    sql = conexao.execute("SELECT * FROM gold_kpi_tipo").df()
    comparar(sql, python_kpis["tipo"], "tipo_solicitacao")
    ordenado = sql.sort_values("tipo_solicitacao").reset_index(drop=True)
    esperado = python_kpis["tipo"].sort_values("tipo_solicitacao").reset_index(drop=True)
    assert list(ordenado["posicao_gargalo"]) == list(esperado["posicao_gargalo"])


def test_mensal_sql_igual_ao_python(conexao, python_kpis):
    sql = conexao.execute("SELECT * FROM gold_kpi_mensal").df()
    sql["mes_abertura"] = sql["mes_abertura"].astype(str).str[:10]
    python = python_kpis["mensal"].copy()
    python["mes_abertura"] = python["mes_abertura"].astype(str)
    comparar(sql, python, "mes_abertura")
    assert list(sql.sort_values("mes_abertura")["mes_parcial"]) == list(python.sort_values("mes_abertura")["mes_parcial"])


def test_qualidade_sql_igual_ao_python(conexao, python_kpis):
    sql = conexao.execute("SELECT * FROM gold_qualidade").df().set_index("indicador")["valor"]
    python = python_kpis["qualidade"].set_index("indicador")["valor"]
    assert set(sql.index) == set(python.index)
    for indicador in python.index:
        assert abs(float(sql[indicador]) - float(python[indicador])) < 0.01, indicador