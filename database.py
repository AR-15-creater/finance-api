import sqlite3
DB_NAME = "expense.db"

def get_connection():
    return sqlite3.connect("finance.db")

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULl,
            category TEXT NOT NULL)
    """ )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Category TEXT NOT NULL,
            monthly_limit REAL NOT NULL)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT)
""")

    conn.commit()
    conn.close()
