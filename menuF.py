import streamlit as st
from PIL import Image
import os

from database import crear_tablas
from auth import login, crear_admin_inicial, registrar_usuario
from dashboard import mostrar_dashboard
from inventario import gestionar_productos
from clientes import gestionar_clientes
from ventas import registrar_venta
from facturas import generar_factura
from finanzas import herramientas_financieras
from admin import mostrar_administracion
from seguridad import registrar_log
from reportes2 import exportar_reporte_excel
from ia_predictiva import prediccion_ventas
from copiloto_ia import copiloto_local
from streamlit_cookies_manager import EncryptedCookieManager

# Inicializar cookies
cookies = EncryptedCookieManager(
    prefix="fidecod",
    password="clave_secreta_fidecod"
)
if not cookies.ready():
    st.stop()

# Configuración de página
st.set_page_config(
    page_title="FIDECOD",
    page_icon="assets/logo.png",
    layout="wide"
)

# Crear tablas y admin
crear_tablas()
crear_admin_inicial()

# Mostrar logo
def mostrar_logo_derecha(ruta_logo="assets/logo.png", ancho_px=180, proporciones=(3,2,1)):
    if os.path.exists(ruta_logo):
        logo = Image.open(ruta_logo)
        col_izq, col_logo, col_der = st.columns(proporciones)
        with col_logo:
            st.image(logo, width=ancho_px)
    else:
        st.warning("Logo no se pudo cargar.")

def cerrar_sesion():
    cookies["user"] = ""
    cookies["rol"] = ""
    cookies.save()
    st.session_state.clear()
    st.stop()

# Login
if not login(cookies):
    st.stop()  

# Sistema principal
st.markdown("<br>", unsafe_allow_html=True)
mostrar_logo_derecha(ancho_px=240, proporciones=(2,2,1))
st.title("ʙɪᴇɴᴠᴇɴɪᴅᴏꜱ ᴀ ꜰɪᴅᴇᴄᴏᴅ")

try:
    logo_sidebar_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_sidebar_path):
        logo_sidebar = Image.open(logo_sidebar_path)
        st.sidebar.image(logo_sidebar, width=210)
except:
    st.sidebar.warning("Logo sidebar no se pudo cargar.")

# Info usuario y botón cerrar sesión
st.sidebar.success(f"Usuario: {st.session_state.get('user', '')}")
st.sidebar.info(f"Rol: {st.session_state.get('rol', '')}")

if st.sidebar.button(" Cerrar Sesión"):
    cerrar_sesion()

# Menú principal
menu = st.sidebar.selectbox("Menú Principal", [
    "Dashboard",
    "Inventario",
    "Clientes",
    "Ventas",
    "Facturación",
    "Finanzas",
    "Reportes",
    "FideIA",
    "IA Predictiva",
    "Administración"
])

st.divider()


# Control de secciones
if menu == "Dashboard":
    mostrar_dashboard()
    registrar_log(st.session_state.get("user", ""), "Accedió al Dashboard")

elif menu == "Inventario":
    if st.session_state.get("rol", "") == "admin":
        gestionar_productos()
        registrar_log(st.session_state.get("user", ""), "Gestionó Inventario")
    else:
        st.error("No tienes permisos para acceder al Inventario.")

elif menu == "Clientes":
    gestionar_clientes()
    registrar_log(st.session_state.get("user", ""), "Gestionó Clientes")

elif menu == "Ventas":
    registrar_venta()
    registrar_log(st.session_state.get("user", ""), "Registró una Venta")

elif menu == "Facturación":
    generar_factura()
    registrar_log(st.session_state.get("user", ""), "Generó una Factura")

elif menu == "Finanzas":
    if st.session_state.get("rol", "") == "admin":
        herramientas_financieras()
        registrar_log(st.session_state.get("user", ""), "Accedió a Finanzas")
    else:
        st.error("Solo el administrador puede acceder a Finanzas.")

elif menu == "Administración":
    if st.session_state.get("rol", "") == "admin":
        mostrar_administracion()
        registrar_log(st.session_state.get("user", ""), "Accedió al Panel Admin")

        st.divider()
        st.subheader("Registrar nuevo usuario")

        nuevo_usuario = st.text_input("Nombre de usuario", key="nuevo_usuario")
        nueva_clave = st.text_input("Contraseña", type="password", key="nueva_clave")
        rol_usuario = st.selectbox("Rol del usuario", ["admin", "vendedor", "cajero"], key="rol_usuario")

        if st.button("Registrar Usuario", key="registrar_usuario"):
            if nuevo_usuario and nueva_clave:
                registrar_usuario(nuevo_usuario, nueva_clave, rol_usuario)
            else:
                st.warning("Debe llenar todos los campos.")
    else:
        st.error("Acceso restringido.")

elif menu == "Reportes":
    if st.session_state.get("rol", "") == "admin":
        exportar_reporte_excel()
    else:
        st.error("Solo el administrador puede exportar reportes.")

elif menu == "IA Predictiva":
    registrar_log(st.session_state.get("user", ""), "Usó IA Predictiva")
    prediccion_ventas()

elif menu == "FideIA":
    registrar_log(st.session_state.get("user", ""), "Usó FideIA")
    copiloto_local()
