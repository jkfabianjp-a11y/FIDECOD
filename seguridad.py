import sqlite3
from datetime import datetime
from database import conectar


def registrar_log(usuario, accion):

    try:
        conn = conectar()
        c = conn.cursor()

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            INSERT INTO logs (usuario, accion, fecha)
            VALUES (?, ?, ?)
        """, (usuario, accion, fecha))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Error al registrar log:", e)