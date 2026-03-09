import streamlit as st

# =============================
# FUNCIÓN AUXILIAR
# =============================

def colones(monto):
    """Formatea números como colones costarricenses"""
    return f"₡{monto:,.0f}".replace(",", ".")

# =============================
# GESTIÓN DE PRODUCTOS
# =============================

def mostrar_productos(productos):
    st.write("### 📦 Inventario")

    # Encabezados
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown("**Producto**")
    col2.markdown("**Stock**")
    col3.markdown("**Precio venta**")
    col4.markdown("**Costo**")
    col5.markdown("**Ganancia**")

    st.divider()

    for nombre, datos in productos.items():
        ganancia_por_unidad = datos["precio"] - datos["costo"]

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.write(nombre)
        c2.write(datos["stock"])
        c3.write(colones(datos["precio"]))
        c4.write(colones(datos["costo"]))
        c5.write(colones(ganancia_por_unidad))

        if datos["stock"] <= datos["alerta"]:
            st.warning(f"⚠️ Inventario bajo: {nombre}")



def ajustar_inventario(productos):
    mostrar_productos(productos)

    with st.form("form_inventario"):
        prod = st.selectbox(
            "Producto a ajustar",
            list(productos.keys())
        )

        ajuste = st.number_input(
            "Cantidad (+ entrada / - salida)",
            step=1
        )

        submit = st.form_submit_button("Actualizar inventario")

    if submit:
        productos[prod]["stock"] += ajuste

        if productos[prod]["stock"] < 0:
            productos[prod]["stock"] = 0

        st.success("Inventario actualizado")
        st.rerun()



# =============================
# VENTAS
# =============================

def registrar_venta(ventas, productos):
    mostrar_productos(productos)

    with st.form("form_venta"):
        prod = st.selectbox(
            "Producto vendido",
            list(productos.keys())
        )

        cantidad = st.number_input(
            "Cantidad vendida",
            min_value=0,
            step=1
        )

        submit = st.form_submit_button("Registrar venta")

    if submit:
        if cantidad > productos[prod]["stock"]:
            st.error("Stock insuficiente")
            return

        total = cantidad * productos[prod]["precio"]
        costo_total = cantidad * productos[prod]["costo"]

        ventas.append({
            "producto": prod,
            "cantidad": cantidad,
            "total": total,
            "costo": costo_total
        })

        productos[prod]["stock"] -= cantidad

        st.success(f"Venta registrada. Total: ¢{total}")

        st.rerun()




def mostrar_ventas(ventas):
    st.write("### 📋 Ventas")

    if not ventas:
        st.info("No hay ventas registradas")
        return

    for v in ventas:
        st.write(
            f"{v['producto']} - {v['cantidad']} - ¢{v['total']}"
        )


# =============================
# GASTOS
# =============================

def registrar_gasto(gastos):
    concepto = st.text_input("Concepto del gasto")
    monto = st.number_input("Monto", min_value=0.0, step=100.0)
    tipo = st.selectbox("Tipo de gasto", ["Fijo", "Variable"])

    if st.button("Registrar gasto"):
        gastos.append({
            "concepto": concepto,
            "monto": monto,
            "tipo": tipo
        })

        st.success("Gasto registrado")


# =============================
# FINANZAS
# =============================

def resumen_financiero(ventas, gastos):
    dinero_entrado = sum(v["total"] for v in ventas)
    costo_de_lo_vendido = sum(v["costo"] for v in ventas)
    gastos_del_negocio = sum(g["monto"] for g in gastos)

    ganancia_final = dinero_entrado - costo_de_lo_vendido - gastos_del_negocio

    if dinero_entrado > 0:
        que_tanto_deja = (ganancia_final / dinero_entrado) * 100
    else:
        que_tanto_deja = 0

    return {
        "dinero_entrado": dinero_entrado,
        "costo_de_lo_vendido": costo_de_lo_vendido,
        "gastos_del_negocio": gastos_del_negocio,
        "ganancia_final": ganancia_final,
        "que_tanto_deja": que_tanto_deja
    }



