import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
import os


# ==========================================
# GENERAR NÚMERO AUTOMÁTICO
# ==========================================
def generar_numero_factura(conn):
    df = pd.read_sql("SELECT id FROM facturas ORDER BY id DESC LIMIT 1", conn)

    if df.empty:
        return "FAC-0001"

    ultimo_id = int(df.iloc[0]["id"]) + 1
    return f"FAC-{str(ultimo_id).zfill(4)}"


# ==========================================
# MÓDULO PRINCIPAL
# ==========================================
def generar_factura():

    st.title("🧾 Facturación Profesional")

    conn = conectar()
    c = conn.cursor()

    # ===============================
    # CARGAR CLIENTES
    # ===============================
    clientes = pd.read_sql("SELECT * FROM clientes", conn)

    if clientes.empty:
        st.warning("No hay clientes registrados.")
        conn.close()
        return

    cliente_nombre = st.selectbox("Seleccionar Cliente", clientes["nombre"])
    cliente = clientes[clientes["nombre"] == cliente_nombre].iloc[0]
    cliente_id = int(cliente["id"])

    st.divider()

    # ===============================
    # DATOS FINANCIEROS
    # ===============================
    subtotal = st.number_input("Subtotal", min_value=0.0, step=0.01)
    iva = subtotal * 0.13
    total = subtotal + iva

    st.write(f"IVA (13%): ₡{iva:.2f}")
    st.write(f"Total Final: ₡{total:.2f}")

    metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta", "Transferencia"])
    estado = st.selectbox("Estado", ["Pagada", "Pendiente"])

    # ===============================
    # GENERAR FACTURA
    # ===============================
    if st.button("Generar Factura"):

        numero_factura = generar_numero_factura(conn)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            INSERT INTO facturas
            (numero_factura, cliente_id, fecha, subtotal, iva, total, metodo_pago, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            numero_factura,
            cliente_id,
            fecha,
            subtotal,
            iva,
            total,
            metodo_pago,
            estado
        ))

        conn.commit()
        st.success(f"Factura {numero_factura} generada correctamente.")
        st.rerun()

    st.divider()

    # ===============================
    # HISTORIAL DE FACTURAS
    # ===============================
    try:
        historial = pd.read_sql("""
            SELECT 
                f.numero_factura,
                c.nombre AS cliente,
                f.fecha,
                f.subtotal,
                f.iva,
                f.total,
                f.metodo_pago,
                f.estado
            FROM facturas f
            LEFT JOIN clientes c ON f.cliente_id = c.id
            ORDER BY f.fecha DESC
        """, conn)

        if historial.empty:
            st.info("No hay facturas registradas.")
        else:
            st.subheader("📄 Historial de Facturas")
            st.dataframe(historial)

            factura_select = st.selectbox(
                "Seleccionar factura para descargar",
                historial["numero_factura"]
            )

            if st.button("Descargar Factura en PDF"):

                factura = historial[historial["numero_factura"] == factura_select].iloc[0]

                file_name = f"{factura_select}.pdf"
                doc = SimpleDocTemplate(file_name, pagesize=pagesizes.A4)
                elements = []
                styles = getSampleStyleSheet()

                elements.append(Paragraph(f"Factura: {factura_select}", styles["Title"]))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Cliente: {factura['cliente']}", styles["Normal"]))
                elements.append(Paragraph(f"Fecha: {factura['fecha']}", styles["Normal"]))
                elements.append(Paragraph(f"Subtotal: ₡{factura['subtotal']}", styles["Normal"]))
                elements.append(Paragraph(f"IVA: ₡{factura['iva']}", styles["Normal"]))
                elements.append(Paragraph(f"Total: ₡{factura['total']}", styles["Normal"]))
                elements.append(Paragraph(f"Método de Pago: {factura['metodo_pago']}", styles["Normal"]))
                elements.append(Paragraph(f"Estado: {factura['estado']}", styles["Normal"]))

                doc.build(elements)

                with open(file_name, "rb") as f:
                    st.download_button(
                        label="Descargar PDF",
                        data=f,
                        file_name=file_name,
                        mime="application/pdf"
                    )

                os.remove(file_name)

    except Exception as e:
        st.error("Error al cargar historial de facturas.")
        st.code(str(e))

    conn.close()