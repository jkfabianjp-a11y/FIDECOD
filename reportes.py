import pandas as pd
from database import conectar

def exportar_csv():
    conn = conectar()
    df = pd.read_sql("SELECT * FROM ventas", conn)
    conn.close()
    df.to_csv("reporte_ventas.csv", index=False)