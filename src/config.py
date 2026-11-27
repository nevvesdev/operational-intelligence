from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"

SEMENTE = 42
TOTAL_SOLICITACOES = 8000
DATA_INICIO = "2025-12-01"
DATA_REFERENCIA = "2026-11-26 00:00:00"

DEPARTAMENTOS = {
    "FIN": "Financeiro",
    "SUP": "Suprimentos",
    "OPE": "Operações",
    "LOG": "Logística",
    "ADM": "Administrativo",
    "TEC": "Tecnologia",
    "ATV": "Gestão de Ativos",
}

PESO_DEPARTAMENTO = {
    "FIN": 0.20,
    "SUP": 0.17,
    "OPE": 0.22,
    "LOG": 0.14,
    "ADM": 0.08,
    "TEC": 0.12,
    "ATV": 0.07,
}

CATALOGO = [
    ("FIN", "Emissão de nota fiscal", 24, 4),
    ("FIN", "Conciliação de pagamento", 48, 3),
    ("FIN", "Ajuste de faturamento", 72, 2),
    ("FIN", "Estorno", 96, 1),
    ("SUP", "Cotação de fornecedor", 72, 3),
    ("SUP", "Pedido de compra", 48, 4),
    ("SUP", "Cadastro de fornecedor", 96, 2),
    ("SUP", "Reposição de estoque", 24, 3),
    ("OPE", "Registro de pesagem", 8, 5),
    ("OPE", "Correção de apontamento", 24, 3),
    ("OPE", "Liberação de carga", 12, 3),
    ("OPE", "Revisão de procedimento", 120, 1),
    ("LOG", "Agendamento de transporte", 24, 4),
    ("LOG", "Roteirização", 48, 3),
    ("LOG", "Ocorrência de entrega", 12, 3),
    ("LOG", "Devolução de mercadoria", 96, 1),
    ("ADM", "Solicitação de material", 72, 4),
    ("ADM", "Contrato e documentos", 120, 2),
    ("ADM", "Reembolso de despesa", 96, 3),
    ("TEC", "Acesso a sistema", 8, 4),
    ("TEC", "Incidente em sistema", 12, 3),
    ("TEC", "Nova funcionalidade", 240, 1),
    ("TEC", "Extração de relatório", 48, 3),
    ("ATV", "Manutenção corretiva", 48, 4),
    ("ATV", "Manutenção preventiva", 120, 3),
    ("ATV", "Baixa de ativo", 168, 1),
]

PRIORIDADES = ["Crítica", "Alta", "Média", "Baixa"]

FATOR_PRIORIDADE = {
    "Crítica": 0.5,
    "Alta": 0.75,
    "Média": 1.0,
    "Baixa": 1.25,
}

PROB_PRIORIDADE_PADRAO = [0.08, 0.22, 0.50, 0.20]

PROB_PRIORIDADE_DEPARTAMENTO = {
    "TEC": [0.15, 0.30, 0.40, 0.15],
    "OPE": [0.12, 0.28, 0.45, 0.15],
}

PROB_ATRASO_DEPARTAMENTO = {
    "FIN": 0.22,
    "SUP": 0.30,
    "OPE": 0.15,
    "LOG": 0.28,
    "ADM": 0.35,
    "TEC": 0.18,
    "ATV": 0.40,
}

ACRESCIMO_ATRASO_TIPO = {
    "Cotação de fornecedor": 0.15,
    "Baixa de ativo": 0.15,
    "Manutenção corretiva": 0.10,
    "Devolução de mercadoria": 0.12,
    "Estorno": 0.10,
    "Nova funcionalidade": 0.08,
}

ACRESCIMO_ATRASO_CRITICA = 0.06
LIMITE_PROB_ATRASO = (0.02, 0.85)

PROB_BACKLOG_PADRAO = 0.012
PROB_BACKLOG_DEPARTAMENTO = {"ADM": 0.03, "ATV": 0.03}
PROB_CANCELAMENTO = 0.03
DIAS_PARA_BACKLOG = 30

PESO_DIA_SEMANA = [1.0, 1.0, 1.0, 1.0, 1.0, 0.12, 0.06]

SAZONALIDADE_MENSAL = {
    "OPE": {
        1: 0.7, 2: 0.7, 3: 0.8, 4: 1.3, 5: 1.4, 6: 1.4,
        7: 1.4, 8: 1.4, 9: 1.4, 10: 1.3, 11: 1.2, 12: 0.8,
    },
    "FIN": {12: 1.2, 3: 1.1},
    "LOG": {4: 1.15, 5: 1.2, 6: 1.2, 7: 1.2, 8: 1.2, 9: 1.2, 10: 1.15},
}

CRESCIMENTO_MENSAL = 0.02
DIA_PICO_FINANCEIRO = 25
FATOR_PICO_FINANCEIRO = 2.0

HORAS = list(range(7, 19))
PESO_HORAS = [3, 6, 8, 8, 6, 5, 6, 8, 8, 6, 4, 2]

CANAIS = ["Sistema", "E-mail", "Planilha", "Telefone"]
PROB_CANAIS = [0.45, 0.30, 0.15, 0.10]

OBSERVACOES = [
    "Aguardando aprovação do gestor",
    "Documento anexado incompleto",
    "Reaberta a pedido do solicitante",
    "Dependência de fornecedor externo",
    "Urgência informada por telefone",
    "Solicitação encaminhada a outra área",
]
PROB_OBSERVACAO = 0.12

SOLICITANTES_POR_DEPARTAMENTO = 40
ANALISTAS_POR_DEPARTAMENTO = 6

FRACAO_DUPLICATAS = 0.015
FRACAO_CONCLUSAO_INVALIDA = 0.006
FRACAO_STATUS_INCONSISTENTE = 0.008
FRACAO_DEPARTAMENTO_VARIADO = 0.03
FRACAO_NULOS_POR_CAMPO = 0.005
FRACAO_TIPO_FORA_CATALOGO = 0.007

CAMPOS_COM_NULOS = ["solicitante", "responsavel", "prioridade", "canal_abertura"]

STATUS_PENDENTES = ["Aberta", "Em andamento", "Aguardando terceiros"]

VARIACOES_DEPARTAMENTO = {
    "Financeiro": ["financeiro", "FINANCEIRO", "Financeiro ", " Financeiro", "Fin.", "Financ"],
    "Suprimentos": ["suprimentos", "SUPRIMENTOS", "Suprimentos ", " Suprimentos", "Supr.", "Suprim"],
    "Operações": ["operações", "OPERAÇÕES", "Operações ", " Operações", "Oper.", "Operacoes"],
    "Logística": ["logística", "LOGÍSTICA", "Logística ", " Logística", "Log.", "Logistica"],
    "Administrativo": ["administrativo", "ADMINISTRATIVO", "Administrativo ", " Administrativo", "Admin.", "Adm"],
    "Tecnologia": ["tecnologia", "TECNOLOGIA", "Tecnologia ", " Tecnologia", "Tec.", "TI"],
    "Gestão de Ativos": ["gestão de ativos", "GESTÃO DE ATIVOS", "Gestão de Ativos ", " Gestão de Ativos", "Ativos", "Gestao de Ativos"],
}

COLUNAS_BASE = [
    "id_solicitacao",
    "data_abertura",
    "data_conclusao",
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
    "observacao",
]