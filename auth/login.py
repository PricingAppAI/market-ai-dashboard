import sqlite3
import bcrypt


def login_user(email, password):

    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE email=?",
        (email,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:

        stored_password = result[0]

        if bcrypt.checkpw(password.encode(), stored_password):
            return True

    return False
