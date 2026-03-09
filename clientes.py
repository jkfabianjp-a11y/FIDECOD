import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime


def gestionar_clientes():

    st.title("👥 Gestión de Clientes")

    conn = conectar()
    c = conn.cursor()


    # FORMULARIO REGISTRO

    with st.form("form_cliente"):
        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")
        email = st.text_input("Email")
        direccion = st.text_input("Dirección")

        submit = st.form_submit_button("Registrar Cliente")

        if submit:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            c.execute("""
                INSERT INTO clientes (nombre, telefono, email, direccion, fecha_registro)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, telefono, email, direccion, fecha))

            conn.commit()
            st.success("Cliente registrado correctamente.")

    st.divider()


    # MOSTRAR CLIENTES

    df = pd.read_sql("SELECT * FROM clientes", conn)

    if df.empty:
        st.info("No hay clientes registrados.")
    else:
        st.dataframe(df)

    conn.close()