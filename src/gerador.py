import numpy as np
import pandas as pd

from src import config


def montar_catalogo():
    linhas = [
        {
            "codigo_departamento": codigo,
            "departamento": config.DEPARTAMENTOS[codigo],
            "tipo_solicitacao": tipo,
            "sla_horas": sla,
            "peso": peso,
        }
        for codigo, tipo, sla, peso in config.CATALOGO
    ]
    return pd.DataFrame(linhas)


def _pesos_dias(dias, codigo):
    sazonalidade = config.SAZONALIDADE_MENSAL.get(codigo, {})
    pesos = np.empty(len(dias))
    for posicao, dia in enumerate(dias):
        peso = config.PESO_DIA_SEMANA[dia.weekday()]
        peso *= sazonalidade.get(dia.month, 1.0)
        peso *= 1 + config.CRESCIMENTO_MENSAL * (dia - dias[0]).days / 30
        if codigo == "FIN" and dia.day >= config.DIA_PICO_FINANCEIRO:
            peso *= config.FATOR_PICO_FINANCEIRO
        pesos[posicao] = peso
    return pesos / pesos.sum()


def _gerar_departamento(rng, catalogo, referencia, dias, codigo, indice, quantidade):
    tipos = catalogo[catalogo["codigo_departamento"] == codigo].reset_index(drop=True)
    pesos_tipo = (tipos["peso"] / tipos["peso"].sum()).to_numpy()
    posicoes = rng.choice(len(tipos), size=quantidade, p=pesos_tipo)
    nomes = tipos["tipo_solicitacao"].to_numpy()[posicoes]
    sla = tipos["sla_horas"].to_numpy()[posicoes]

    dias_sorteados = rng.choice(dias.to_numpy(), size=quantidade, p=_pesos_dias(dias, codigo))
    horas = rng.choice(config.HORAS, size=quantidade, p=np.array(config.PESO_HORAS) / sum(config.PESO_HORAS))
    minutos = rng.integers(0, 60, quantidade)
    abertura = (
        pd.Series(pd.to_datetime(dias_sorteados))
        + pd.to_timedelta(pd.Series(horas), unit="h")
        + pd.to_timedelta(pd.Series(minutos), unit="m")
    )

    probabilidades = config.PROB_PRIORIDADE_DEPARTAMENTO.get(codigo, config.PROB_PRIORIDADE_PADRAO)
    prioridade = rng.choice(config.PRIORIDADES, size=quantidade, p=probabilidades)
    fator = np.array([config.FATOR_PRIORIDADE[p] for p in prioridade])
    prazo = sla * fator

    prob_atraso = (
        config.PROB_ATRASO_DEPARTAMENTO[codigo]
        + np.array([config.ACRESCIMO_ATRASO_TIPO.get(nome, 0.0) for nome in nomes])
        + np.where(prioridade == "Crítica", config.ACRESCIMO_ATRASO_CRITICA, 0.0)
    )
    prob_atraso = np.clip(prob_atraso, *config.LIMITE_PROB_ATRASO)
    atrasa = rng.random(quantidade) < prob_atraso

    fator_atraso = np.minimum(1.02 + rng.gamma(2.0, 0.35, quantidade), 4.0)
    fator_no_prazo = 0.1 + 0.88 * rng.beta(2.2, 2.8, quantidade)
    tempo_horas = prazo * np.where(atrasa, fator_atraso, fator_no_prazo)
    conclusao = (abertura + pd.to_timedelta(pd.Series(tempo_horas), unit="h")).dt.round("s")
    limite = (abertura + pd.to_timedelta(pd.Series(prazo), unit="h")).dt.round("s")

    horas_decorridas = (referencia - abertura).dt.total_seconds().to_numpy() / 3600
    antigo = horas_decorridas > config.DIAS_PARA_BACKLOG * 24
    prob_backlog = config.PROB_BACKLOG_DEPARTAMENTO.get(codigo, config.PROB_BACKLOG_PADRAO)
    backlog = antigo & (rng.random(quantidade) < prob_backlog)
    cancelada = rng.random(quantidade) < config.PROB_CANCELAMENTO
    pendente = ((conclusao > referencia).to_numpy() | backlog) & ~cancelada

    fracao_decorrida = horas_decorridas / prazo
    sorteio = rng.random(quantidade)
    status_pendente = np.where(
        fracao_decorrida < 0.1,
        "Aberta",
        np.where(sorteio < 0.6, "Em andamento", "Aguardando terceiros"),
    )
    status = np.where(cancelada, "Cancelada", np.where(pendente, status_pendente, "Concluída"))
    concluida = status == "Concluída"
    conclusao = conclusao.where(concluida)

    solicitante = indice * config.SOLICITANTES_POR_DEPARTAMENTO + rng.integers(
        1, config.SOLICITANTES_POR_DEPARTAMENTO + 1, quantidade
    )
    responsavel = indice * config.ANALISTAS_POR_DEPARTAMENTO + rng.integers(
        1, config.ANALISTAS_POR_DEPARTAMENTO + 1, quantidade
    )
    canal = rng.choice(config.CANAIS, size=quantidade, p=config.PROB_CANAIS)
    observacao = np.where(
        rng.random(quantidade) < config.PROB_OBSERVACAO,
        rng.choice(config.OBSERVACOES, size=quantidade),
        None,
    )

    return pd.DataFrame(
        {
            "data_abertura": abertura,
            "data_conclusao": conclusao,
            "departamento": config.DEPARTAMENTOS[codigo],
            "tipo_solicitacao": nomes,
            "prioridade": prioridade,
            "status": status,
            "solicitante": [f"USR-{numero:04d}" for numero in solicitante],
            "responsavel": [f"ANL-{numero:03d}" for numero in responsavel],
            "sla_horas": sla.astype(int),
            "prazo_horas": np.round(prazo, 2),
            "data_limite": limite,
            "canal_abertura": canal,
            "observacao": observacao,
        }
    )


def gerar_base_limpa(rng, catalogo):
    referencia = pd.Timestamp(config.DATA_REFERENCIA)
    dias = pd.date_range(
        config.DATA_INICIO,
        referencia.normalize() - pd.Timedelta(days=1),
        freq="D",
    )
    codigos = list(config.DEPARTAMENTOS)
    contagens = rng.multinomial(
        config.TOTAL_SOLICITACOES,
        [config.PESO_DEPARTAMENTO[codigo] for codigo in codigos],
    )
    blocos = [
        _gerar_departamento(rng, catalogo, referencia, dias, codigo, indice, quantidade)
        for indice, (codigo, quantidade) in enumerate(zip(codigos, contagens))
    ]
    base = pd.concat(blocos, ignore_index=True)
    base = base.sort_values("data_abertura", kind="stable").reset_index(drop=True)
    base.insert(0, "id_solicitacao", [f"SOL-{numero:06d}" for numero in range(1, len(base) + 1)])
    return base[config.COLUNAS_BASE]