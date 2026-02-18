import sqlite3
import os

DB_FILE = "sql_app.db"

def verify():
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check columns
        cursor.execute("PRAGMA table_info(item)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Columns in 'item': {columns}")
        
        # Check count
        cursor.execute("SELECT COUNT(*) FROM item")
        count = cursor.fetchone()[0]
        print(f"Total items in 'item': {count}")
        
        if "prompt_type" in columns and count == 24:
            print("VERIFICATION SUCCESS: Schema and data are correct.")
        else:
            print(f"VERIFICATION FAILURE: Expected prompt_type and 24 items, got {columns} and {count} items.")
            
        conn.close()
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    verify()
