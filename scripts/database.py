import sqlite3
from typing import List, Tuple, Any, Optional

DB_PATH = 'jarvis_data.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    """Crea las tablas principales para la app Jarvis."""
    with get_connection() as conn:
        c = conn.cursor()
        # Ejemplo: tabla de comandos ejecutados
        c.execute('''
            CREATE TABLE IF NOT EXISTS comandos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                usuario TEXT NOT NULL,
                comando TEXT NOT NULL,
                resultado TEXT
            )
        ''')
        # Puedes agregar más tablas aquí
        conn.commit()

def insertar_comando(fecha: str, usuario: str, comando: str, resultado: Optional[str] = None):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO comandos (fecha, usuario, comando, resultado)
            VALUES (?, ?, ?, ?)
        ''', (fecha, usuario, comando, resultado))
        conn.commit()

def obtener_comandos(limit: int = 20) -> List[Tuple[Any, ...]]:
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT id, fecha, usuario, comando, resultado
            FROM comandos
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        return c.fetchall()

def actualizar_resultado_comando(comando_id: int, resultado: str):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE comandos SET resultado = ? WHERE id = ?
        ''', (resultado, comando_id))
        conn.commit()

def eliminar_comando(comando_id: int):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            DELETE FROM comandos WHERE id = ?
        ''', (comando_id,))
        conn.commit()

if __name__ == "__main__":
    create_tables()
    print("Tablas creadas y base de datos lista.")
