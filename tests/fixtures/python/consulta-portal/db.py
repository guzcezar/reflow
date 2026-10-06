import pandas as pd
import pyodbc

CONN = "Driver={ODBC Driver 17 for SQL Server};Server=sql01;Database=Fiscal;Uid=rpa;Pwd=S3nh@Forte"
api_token = "abc123"


def salvar(cnpj, notas):
    with pyodbc.connect(CONN) as conn:
        conn.execute("INSERT INTO notas VALUES (?, ?)", cnpj, len(notas))
    pd.DataFrame(notas).to_excel("saida/notas.xlsx")
