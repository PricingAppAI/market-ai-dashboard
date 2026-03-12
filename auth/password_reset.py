import sqlite3
import bcrypt


def update_password(email, new_password):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

    cursor.execute(
        "UPDATE users SET password=? WHERE email=?",
        (hashed_password, email)
    )

    conn.commit()
    conn.close()

    return True