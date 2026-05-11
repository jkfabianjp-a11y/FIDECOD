import streamlit as st
import pandas as pd
import numpy as np
from database import conectar
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from datetime import timedelta

def prediccion_ventas():
    st.title("IA Predictiva")

    conn = conectar()


    # PREDICCIÓN DE VENTAS
    try:
        ventas = pd.read_sql("SELECT fecha, total FROM facturas", conn)
    except Exception as e:
        st.error("No se pudieron cargar las ventas desde la base de datos.")
        st.code(str(e))
        return

    if ventas.empty:
        st.warning("Aún no hay ventas registradas.")
        return
    ventas["fecha"] = pd.to_datetime(ventas["fecha"], errors="coerce")
    ventas = ventas.dropna(subset=["fecha", "total"]).sort_values("fecha")

    ventas["dia"] = (ventas["fecha"] - ventas["fecha"].min()).dt.days
    X = ventas[["dia"]]
    y = ventas["total"]

    modelo = LinearRegression()
    modelo.fit(X, y)

    # Predicción para 30 días futuros
    dias_futuros = np.arange(ventas["dia"].max() + 1, ventas["dia"].max() + 31)
    predicciones = modelo.predict(dias_futuros.reshape(-1, 1))
    fechas_futuras = [ventas["fecha"].max() + timedelta(days=i) for i in range(1, 31)]

    st.subheader("Predicción de ventas para 30 días")
    total_estimado = predicciones.sum()
    st.metric("Ventas estimadas próximo mes", f"₡{total_estimado:,.2f}")

    # Gráfico de ventas
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(ventas["fecha"], ventas["total"], marker='o', label="Ventas reales", color="blue")
    ax.plot(fechas_futuras, predicciones, marker='x', linestyle="--", color="orange", label="Predicción")
    ax.set_title("Predicción de Ventas")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Monto de Ventas (₡)")
    ax.legend()
    ax.grid(True)
    fig.autofmt_xdate()
    plt.tight_layout()

    st.pyplot(fig)
    st.divider()


    # PREDICCIÓN DE STOCK
    st.subheader("Predicción de Stock")
    try:
        productos = pd.read_sql("SELECT nombre, stock FROM productos", conn)
    except:
        st.warning("No se pudieron analizar productos.")
        return

    if productos.empty:
        st.info("No hay productos registrados.")
        return

    ventas_promedio = ventas["total"].mean()
    alerta = []

    for _, p in productos.iterrows():
        consumo_estimado = ventas_promedio / max(len(productos),1)
        if p["stock"] < consumo_estimado * 10:
            alerta.append({"Producto": p["nombre"], "Stock Actual": p["stock"], "Consumo Estimado": consumo_estimado})

    if alerta:
        st.error("Productos que podrían quedarse sin stock pronto:")
        alerta_df = pd.DataFrame(alerta)
        st.dataframe(alerta_df)
    else:
        st.success("El inventario parece estable.")

    conn.close()