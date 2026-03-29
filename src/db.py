import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shubham07@",  # 🔴 change this
        database="poison_app"
    )