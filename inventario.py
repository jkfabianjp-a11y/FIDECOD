import streamlit as st
import pandas as pd
from database import conectar


def gestionar_productos():

    st.title("Gestión de Inventario")

    conn = conectar()
    c = conn.cursor()


    # AGREGAR NUEVO PRODUCTO
    st.subheader("Agregar Producto")

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
                """, (nombre, precio, costo, int(stock)))

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

    st.subheader("Inventario Actual")
    st.dataframe(df)

    st.divider()

    # SELECCIONAR PRODUCTO
    st.subheader("Gestionar Producto")

    producto_seleccionado = st.selectbox(
        "Seleccionar producto",
        df["nombre"],
        key="producto_selector"
    )

    producto = df[df["nombre"] == producto_seleccionado].iloc[0]
    producto_id = int(producto["id"])

    # OBTENER STOCK ACTUAL (ARREGLADO)
    c.execute("SELECT stock FROM productos WHERE id=?", (producto_id,))
    resultado = c.fetchone()

    try:
        stock_actual = int(resultado[0]) if resultado and resultado[0] is not None else 0
    except:
        stock_actual = 0

    col1, col2 = st.columns(2)

    # AUMENTAR STOCK
    with col1:

        st.markdown("Aumentar Stock")

        cantidad_sumar = st.number_input(
            "Cantidad a agregar",
            min_value=0,
            step=1,
            key="sumar_stock"
        )

        if st.button("Agregar Stock", key="btn_sumar"):

            if cantidad_sumar <= 0:
                st.warning("Debes ingresar una cantidad mayor a 0.")

            else:

                c.execute(
                    "UPDATE productos SET stock = stock + ? WHERE id=?",
                    (int(cantidad_sumar), producto_id)
                )

                conn.commit()

                st.success("Stock actualizado correctamente.")
                st.rerun()

    # REDUCIR STOCK
    with col2:

        st.markdown("Reducir Stock")

        cantidad_restar = st.number_input(
            "Cantidad a quitar",
            min_value=0,
            step=1,
            key="restar_stock"
        )

        if st.button("Quitar Stock", key="btn_restar"):

            if cantidad_restar <= 0:
                st.warning("Debes ingresar una cantidad mayor a 0.")

            elif cantidad_restar > stock_actual:
                st.error("No puedes quitar más de lo que hay en stock.")

            else:

                c.execute(
                    "UPDATE productos SET stock = stock - ? WHERE id=?",
                    (int(cantidad_restar), producto_id)
                )

                conn.commit()

                st.success("Stock reducido correctamente.")
                st.rerun()

    st.divider()


    # EDITAR PRECIO Y COSTO
    st.subheader("Editar Precio / Costo")

    nuevo_precio = st.number_input(
        "Nuevo precio",
        value=float(producto["precio"]),
        min_value=0.0,
        step=0.01,
        key="nuevo_precio"
    )

    nuevo_costo = st.number_input(
        "Nuevo costo",
        value=float(producto["costo"]),
        min_value=0.0,
        step=0.01,
        key="nuevo_costo"
    )

    if st.button("Actualizar Precio y Costo", key="btn_actualizar_precio"):

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

    if st.button("Eliminar Producto", key="btn_eliminar"):

        c.execute(
            "DELETE FROM productos WHERE id=?",
            (producto_id,)
        )

        conn.commit()

        st.success("Producto eliminado.")
        st.rerun()

    conn.close()