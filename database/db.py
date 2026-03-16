import sqlite3


def create_users_table():

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        plan TEXT DEFAULT 'free'
    )
    """)

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN verification_code TEXT")
    except:
        pass

    conn.commit()
    conn.close()

def init_simulations_table():

    conn = sqlite3.connect("database/database.db")
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

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO simulations (email, precio, demanda, ingresos) VALUES (?, ?, ?, ?)",
        (email, precio, demanda, ingresos)
    )

    conn.commit()
    conn.close()

def create_user(email, password):

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (email, password)
    )

    conn.commit()
    conn.close()

def get_user_simulations(email):

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT precio, demanda, ingresos FROM simulations WHERE email=?",
        (email,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows

def activar_pro(user_email):

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET plan='pro' WHERE email=?",
        (user_email,)
    )

    conn.commit()
    conn.close()

def es_pro(user_email):

    conn = sqlite3.connect("database/database.db")
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
