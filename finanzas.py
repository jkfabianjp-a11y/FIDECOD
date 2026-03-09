import streamlit as st
import pandas as pd
from database import conectar


def herramientas_financieras():

    st.title("📊 Herramientas Financieras Estratégicas")

    conn = conectar()
    c = conn.cursor()


    # REGISTRAR COSTOS FIJOS

    st.subheader("💰 Costos Fijos Mensuales")

    with st.form("form_costos"):
        descripcion = st.text_input("Descripción del costo")
        monto = st.number_input("Monto", min_value=0.0)

        submit = st.form_submit_button("Agregar Costo")

        if submit:
            if monto > 0:
                c.execute("""
                    INSERT INTO costos_fijos (descripcion, monto)
                    VALUES (?, ?)
                """, (descripcion, monto))
                conn.commit()
                st.success("Costo agregado correctamente.")
                st.rerun()

    # Mostrar costos actuales
    costos_df = pd.read_sql("SELECT * FROM costos_fijos", conn)

    total_costos_fijos = costos_df["monto"].sum() if not costos_df.empty else 0

    st.write(f"### Total Costos Fijos: ₡{total_costos_fijos:,.2f}")

    st.divider()


    # PUNTO DE EQUILIBRIO

    st.subheader("📈 Punto de Equilibrio")

    productos = pd.read_sql("SELECT * FROM productos", conn)

    if productos.empty:
        st.warning("No hay productos registrados.")
        conn.close()
        return

    # Calcular margen promedio
    productos["margen"] = productos["precio"] - productos["costo"]
    margen_promedio = productos["margen"].mean()

    if margen_promedio <= 0:
        st.error("El margen promedio es 0 o negativo. Revisa precios y costos.")
        conn.close()
        return

    if total_costos_fijos <= 0:
        st.warning("Agrega costos fijos para calcular el punto de equilibrio.")
        conn.close()
        return

    punto_equilibrio = total_costos_fijos / margen_promedio

    st.write(f"Debes vender aproximadamente **{punto_equilibrio:.2f} unidades** para cubrir costos.")

    conn.close()
    