import streamlit as st
import pandas as pd
import altair as alt
from database import conectar


def mostrar_dashboard():

    st.title(" Dashboard Empresarial")

    conn = conectar()

    try:
        productos = pd.read_sql("SELECT * FROM productos", conn)
        ventas = pd.read_sql("SELECT * FROM ventas", conn)
    except:
        st.error("Error al cargar datos de la base de datos.")
        conn.close()
        return

    conn.close()

    if productos.empty:
        st.warning("No hay productos registrados.")
        return

    # LIMPIEZA DE DATOS
    productos["precio"] = pd.to_numeric(productos["precio"], errors="coerce").fillna(0)
    productos["costo"] = pd.to_numeric(productos["costo"], errors="coerce").fillna(0)
    productos["stock"] = pd.to_numeric(productos["stock"], errors="coerce").fillna(0)

    if not ventas.empty:
        ventas["total"] = pd.to_numeric(ventas["total"], errors="coerce").fillna(0)

        if "fecha" in ventas.columns:
            ventas["fecha"] = pd.to_datetime(ventas["fecha"], errors="coerce")

    # MÉTRICAS PRINCIPALES
    valor_inventario = (productos["costo"] * productos["stock"]).sum()
    total_ventas = ventas["total"].sum() if not ventas.empty else 0
    cantidad_productos = len(productos)
    total_stock = productos["stock"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Ventas Totales", f"₡{total_ventas:,.2f}")
    col2.metric("Valor Inventario", f"₡{valor_inventario:,.2f}")
    col3.metric("Productos", cantidad_productos)
    col4.metric("Stock Total", int(total_stock))

    st.divider()

    # GRÁFICO 1 — INVENTARIO POR PRODUCTO
    st.subheader("Inventario por Producto")

    graf_stock = alt.Chart(productos).mark_bar().encode(
        x=alt.X("nombre:N", sort="-y", title="Producto"),
        y=alt.Y("stock:Q", title="Stock"),
        tooltip=["nombre", "stock"]
    ).properties(
        height=400
    )

    st.altair_chart(graf_stock, use_container_width=True)

    st.divider()

    # GRÁFICO 2 — VENTAS MENSUALES
    if not ventas.empty and "fecha" in ventas.columns:

        ventas_mes = ventas.groupby(
            ventas["fecha"].dt.to_period("M")
        )["total"].sum().reset_index()

        ventas_mes["fecha"] = ventas_mes["fecha"].astype(str)

        st.subheader("Ventas Mensuales")

        graf_ventas = alt.Chart(ventas_mes).mark_line(point=True).encode(
            x=alt.X("fecha:N", title="Mes"),
            y=alt.Y("total:Q", title="Ventas ₡"),
            tooltip=["fecha", "total"]
        ).properties(
            height=400
        )

        st.altair_chart(graf_ventas, use_container_width=True)

    else:

        st.info("No hay datos de ventas para mostrar gráfico.")

    st.divider()

    # GRÁFICO 3 — PRODUCTOS MÁS CAROS
    st.subheader("Productos Más Caros")

    top_caros = productos.sort_values("precio", ascending=False).head(10)

    graf_precios = alt.Chart(top_caros).mark_bar().encode(
        x=alt.X("precio:Q", title="Precio ₡"),
        y=alt.Y("nombre:N", sort="-x", title="Producto"),
        tooltip=["nombre", "precio"]
    ).properties(
        height=400
    )

    st.altair_chart(graf_precios, use_container_width=True)

    st.divider()

    # TABLA RESUMEN

    st.subheader("Resumen de Productos")

    resumen = productos[["nombre", "precio", "costo", "stock"]]

    st.dataframe(resumen, use_container_width=True)