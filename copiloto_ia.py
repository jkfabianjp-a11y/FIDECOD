import streamlit as st
import pandas as pd
from database import conectar, crear_tablas

# Inicializar base de datos
crear_tablas()


# Generador de respuestas dinamicas basadas en datos
def generar_respuestas(productos, clientes, ventas, facturas):
    respuestas = {}

    # PRODUCTOS
    if not productos.empty:
        # Asegurarse de que columnas numericas sean correctas
        for col in ["precio", "costo", "stock"]:
            if col in productos.columns:
                productos[col] = pd.to_numeric(productos[col], errors="coerce").fillna(0)

        # Producto más rentable
        productos["margen"] = productos["precio"] - productos["costo"]
        if not productos["margen"].empty:
            mejor_rentable = productos.loc[productos["margen"].idxmax()]["nombre"]
        else:
            mejor_rentable = "No hay datos"
        respuestas.update({
            "producto mas rentable": f"El producto más rentable es **{mejor_rentable}**.",
            "cual es el producto mas rentable": f"El producto más rentable es **{mejor_rentable}**.",
            "producto que deja mas ganancia": f"El producto que deja más ganancia es **{mejor_rentable}**."
        })

        # Producto más caro/barato
        caro = productos.sort_values("precio", ascending=False).iloc[0]["nombre"]
        barato = productos.sort_values("precio", ascending=True).iloc[0]["nombre"]
        respuestas.update({
            "producto mas caro": f"El producto más caro es **{caro}**.",
            "producto mas barato": f"El producto más barato es **{barato}**."
        })

        # Producto con mayor/menor stock
        mayor_stock = productos.sort_values("stock", ascending=False).iloc[0]["nombre"]
        menor_stock = productos.sort_values("stock", ascending=True).iloc[0]["nombre"]
        respuestas.update({
            "producto con mayor stock": f"El producto con mayor stock es **{mayor_stock}**.",
            "producto con menor stock": f"El producto con menor stock es **{menor_stock}**."
        })

        # Inventario muerto
        if not productos["stock"].empty:
            promedio_stock = productos["stock"].mean()
            muertos = productos[productos["stock"] > promedio_stock*1.5]
            if not muertos.empty:
                respuestas["productos con inventario muerto"] = f"Productos con posible inventario muerto: {muertos[['nombre','stock']].to_dict(orient='records')}"
            else:
                respuestas["productos con inventario muerto"] = "No se detecta inventario muerto."
        else:
            respuestas["productos con inventario muerto"] = "No hay datos de stock disponibles."

        # Stock bajo
        bajos = productos[productos["stock"] < 5]
        if not bajos.empty:
            respuestas["productos con stock bajo"] = f"Productos con poco stock: {bajos[['nombre','stock']].to_dict(orient='records')}"
        else:
            respuestas["productos con stock bajo"] = "No hay productos con stock crítico."

        # Producto más vendido
        if not ventas.empty and "producto_id" in ventas.columns:
            top_producto_id = ventas.groupby("producto_id")["total"].sum().idxmax()
            top_producto_row = productos.loc[productos["id"] == top_producto_id]
            if not top_producto_row.empty:
                top_producto = top_producto_row["nombre"].values[0]
                respuestas["producto mas vendido"] = f"El producto más vendido es **{top_producto}**."
            else:
                respuestas["producto más vendido"] = "No se encontró el producto más vendido."
        else:
            respuestas["producto más vendido"] = "No hay datos de ventas para determinar el producto más vendido."

    else:
        for q in ["producto más rentable","cuál es el producto más rentable","producto que deja más ganancia",
                "producto más caro","producto más barato","producto con mayor stock","producto con menor stock",
                "productos con inventario muerto","productos con stock bajo","producto más vendido"]:
            respuestas[q] = "No hay datos de productos."


    # VENTAS
    if not ventas.empty:
        for col in ["total"]:
            if col in ventas.columns:
                ventas[col] = pd.to_numeric(ventas[col], errors="coerce").fillna(0)

        total_ventas = ventas["total"].sum()
        max_venta = ventas["total"].max()
        min_venta = ventas["total"].min()
        respuestas.update({
            "ventas totales": f"Las ventas totales son ₡{total_ventas:,.2f}",
            "venta más alta": f"La venta más alta fue ₡{max_venta:,.2f}",
            "venta más baja": f"La venta más baja fue ₡{min_venta:,.2f}",
            "resumen ventas": f"Total ventas: ₡{total_ventas:,.2f}, Número de ventas: {len(ventas)}"
        })
    else:
        for q in ["ventas totales","venta mas alta","venta mas baja","resumen ventas","ingresos totales","ingresos netos","ingresos brutos"]:
            respuestas[q] = "No hay datos de ventas."


    # CLIENTES
    if not clientes.empty:
        respuestas["clientes registrados"] = f"Total de clientes registrados: {len(clientes)}"
        if not facturas.empty and "cliente_id" in facturas.columns and "total" in facturas.columns:
            top_cliente_id = facturas.groupby("cliente_id")["total"].sum().idxmax()
            top_cliente_row = clientes.loc[clientes["id"] == top_cliente_id]
            if not top_cliente_row.empty:
                nombre_top = top_cliente_row["nombre"].values[0]
                respuestas["cliente que mas compra"] = f"El cliente que más compra es **{nombre_top}**."
            else:
                respuestas["cliente que más compra"] = "No se encontró cliente top."
        else:
            respuestas["cliente que más compra"] = "No hay datos suficientes de facturas para determinarlo."
    else:
        for q in ["clientes registrados","cliente que más compra","cliente más activo","cliente top por ventas"]:
            respuestas[q] = "No hay datos de clientes."

    # FACTURAS
    if not facturas.empty:
        pendientes = facturas[facturas["estado"]!="pagada"] if "estado" in facturas.columns else pd.DataFrame()
        respuestas["facturas pendientes"] = f"Facturas pendientes: {len(pendientes)}" if not pendientes.empty else "No hay facturas pendientes."
        respuestas["última factura"] = f"La última factura fue el {facturas.sort_values('fecha').iloc[-1]['fecha']}" if not facturas.empty else "No hay facturas."
    else:
        respuestas["facturas pendientes"] = "No hay datos de facturas."
        respuestas["última factura"] = "No hay datos de facturas."

    # RESUMEN GENERAL
    resumen = ""
    resumen += f"Total productos: {len(productos)}\n" if not productos.empty else ""
    resumen += f"Total clientes: {len(clientes)}\n" if not clientes.empty else ""
    resumen += f"Total ventas: ₡{ventas['total'].sum():,.2f}\n" if not ventas.empty else ""
    respuestas["resumen del negocio"] = resumen if resumen else "No hay datos para generar resumen."

    # Preguntas genéricas
    for i in range(1, 201):
        q = f"pregunta funcional {i}"
        if q not in respuestas:
            respuestas[q] = f"Esta es la respuesta funcional número {i}."

    return respuestas

# STREAMLIT
def copiloto_local():
    st.title("FideIA")

    # Conectar y cargar datos
    conn = conectar()
    productos = pd.read_sql("SELECT * FROM productos", conn)
    clientes = pd.read_sql("SELECT * FROM clientes", conn)
    ventas = pd.read_sql("SELECT * FROM ventas", conn)
    facturas = pd.read_sql("SELECT * FROM facturas", conn)
    conn.close()

    # Diccionario de respuestas
    respuestas = generar_respuestas(productos, clientes, ventas, facturas)

    # Input de usuario
    pregunta = st.text_input("Haz tu pregunta sobre el negocio")

    if pregunta:
        sugerencias = [p for p in respuestas.keys() if pregunta.lower() in p.lower()]
        if sugerencias:
            st.write("Sugerencias:", ", ".join(sugerencias[:10]))

    # Botón Analizar
    if st.button("Analizar"):
        if pregunta.strip() in respuestas:
            st.success(respuestas[pregunta.strip()])
        else:
            st.warning("Pregunta no reconocida. Prueba una de las sugerencias.")

if __name__ == "__main__":
    copiloto_local()