from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def generar_factura(cliente, total):
    doc = SimpleDocTemplate(f"factura_{cliente}.pdf")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Factura de Venta", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Cliente: {cliente}", styles["Normal"]))
    elements.append(Paragraph(f"Total: ₡{total}", styles["Normal"]))
    elements.append(Paragraph(f"Fecha: {datetime.datetime.now()}", styles["Normal"]))

    doc.build(elements)