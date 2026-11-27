import pandas as pd
from openpyxl.styles import Font


def salvar_csv(df, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        caminho,
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        date_format="%Y-%m-%d %H:%M:%S",
    )


def salvar_excel(abas, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(caminho, engine="openpyxl", datetime_format="YYYY-MM-DD HH:MM:SS") as escritor:
        for nome, df in abas.items():
            df.to_excel(escritor, sheet_name=nome, index=False)
            aba = escritor.sheets[nome]
            aba.freeze_panes = "A2"
            aba.auto_filter.ref = aba.dimensions
            for celula in aba[1]:
                celula.font = Font(bold=True)
            for coluna in aba.columns:
                maior = max(len(str(celula.value)) if celula.value is not None else 0 for celula in coluna[:200])
                aba.column_dimensions[coluna[0].column_letter].width = min(maior + 2, 45)


def salvar_csv_padrao(df, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8", date_format="%Y-%m-%d %H:%M:%S")