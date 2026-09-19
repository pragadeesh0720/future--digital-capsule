import sqlite3


DATABASE = "capsules.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def create_table():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS capsules (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            encrypted_message BLOB NOT NULL,

            salt BLOB NOT NULL,

            unlock_time TEXT NOT NULL,

            created_at TEXT NOT NULL,

            failed_attempts INTEGER DEFAULT 0,

            locked_until TEXT

        )
    """)

    connection.commit()

    connection.close()