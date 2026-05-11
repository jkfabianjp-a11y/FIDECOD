import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime
def registrar_venta(usuario=None):

    st.title("🛒 Registrar Venta")


    # Conexión a la base de datos
    conn = conectar()
    c = conn.cursor()

    # Cargar productos
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

    # Filtrar productos con stock
    productos_disponibles = productos[productos["stock"] > 0]
    if productos_disponibles.empty:
        st.info("Todos los productos están agotados.")
        conn.close()
        return

    producto_nombre = st.selectbox(
        "Selecciona un producto",
        productos_disponibles["nombre"]
    )

    producto = productos_disponibles[productos_disponibles["nombre"] == producto_nombre].iloc[0]

    producto_id = int(producto["id"])
    precio_unitario = float(producto["precio"])
    stock_actual = int(producto["stock"])

    st.info(f"Stock disponible: {stock_actual} unidades")
    st.info(f"Precio unitario: ₡{precio_unitario:,.2f}")


    # Selección de cantidad
    cantidad = st.number_input(
        "Cantidad a vender",
        min_value=1,
        max_value=stock_actual,
        step=1
    )

    total = cantidad * precio_unitario
    st.success(f"Total de la venta: ₡{total:,.2f}")

    # Botón de registrar venta
    if st.button("Registrar Venta"):

        if cantidad > stock_actual:
            st.error("No hay suficiente stock disponible.")
        else:

            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                # Registrar venta
                c.execute("""
                    INSERT INTO ventas (producto_id, cantidad, total, fecha)
                    VALUES (?, ?, ?, ?)
                """, (producto_id, cantidad, total, fecha))

                # Actualizar stock
                nuevo_stock = stock_actual - cantidad
                c.execute("""
                    UPDATE productos
                    SET stock = ?
                    WHERE id = ?
                """, (nuevo_stock, producto_id))

                # Registrar en logs si se pasa usuario
                if usuario:
                    c.execute("""
                        INSERT INTO logs (usuario, accion, fecha)
                        VALUES (?, ?, ?)
                    """, (usuario, f"Registró venta de {cantidad} '{producto_nombre}' por ₡{total:,.2f}", fecha))

                conn.commit()

                st.success(f"✅ Venta registrada correctamente")
                st.info(f"Producto: {producto_nombre} | Cantidad: {cantidad} | Total: ₡{total:,.2f}")
                st.info(f"Stock actualizado: {nuevo_stock} unidades")

                # Mostrar tabla de ventas
                ventas_df = pd.read_sql("""
                    SELECT v.id, p.nombre AS producto, v.cantidad, v.total, v.fecha
                    FROM ventas v
                    JOIN productos p ON v.producto_id = p.id
                    ORDER BY v.fecha DESC
                """, conn)

                if not ventas_df.empty:
                    st.subheader("Historial de Ventas")
                    st.dataframe(ventas_df)

            except Exception as e:
                conn.rollback()
                st.error(f"Ocurrió un error al registrar la venta: {e}")

    else:
        ventas_df = pd.read_sql("""
            SELECT v.id, p.nombre AS producto, v.cantidad, v.total, v.fecha
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            ORDER BY v.fecha DESC
        """, conn)

        if not ventas_df.empty:
            st.subheader("Historial de Ventas")
            st.dataframe(ventas_df)

    conn.close()