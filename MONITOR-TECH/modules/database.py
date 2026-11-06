import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "system_pulse.db")

def get_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados e cria a tabela de histórico de desempenho."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_hardware (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_uso REAL,
                ram_uso REAL,
                disco_uso REAL
            )
        """)
        conn.commit()

def registrar_metrica(cpu, ram, disco):
    """Insere um registro de desempenho no banco de dados local."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historico_hardware (cpu_uso, ram_uso, disco_uso)
            VALUES (?, ?, ?)
        """, (cpu, ram, disco))
        conn.commit()

def obter_historico_recente():
    """Retorna os últimos 20 registros salvos no banco."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, cpu_uso, ram_uso, disco_uso 
            FROM historico_hardware 
            ORDER BY id DESC LIMIT 20
        """)
        return [dict(row) for row in cursor.fetchall()]