import sqlite3

def create_users_table():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        is_pro INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def init_simulations_table():
    conn = sqlite3.connect("users.db")
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

    conn = sqlite3.connect("users.db")
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

    cursor.execute(
        "INSERT INTO simulations (email, precio, demanda, ingresos) VALUES (?, ?, ?, ?)",
        (email, precio, demanda, ingresos)
    )

    conn.commit()
    conn.close()

def create_user(email, password):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (email, password)
    )

    conn.commit()
    conn.close()

def get_user_simulations(email):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT precio, demanda, ingresos FROM simulations WHERE email=?",
        (email,)
    )

    rows = cursor.fetchall()

    conn.close()
    
    return rows

def is_user_pro(email):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_pro FROM users WHERE email = ?",
        (email,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0] == 1

    return False
