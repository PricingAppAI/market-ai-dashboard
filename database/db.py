import sqlite3

def create_users_table():

    conn = sqlite3.connect("database/database.db")
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

    conn.commit()
    conn.close()

def init_simulations_table():

    import sqlite3

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

def get_user_simulations(email):

    import sqlite3

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT precio, demanda, ingresos FROM simulations WHERE email=?",
        (email,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows
