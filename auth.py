import streamlit as st
from database import conectar



# CREAR ADMIN INICIAL

def crear_admin_inicial():

    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    c.execute("SELECT * FROM usuarios WHERE username='admin'")
    admin = c.fetchone()

    if not admin:
        c.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES ('admin', 'admin123', 'admin')
        """)
        conn.commit()

    conn.close()



# LOGIN

def login():

    if "user" not in st.session_state:

        st.title("🔐 Iniciar Sesión")

        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):

            conn = conectar()
            c = conn.cursor()

            c.execute("""
                SELECT * FROM usuarios
                WHERE username=? AND password=?
            """, (username, password))

            user = c.fetchone()
            conn.close()

            if user:
                st.session_state["user"] = user[1]
                st.session_state["rol"] = user[3]
                st.rerun()
            else:
                st.error("Credenciales incorrectas")