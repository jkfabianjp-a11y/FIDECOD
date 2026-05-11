import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

def generar_numero_factura(conn):
    df = pd.read_sql("SELECT id FROM facturas ORDER BY id DESC LIMIT 1", conn)
    if df.empty:
        return "FAC-0001"
    ultimo_id = int(df.iloc[0]["id"]) + 1
    return f"FAC-{str(ultimo_id).zfill(4)}"

def generar_factura():

    st.title("Facturación")

    conn = conectar()
    c = conn.cursor()

    clientes = pd.read_sql("SELECT * FROM clientes", conn)
    if clientes.empty:
        st.warning("No hay clientes registrados.")
        conn.close()
        return

    cliente_nombre = st.selectbox("Seleccionar Cliente", clientes["nombre"])
    cliente = clientes[clientes["nombre"] == cliente_nombre].iloc[0]
    cliente_id = int(cliente["id"])

    st.divider()

    subtotal = st.number_input("Subtotal", min_value=0.0, step=0.01)
    iva = subtotal * 0.13
    total = subtotal + iva

    st.write(f"IVA (13%): ₡{iva:.2f}")
    st.write(f"Total Final: ₡{total:.2f}")

    metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta", "Transferencia"])
    estado = st.selectbox("Estado", ["Pagada", "Pendiente"])

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
            st.subheader("Historial de Facturas")
            st.dataframe(historial)

            factura_select = st.selectbox(
                "Seleccionar factura para descargar",
                historial["numero_factura"]
            )

            if st.button("Descargar Factura en PDF"):
                factura = historial[historial["numero_factura"] == factura_select].iloc[0]

                file_name = f"{factura_select}.pdf"
                doc = SimpleDocTemplate(
                    file_name,
                    pagesize=A4,
                    rightMargin=30, leftMargin=30,
                    topMargin=30, bottomMargin=30
                )

                elements = []
                styles = getSampleStyleSheet()
                styles.add(ParagraphStyle(name="CenterTitle", alignment=1, fontSize=20, spaceAfter=10, leading=22))
                styles.add(ParagraphStyle(name="NormalBold", fontSize=12, spaceAfter=6, leading=14, fontName="Helvetica-Bold"))

                # ------------------------
                # LOGO AJUSTADO
                # ------------------------
                logo_path = "assets/logo.png"
                if os.path.exists(logo_path):
                    from reportlab.lib.utils import ImageReader
                    img = ImageReader(logo_path)
                    iw, ih = img.getSize()
                    aspect = ih / iw
                    width = 250
                    height = width * aspect
                    elements.append(Image(logo_path, width=width, height=height, hAlign='CENTER'))
                    elements.append(Spacer(1, 10))

                elements.append(Paragraph("FIDECOD.", styles["CenterTitle"]))
                elements.append(Paragraph("Factura Oficial", styles["CenterTitle"]))
                elements.append(Paragraph("Dirección: Calle Siles 203, San José Province, San Pedro, Santa Marta, 11501, Costa Rica", styles["Normal"]))
                elements.append(Paragraph("Tel: +506 859-275 | Email: info@fidecod.com", styles["Normal"]))
                elements.append(Spacer(1, 15))


                # DATOS DE CLIENTE Y FACTURA
                cliente_data = [
                    ["Número de Factura:", factura['numero_factura']],
                    ["Fecha:", factura['fecha']],
                    ["Cliente:", factura['cliente']],
                    ["Método de Pago:", factura['metodo_pago']],
                    ["Estado:", factura['estado']],
                    ["Teléfono:", cliente.get("telefono", "")],
                    ["Email:", cliente.get("email", "")],
                    ["Dirección:", cliente.get("direccion", "")]
                ]
                cliente_table = Table(cliente_data, colWidths=[150, 300])
                cliente_table.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f2f2f2")),
                    ("GRID", (0,0), (-1,-1), 1, colors.black),
                    ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
                    ("ALIGN", (0,0), (-1,-1), "LEFT"),
                    ("VALIGN", (0,0), (-1,-1), "MIDDLE")
                ]))
                elements.append(cliente_table)
                elements.append(Spacer(1, 20))


                # DETALLE DE FACTURA
                detalle_data = [
                    ["Concepto", "Monto (Colones)"],
                    ["Subtotal", f"{factura['subtotal']:.2f}"],
                    ["IVA (13%)", f"{factura['iva']:.2f}"],
                    ["Total", f"{factura['total']:.2f}"]
                ]
                detalle_table = Table(detalle_data, colWidths=[350, 100])
                detalle_table.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9edf7")),
                    ("TEXTCOLOR", (0,0), (-1,0), colors.black),
                    ("ALIGN", (0,0), (-1,-1), "CENTER"),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("GRID", (0,0), (-1,-1), 1, colors.black),
                    ("BOTTOMPADDING", (0,0), (-1,0), 12)
                ]))
                elements.append(detalle_table)
                elements.append(Spacer(1, 20))

                # NOTAS / OBSERVACIONES
                elements.append(Paragraph("Notas / Observaciones:", styles["NormalBold"]))
                elements.append(Paragraph("_____________________________________________________________", styles["Normal"]))
                elements.append(Spacer(1, 10))

                # FOOTER MEJORADO
                elements.append(Spacer(1, 15))
                elements.append(Paragraph("Gracias por su preferencia.", styles["NormalBold"]))
                elements.append(Paragraph("Visítanos: www.fidecod.com | Redes Sociales: Facebook / Instagram / Twitter", styles["Normal"]))
                elements.append(Paragraph("Contacto: info@fidecod.com | Tel: +506 8598-7275", styles["Normal"]))
                elements.append(Paragraph("Este documento es válido como comprobante de compra.", styles["Normal"]))

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