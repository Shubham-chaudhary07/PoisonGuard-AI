from src.db import connect_db

def save_dataset(username, filename, total, suspicious, risk):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO datasets (username, filename, total_rows, suspicious_rows, risk_percent) VALUES (%s, %s, %s, %s, %s)",
        (username, filename, total, suspicious, risk)
    )

    conn.commit()


def get_user_datasets(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT filename, total_rows, suspicious_rows, risk_percent, upload_time FROM datasets WHERE username=%s",
        (username,)
    )

    return cursor.fetchall()