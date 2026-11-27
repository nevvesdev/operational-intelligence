import pandas as pd

from src import config
from src.avaliacao import comparar_com_gabarito, sla_ingenuo
from src.diagnostico import diagnosticar
from src.exportacao import salvar_csv, salvar_csv_padrao
from src.leitura import ler_catalogo, ler_controle, ler_solicitacoes
from src.tratamento import tratar
from src.validacao import exigir_valida


def main():
    referencia = pd.Timestamp(config.DATA_REFERENCIA)
    raw = ler_solicitacoes(config.DIR_RAW / "solicitacoes_raw.csv")
    catalogo = ler_catalogo(config.DIR_RAW / "catalogo_tipos.csv")
    controle = ler_controle(config.DIR_RAW / "controle_imperfeicoes.csv")

    detectados = diagnosticar(raw, catalogo)
    relatorio = comparar_com_gabarito(detectados, controle)
    tratada, quarentena = tratar(raw, catalogo, referencia)
    exigir_valida(tratada, catalogo)

    salvar_csv_padrao(tratada, config.DIR_PROCESSED / "solicitacoes_tratadas.csv")
    salvar_csv_padrao(quarentena, config.DIR_PROCESSED / "solicitacoes_quarentena.csv")
    salvar_csv(relatorio, config.RAIZ / "reports" / "relatorio_qualidade.csv")

    dentro, fora, sem_data = sla_ingenuo(raw)
    sla_bruto = dentro / (dentro + fora)
    sla_tratado = tratada["dentro_sla"].dropna().astype(bool).mean()

    print(f"Registros brutos: {len(raw)}")
    print(f"Registros tratados: {len(tratada)}")
    print(f"Registros em quarentena: {len(quarentena)}")
    print(quarentena["motivo_quarentena"].value_counts().to_string())
    print()
    print(relatorio.to_string(index=False))
    print()
    print(f"SLA ingênuo (base bruta): {sla_bruto:.1%} ({dentro} sim, {fora} não, {sem_data} em branco)")
    print(f"SLA com dados tratados: {sla_tratado:.1%}")


if __name__ == "__main__":
    main()