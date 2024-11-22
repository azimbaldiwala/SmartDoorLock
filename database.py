# database.py
import sqlite3

# Database setup function
def init_db():
    conn = sqlite3.connect('access_control.db')
    cursor = conn.cursor()

    # Create users table with is_24_hours column for 24-hour access
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        UID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        pin TEXT,
        email_id TEXT,
        access_start TEXT,
        access_end TEXT,
        is_24_hours INTEGER DEFAULT 0  -- 0 means false, 1 means true
    )
    ''')

    # Create access control table for unlock history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_control (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        UID INTEGER,
        access_time TEXT,
        access_date TEXT,
        result TEXT,
        FOREIGN KEY (UID) REFERENCES users (UID)
    )
    ''')

    # Table for unsuccessful login attempts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS unsuccessful_attempts (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        UID INTEGER,
        attempt_time TEXT,
        attempt_date TEXT,
        FOREIGN KEY (UID) REFERENCES users (UID)
    )
    ''')

    conn.commit()
    conn.close()

# Call this function to initialize the database
if __name__ == "__main__":
    init_db()
