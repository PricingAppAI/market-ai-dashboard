import sqlite3

DB_PATH = "database/database.db"

def create_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           email TEXT UNIQUE,
           password BLOB,
           plan TEXT DEFAULT 'free',
           verification_code TEXT
    )
    """)

    # Si la tabla ya existía sin verification_code, intenta agregarla
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN verification_code TEXT")
    except:
        pass

    conn.commit()
    conn.close()

def init_simulations_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        precio REAL,
        demanda REAL,
        ingresos REAL
    )
    """)

    conn.commit()
    conn.close()


def save_simulation(email, precio, demanda, ingresos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO simulations (email, precio, demanda, ingresos) VALUES (?, ?, ?, ?)",
        (email, precio, demanda, ingresos)
    )

    conn.commit()
    conn.close()

def get_user_simulations(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT precio, demanda, ingresos FROM simulations WHERE email=?",
        (email,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows

def es_pro(user_email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT plan FROM users WHERE email=?",
        (user_email,)
    )

    result = cursor.fetchone()

    conn.close()

    if result and result[0] == "pro":
        return True

    return False
