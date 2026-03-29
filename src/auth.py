import bcrypt
from src.db import connect_db

# SIGNUP
def signup(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


# LOGIN
def login(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username=%s",
        (username,)
    )

    result = cursor.fetchone()

    if result:
        stored_password = result[0]

        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return True

    return False