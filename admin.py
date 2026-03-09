import streamlit as st
import pandas as pd
from database import conectar

def mostrar_administracion():

    st.title("⚙ Panel de Administración")

    conn = conectar()

    st.subheader("📜 Registro de Actividad")

    logs = pd.read_sql("SELECT * FROM logs ORDER BY fecha DESC", conn)

    if not logs.empty:
        st.dataframe(logs)
    else:
        st.info("No hay actividad registrada.")

    st.divider()

    st.subheader("🔐 Cambiar Contraseña")

    nueva_pass = st.text_input("Nueva contraseña", type="password")

    if st.button("Actualizar Contraseña"):
        c = conn.cursor()
        c.execute(
            "UPDATE usuarios SET password=? WHERE username=?",
            (nueva_pass, st.session_state["user"])
        )
        conn.commit()
        st.success("Contraseña actualizada correctamente.")

    conn.close()