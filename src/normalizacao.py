import re
import unicodedata

import pandas as pd

ALIASES_DEPARTAMENTO = {
    "Financeiro": ["financeiro", "fin", "financ"],
    "Suprimentos": ["suprimentos", "supr", "suprim"],
    "Operações": ["operações", "operacoes", "oper"],
    "Logística": ["logística", "logistica", "log"],
    "Administrativo": ["administrativo", "admin", "adm"],
    "Tecnologia": ["tecnologia", "tec", "ti"],
    "Gestão de Ativos": ["gestão de ativos", "gestao de ativos", "ativos"],
}


def chave_texto(valor):
    if pd.isna(valor):
        return None
    texto = unicodedata.normalize("NFD", str(valor))
    texto = "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")
    texto = texto.casefold().replace("_", " ").replace(".", " ")
    return re.sub(r"\s+", " ", texto).strip()


MAPA_DEPARTAMENTO = {
    chave_texto(alias): canonico
    for canonico, aliases in ALIASES_DEPARTAMENTO.items()
    for alias in aliases
}


def canonizar_departamento(valor):
    chave = chave_texto(valor)
    if chave is None:
        return None
    return MAPA_DEPARTAMENTO.get(chave)


def mapa_tipos(catalogo):
    return {chave_texto(tipo): tipo for tipo in catalogo["tipo_solicitacao"]}


def canonizar_tipo(valor, mapa):
    chave = chave_texto(valor)
    if chave is None:
        return None
    chave = re.sub(r"\s*-\s*urgente$", "", chave)
    return mapa.get(chave)