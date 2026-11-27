import shutil

from src import config
from src.exportacao import salvar_csv_padrao
from src.leitura import ler_catalogo, ler_solicitacoes


def main():
    destino = config.DIR_PROCESSED / "databricks"
    destino.mkdir(parents=True, exist_ok=True)

    bronze = ler_solicitacoes(config.DIR_RAW / "solicitacoes_raw.csv")
    salvar_csv_padrao(bronze, destino / "bronze_solicitacoes.csv")

    catalogo = ler_catalogo(config.DIR_RAW / "catalogo_tipos.csv")
    salvar_csv_padrao(catalogo, destino / "catalogo_tipos.csv")

    for nome in ["solicitacoes_tratadas", "solicitacoes_quarentena"]:
        shutil.copy(config.DIR_PROCESSED / f"{nome}.csv", destino / f"{nome}.csv")

    for arquivo in sorted(destino.glob("*.csv")):
        print(arquivo.name)


if __name__ == "__main__":
    main()