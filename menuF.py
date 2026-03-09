import streamlit as st


# IMPORTACIONES

from database import crear_tablas
from auth import login, crear_admin_inicial
from dashboard import mostrar_dashboard
from inventario import gestionar_productos
from clientes import gestionar_clientes
from ventas import registrar_venta
from facturas import generar_factura
from finanzas import herramientas_financieras
from admin import mostrar_administracion
from seguridad import registrar_log
from reportes2 import exportar_reporte_excel
from database import crear_tablas
from auth import crear_admin_inicial




# CONFIGURACIÓN

st.set_page_config(
    page_title="Sistema Empresarial Pro",
    page_icon="💼",
    layout="wide"
)

crear_tablas()
crear_admin_inicial()


# LOGIN

login()


# SISTEMA PRINCIPAL

if "user" in st.session_state:

    st.sidebar.success(f"👤 Usuario: {st.session_state['user']}")
    st.sidebar.info(f"🔑 Rol: {st.session_state['rol']}")

    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()


    # MENÚ (DEFINIDO ANTES DEL IF)

    menu = st.sidebar.selectbox("📌 Menú Principal", [
        "📊 Dashboard",
        "📦 Inventario",
        "👥 Clientes",
        "💰 Ventas",
        "🧾 Facturación",
        "📊 Finanzas",
        "📁 Reportes",
        "⚙ Administración"
    ])

    st.divider()


    # CONTROL DE SECCIONES


    if menu == "📊 Dashboard":
        mostrar_dashboard()
        registrar_log(st.session_state["user"], "Accedió al Dashboard")

    elif menu == "📦 Inventario":
        if st.session_state["rol"] == "admin":
            gestionar_productos()
            registrar_log(st.session_state["user"], "Gestionó Inventario")
        else:
            st.error("No tienes permisos para acceder al Inventario.")

    elif menu == "👥 Clientes":
        gestionar_clientes()
        registrar_log(st.session_state["user"], "Gestionó Clientes")

    elif menu == "💰 Ventas":
        registrar_venta()
        registrar_log(st.session_state["user"], "Registró una Venta")

    elif menu == "🧾 Facturación":
        generar_factura()
        registrar_log(st.session_state["user"], "Generó una Factura")

    elif menu == "📊 Finanzas":
        if st.session_state["rol"] == "admin":
            herramientas_financieras()
            registrar_log(st.session_state["user"], "Accedió a Finanzas")
        else:
            st.error("Solo el administrador puede acceder a Finanzas.")

    elif menu == "⚙ Administración":
        if st.session_state["rol"] == "admin":
            mostrar_administracion()
            registrar_log(st.session_state["user"], "Accedió al Panel Admin")
        else:
            st.error("Acceso restringido.")
    elif menu == "📁 Reportes":
        if st.session_state["rol"] == "admin":
            exportar_reporte_excel()
        else:
            st.error("Solo el administrador puede exportar reportes.")

else:
    st.title("🔐 Sistema Empresarial Profesional")
    st.info("Inicia sesión para continuar.")







