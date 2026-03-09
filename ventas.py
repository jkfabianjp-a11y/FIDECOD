import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime

def registrar_venta():

    st.title("🛒 Registrar Venta")

    conn = conectar()
    c = conn.cursor()

    productos = pd.read_sql("SELECT * FROM productos", conn)

    if productos.empty:
        st.warning("No hay productos registrados.")
        conn.close()
        return

    # Forzar tipos correctos
    productos["precio"] = pd.to_numeric(productos["precio"], errors="coerce")
    productos["costo"] = pd.to_numeric(productos["costo"], errors="coerce")
    productos["stock"] = pd.to_numeric(productos["stock"], errors="coerce")

    productos = productos.dropna()

    producto_nombre = st.selectbox(
        "Selecciona un producto",
        productos["nombre"]
    )

    producto = productos[productos["nombre"] == producto_nombre].iloc[0]

    producto_id = int(producto["id"])
    precio = float(producto["precio"])
    stock_actual = int(producto["stock"])

    st.write(f"Stock disponible: {stock_actual}")
    st.write(f"Precio unitario: ₡{precio}")

    cantidad = st.number_input(
        "Cantidad",
        min_value=1,
        max_value=stock_actual if stock_actual > 0 else 1,
        step=1
    )

    total = cantidad * precio

    st.write(f"Total: ₡{total}")

    if st.button("Registrar Venta"):

        if cantidad > stock_actual:
            st.error("No hay suficiente stock.")
        else:

            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            c.execute("""
                INSERT INTO ventas (producto_id, cantidad, total, fecha)
                VALUES (?, ?, ?, ?)
            """, (producto_id, cantidad, total, fecha))

            nuevo_stock = stock_actual - cantidad

            c.execute("""
                UPDATE productos
                SET stock = ?
                WHERE id = ?
            """, (nuevo_stock, producto_id))

            conn.commit()
            st.success("Venta registrada correctamente.")

    conn.close()