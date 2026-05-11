import streamlit as st
import pandas as pd
from database import conectar
import hashlib
from seguridad import registrar_log  


# FUNCIONES AUXILIARES
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def mostrar_logs():
    st.subheader("Registro de Actividad")
    conn = conectar()
    try:
        logs = pd.read_sql("SELECT * FROM logs ORDER BY fecha DESC", conn)
        if logs.empty:
            st.info("No hay actividad registrada")
        else:
            st.dataframe(logs)
    except Exception as e:
        st.error("Error al cargar los logs")
        st.code(str(e))
    finally:
        conn.close()


def cambiar_contraseña():
    st.subheader("Cambiar Contraseña")

    contraseña_actual = st.text_input("Contraseña Actual", type="password")
    nueva_contraseña = st.text_input("Nueva Contraseña", type="password")
    confirmar_contraseña = st.text_input("Confirmar Nueva Contraseña", type="password")

    if st.button("Actualizar Contraseña"):
        if not all([contraseña_actual, nueva_contraseña, confirmar_contraseña]):
            st.warning("Por favor, completa todos los campos")
            return

        if nueva_contraseña != confirmar_contraseña:
            st.error("La nueva contraseña y la confirmación no coinciden.")
            return

        conn = conectar()
        c = conn.cursor()
        try:
            c.execute("SELECT password FROM usuarios WHERE username=?", (st.session_state["user"],))
            resultado = c.fetchone()
            if not resultado:
                st.error("Usuario no encontrado.")
                return

            password_hash = resultado[0]

            if hash_password(contraseña_actual) != password_hash:
                st.error("Contraseña actual incorrecta.")
                return

            nueva_hash = hash_password(nueva_contraseña)
            c.execute("UPDATE usuarios SET password=? WHERE username=?", (nueva_hash, st.session_state["user"]))
            conn.commit()
            st.success("Contraseña actualizada correctamente.")

            registrar_log(st.session_state["user"], "Cambio de contraseña")

        except Exception as e:
            st.error("Ocurrió un error al actualizar la contraseña.")
            st.code(str(e))
        finally:
            conn.close()


# MÓDULO PRINCIPAL

def mostrar_administracion():
    st.title("Panel de Administración")

    # Mostrar logs en un expander
    with st.expander("Ver Historial de Actividad"):
        mostrar_logs()

    st.divider()

    # Cambiar contraseña en otro expander
    with st.expander("Cambiar Contraseña Admin"):
        cambiar_contraseña()