import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def conectar():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def crear_tablas():
    conn = conectar()
    c = conn.cursor()

    # PRODUCTOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        costo REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    """)

    # CLIENTES
    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        fecha_registro TEXT
    )
    """)

    # VENTAS
    c.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        total REAL NOT NULL,
        fecha TEXT NOT NULL
    )
    """)

    # FACTURAS
    c.execute("""
    CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_factura TEXT UNIQUE,
        cliente_id INTEGER,
        fecha TEXT NOT NULL,
        subtotal REAL NOT NULL,
        iva REAL NOT NULL,
        total REAL NOT NULL,
        metodo_pago TEXT,
        estado TEXT
    )
    """)

    # DETALLE FACTURA
    c.execute("""
    CREATE TABLE IF NOT EXISTS factura_detalle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factura_id INTEGER,
        producto TEXT,
        cantidad INTEGER,
        precio_unitario REAL,
        total_linea REAL
    )
    """)

    # USUARIOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    """)

    # LOGS
    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        accion TEXT NOT NULL,
        fecha TEXT NOT NULL
    )
    """)

    # COSTOS FIJOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS costos_fijos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT,
        monto REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()