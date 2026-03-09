import streamlit as st
import pandas as pd
from database import conectar

def mostrar_dashboard():

    st.title("📊 Dashboard Empresarial")

    conn = conectar()

    productos = pd.read_sql("SELECT * FROM productos", conn)
    ventas = pd.read_sql("SELECT * FROM ventas", conn)

    conn.close()

    if productos.empty:
        st.warning("No hay productos.")
        return

    # Forzar tipos correctos
    productos["precio"] = pd.to_numeric(productos["precio"], errors="coerce")
    productos["costo"] = pd.to_numeric(productos["costo"], errors="coerce")
    productos["stock"] = pd.to_numeric(productos["stock"], errors="coerce")

    ventas["total"] = pd.to_numeric(ventas["total"], errors="coerce")

    productos = productos.dropna()
    ventas = ventas.dropna()


    # MÉTRICAS PRINCIPALES


    valor_inventario = (productos["costo"] * productos["stock"]).sum()
    total_ventas = ventas["total"].sum()
    cantidad_productos = len(productos)

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Ventas Totales", f"₡{round(total_ventas,2)}")
    col2.metric("📦 Valor Inventario", f"₡{round(valor_inventario,2)}")
    col3.metric("🛍 Productos Registrados", cantidad_productos)

    st.divider()




    if not ventas.empty:

        ventas["fecha"] = pd.to_datetime(ventas["fecha"], errors="coerce")

        ventas_mes = ventas.groupby(
            ventas["fecha"].dt.to_period("M")
        )["total"].sum()

        st.subheader("📈 Ventas Mensuales")
        st.line_chart(ventas_mes)