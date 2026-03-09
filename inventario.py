import streamlit as st
import pandas as pd
from database import conectar


def gestionar_productos():

    st.title("📦 Gestión de Inventario")

    conn = conectar()
    c = conn.cursor()


    # AGREGAR NUEVO PRODUCTO

    st.subheader("➕ Agregar Producto")

    with st.form("form_producto"):
        nombre = st.text_input("Nombre del producto")
        precio = st.number_input("Precio de venta", min_value=0.0, step=0.01)
        costo = st.number_input("Costo del producto", min_value=0.0, step=0.01)
        stock = st.number_input("Cantidad inicial", min_value=0, step=1)

        submit = st.form_submit_button("Agregar Producto")

        if submit:
            if nombre.strip() == "":
                st.error("El nombre no puede estar vacío.")
            else:
                c.execute("""
                    INSERT INTO productos (nombre, precio, costo, stock)
                    VALUES (?, ?, ?, ?)
                """, (nombre, precio, costo, stock))
                conn.commit()
                st.success("Producto agregado correctamente.")
                st.rerun()

    st.divider()


    # MOSTRAR INVENTARIO

    df = pd.read_sql("SELECT * FROM productos", conn)

    if df.empty:
        st.info("No hay productos registrados.")
        conn.close()
        return

    st.subheader("📋 Inventario Actual")
    st.dataframe(df)

    st.divider()


    # GESTIONAR PRODUCTO EXISTENTE

    st.subheader("⚙ Gestionar Producto")

    producto_seleccionado = st.selectbox(
        "Seleccionar producto",
        df["nombre"]
    )

    producto = df[df["nombre"] == producto_seleccionado].iloc[0]
    producto_id = int(producto["id"])

    col1, col2 = st.columns(2)


    # AUMENTAR STOCK

    with col1:
        st.markdown("### 📈 Aumentar Stock")
        cantidad_sumar = st.number_input("Cantidad a agregar", min_value=0, step=1)

        if st.button("Agregar Stock"):
            if cantidad_sumar > 0:
                nuevo_stock = producto["stock"] + cantidad_sumar
                c.execute("UPDATE productos SET stock=? WHERE id=?",
                        (nuevo_stock, producto_id))
                conn.commit()
                st.success("Stock actualizado.")
                st.rerun()

    # ===============================
    # REDUCIR STOCK
    # ===============================
    with col2:
        st.markdown("### 📉 Reducir Stock")
        cantidad_restar = st.number_input("Cantidad a quitar", min_value=0, step=1)

        if st.button("Quitar Stock"):
            if cantidad_restar > 0:
                if cantidad_restar > producto["stock"]:
                    st.error("No puedes quitar más de lo que hay en stock.")
                else:
                    nuevo_stock = producto["stock"] - cantidad_restar
                    c.execute("UPDATE productos SET stock=? WHERE id=?",
                            (nuevo_stock, producto_id))
                    conn.commit()
                    st.success("Stock reducido.")
                    st.rerun()

    st.divider()


    # EDITAR PRECIO Y COSTO

    st.subheader("✏ Editar Precio / Costo")

    nuevo_precio = st.number_input(
        "Nuevo precio",
        value=float(producto["precio"]),
        min_value=0.0,
        step=0.01
    )

    nuevo_costo = st.number_input(
        "Nuevo costo",
        value=float(producto["costo"]),
        min_value=0.0,
        step=0.01
    )

    if st.button("Actualizar Precio y Costo"):
        c.execute("""
            UPDATE productos
            SET precio=?, costo=?
            WHERE id=?
        """, (nuevo_precio, nuevo_costo, producto_id))
        conn.commit()
        st.success("Producto actualizado.")
        st.rerun()

    st.divider()


    # ELIMINAR PRODUCTO

    st.subheader("🗑 Eliminar Producto")

    if st.button("Eliminar Producto"):
        c.execute("DELETE FROM productos WHERE id=?", (producto_id,))
        conn.commit()
        st.success("Producto eliminado.")
        st.rerun()

    conn.close()