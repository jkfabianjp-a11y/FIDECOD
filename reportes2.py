import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime

def exportar_reporte_excel():

    st.subheader("📊 Exportar Reporte Financiero en Excel")

    conn = conectar()

    ventas = pd.read_sql("SELECT * FROM ventas", conn)
    productos = pd.read_sql("SELECT * FROM productos", conn)

    conn.close()

    if ventas.empty:
        st.warning("No hay datos para exportar.")
        return

    ventas["fecha"] = pd.to_datetime(ventas["fecha"], errors="coerce")

    ventas_mes = ventas.groupby(
        ventas["fecha"].dt.to_period("M")
    )["total"].sum().reset_index()

    ventas_mes["fecha"] = ventas_mes["fecha"].astype(str)

    nombre_archivo = f"reporte_financiero_{datetime.now().strftime('%Y%m%d')}.xlsx"

    ventas_mes.to_excel(nombre_archivo, index=False)

    with open(nombre_archivo, "rb") as f:
        st.download_button(
            label="⬇ Descargar Excel",
            data=f,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )