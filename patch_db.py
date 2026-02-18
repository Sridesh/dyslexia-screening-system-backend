import sqlite3
import os
import sys

print("DEBUG: Starting patch_db.py")
db_path = "sql_app.db"
if not os.path.exists(db_path):
    print(f"ERROR: {db_path} not found!")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("DEBUG: Connected to DB")
    
    # Check columns
    cursor.execute("PRAGMA table_info(item)")
    columns = [r[1] for r in cursor.fetchall()]
    print(f"DEBUG: Current columns: {columns}")
    
    if "options_json" not in columns:
        print("DEBUG: Adding options_json...")
        cursor.execute("ALTER TABLE item ADD COLUMN options_json TEXT")
        conn.commit()
        print("DEBUG: SUCCESS - Column added.")
    else:
        print("DEBUG: Column already exists.")
        
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
