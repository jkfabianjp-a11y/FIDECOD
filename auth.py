import streamlit as st
import sqlite3
import hashlib
from database import conectar


#ADMIN INICIAL
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
        password = "admin1234"
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()
        c.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES (?, ?, ?)
        """, ("admin", hashed_pass, "admin"))
        conn.commit()
    conn.close()


# REGISTRO NUEVO USUARIO
def registrar_usuario(username: str, password: str, rol: str):
    conn = conectar()
    c = conn.cursor()
    hashed_pass = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES (?, ?, ?)
        """, (username, hashed_pass, rol))
        conn.commit()
        st.success(f"Usuario '{username}' registrado correctamente con rol '{rol}'.")
    except sqlite3.IntegrityError:
        st.error("El nombre de usuario ya existe.")
    finally:
        conn.close()


# LOGIN
def login(cookies):
    """
    cookies: instancia de EncryptedCookieManager
    """

    if "user" in st.session_state and st.session_state.get("user"):
        return True

    if cookies.get("user") and cookies.get("rol"):
        st.session_state["user"] = cookies.get("user")
        st.session_state["rol"] = cookies.get("rol")
        return True

    st.title("Iniciar Sesión")
    username = st.text_input("Usuario", key="login_user")
    password = st.text_input("Contraseña", type="password", key="login_pass")

    if st.button("Ingresar", key="login_btn"):
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = conectar()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM usuarios
            WHERE username=? AND password=?
        """, (username, input_hash))
        user = c.fetchone()
        conn.close()

        if user:
            st.session_state["user"] = user[1]
            st.session_state["rol"] = user[3]

            # Guardar cookies
            cookies["user"] = user[1]
            cookies["rol"] = user[3]
            cookies.save()

    # Login completado si session_state tiene usuario
    return "user" in st.session_state and st.session_state["user"]


# CAMBIAR CONTRASEÑA
def cambiar_contraseña(usuario: str, nueva_password: str):
    conn = conectar()
    c = conn.cursor()
    hashed_pass = hashlib.sha256(nueva_password.encode()).hexdigest()
    c.execute("""
        UPDATE usuarios SET password=? WHERE username=?
    """, (hashed_pass, usuario))
    conn.commit()
    conn.close()
    st.success("Contraseña actualizada correctamente.")