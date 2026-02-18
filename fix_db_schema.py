import sqlite3
import os

DB_FILE = "sql_app.db"

if not os.path.exists(DB_FILE):
    print(f"Database file {DB_FILE} not found.")
    exit(1)

try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(item)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "correct_option" in columns:
        print("Column 'correct_option' already exists in 'item' table.")
    else:
        print("Column 'correct_option' missing. Adding it...")
        cursor.execute("ALTER TABLE item ADD COLUMN correct_option VARCHAR")
        conn.commit()
        print("Column 'correct_option' added successfully.")
        
    conn.close()

except Exception as e:
    print(f"Error: {e}")
