import numpy as np

from src import config
from src.exportacao import salvar_csv, salvar_excel
from src.gerador import gerar_base_limpa, montar_catalogo
from src.imperfeicoes import aplicar_imperfeicoes


def main():
    rng = np.random.default_rng(config.SEMENTE)
    catalogo = montar_catalogo()
    base_limpa = gerar_base_limpa(rng, catalogo)
    base_raw, controle = aplicar_imperfeicoes(base_limpa, rng)
    catalogo_saida = catalogo[["tipo_solicitacao", "departamento", "sla_horas"]]

    salvar_csv(base_raw, config.DIR_RAW / "solicitacoes_raw.csv")
    salvar_csv(catalogo_saida, config.DIR_RAW / "catalogo_tipos.csv")
    salvar_csv(controle, config.DIR_RAW / "controle_imperfeicoes.csv")
    salvar_excel(
        {"solicitacoes": base_raw, "catalogo_tipos": catalogo_saida},
        config.DIR_RAW / "base_operacional_raw.xlsx",
    )

    print(f"Registros gerados: {len(base_raw)}")
    print(f"Base limpa: {len(base_limpa)}")
    print("Imperfeições injetadas:")
    print(controle["tipo_problema"].value_counts().to_string())


if __name__ == "__main__":
    main()