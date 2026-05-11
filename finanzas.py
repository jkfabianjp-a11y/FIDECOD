import streamlit as st
import pandas as pd
from database import conectar

def herramientas_financieras():

    st.title("Herramientas Financieras Estratégicas")

    conn = conectar()
    c = conn.cursor()

    # REGISTRAR COSTOS FIJOS
    st.subheader("Costos Fijos Mensuales")

    with st.form("form_costos"):
        descripcion = st.text_input("Descripción del costo")
        monto = st.number_input("Monto", min_value=0.0, step=0.01)

        submit = st.form_submit_button("Agregar Costo")

        if submit:
            if descripcion.strip() == "":
                st.error("La descripción no puede estar vacía.")
            elif monto <= 0:
                st.error("El monto debe ser mayor a 0.")
            else:
                # Guardar en base de datos
                c.execute("""
                    INSERT INTO costos_fijos (descripcion, monto)
                    VALUES (?, ?)
                """, (descripcion, monto))
                conn.commit()
                st.success("Costo agregado correctamente.")
                st.rerun()

    # MOSTRAR COSTOS FIJOS
    costos_df = pd.read_sql("SELECT * FROM costos_fijos", conn)

    if costos_df.empty:
        st.info("No hay costos fijos registrados.")
    else:
        st.subheader("📋 Lista de Costos Fijos")
        st.dataframe(costos_df)

        total_costos_fijos = costos_df["monto"].sum()
        st.markdown(f"**Total Costos Fijos: ₡{total_costos_fijos:,.2f}**")

    st.divider()

    # PUNTO DE EQUILIBRIO
    st.subheader("Punto de Equilibrio")

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

    if costos_df.empty:
        st.warning("Agrega costos fijos para calcular el punto de equilibrio.")
        conn.close()
        return

    total_costos_fijos = costos_df["monto"].sum()
    punto_equilibrio = total_costos_fijos / margen_promedio

    st.markdown(f"Debes vender aproximadamente **{punto_equilibrio:.2f} unidades** para cubrir los costos fijos.")

    st.divider()

    # RESUMEN FINANCIERO
    st.subheader("Resumen Financiero")

    resumen_df = pd.DataFrame({
        "Concepto": ["Total Costos Fijos", "Margen Promedio por Producto", "Unidades para Punto de Equilibrio"],
        "Valor": [f"₡{total_costos_fijos:,.2f}", f"₡{margen_promedio:,.2f}", f"{punto_equilibrio:.2f} unidades"]
    })

    st.table(resumen_df)

    conn.close()
    