import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime

def exportar_reporte_excel():

    st.subheader("📁 Exportar Reporte Financiero en Excel")

    conn = conectar()

    # CARGAR DATOS DE VENTAS
    ventas = pd.read_sql("""
        SELECT v.id, v.producto_id, p.nombre AS producto, v.cantidad, v.total, v.fecha
        FROM ventas v
        LEFT JOIN productos p ON v.producto_id = p.id
        ORDER BY v.fecha ASC
    """, conn)

    conn.close()

    if ventas.empty:
        st.warning("No hay datos para exportar.")
        return

    ventas["fecha"] = pd.to_datetime(ventas["fecha"], errors="coerce")
    ventas["fecha"] = ventas["fecha"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # CALCULAR RESUMEN
    resumen_productos = ventas.groupby("producto").agg(
        unidades_vendidas=pd.NamedAgg(column="cantidad", aggfunc="sum"),
        total_vendido=pd.NamedAgg(column="total", aggfunc="sum")
    ).reset_index()

    total_general = ventas["total"].sum()
    subtotal_general = total_general / 1.13  #IVA 13%
    iva_total = total_general - subtotal_general

    st.markdown(f"**Subtotal: ₡{subtotal_general:,.2f} | IVA Total: ₡{iva_total:,.2f} | Total General Vendido: ₡{total_general:,.2f}**")
    st.subheader("Detalle de Ventas")
    st.dataframe(ventas)

    st.subheader("Resumen por Producto")
    st.dataframe(resumen_productos)

    # AGREGAR FILA DE TOTAL EN DETALLE VENTAS
    fila_total = pd.DataFrame({
        "id": [""],
        "producto_id": [""],
        "producto": ["TOTAL GENERAL"],
        "cantidad": [ventas["cantidad"].sum()],
        "total": [total_general],
        "fecha": [""]
    })
    ventas_excel = pd.concat([ventas, fila_total], ignore_index=True)

    # EXPORTAR A EXCEL
    nombre_archivo = f"reporte_financiero_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    with pd.ExcelWriter(nombre_archivo, engine="openpyxl") as writer:
        ventas_excel.to_excel(writer, sheet_name="Detalle Ventas", index=False)
        resumen_productos.to_excel(writer, sheet_name="Resumen Productos", index=False)

        totales_df = pd.DataFrame({
            "Concepto": ["Subtotal", "IVA Total", "Total General Vendido"],
            "Monto": [subtotal_general, iva_total, total_general]
        })
        totales_df.to_excel(writer, sheet_name="Totales", index=False)

    # Botón de descarga
    with open(nombre_archivo, "rb") as f:
        st.download_button(
            label="⬇ Descargar Excel",
            data=f,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success("Reporte listo para descargar.")