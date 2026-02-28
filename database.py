import sqlite3

DB_NAME = "expense.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        monthly_limit REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()