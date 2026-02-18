import sqlite3
import os

DB_FILE = "sql_app.db"

# Minimal expected columns for critical tables
EXPECTED = {
    "item": ["options_json", "correct_option", "is_active", "prompt_media", "created_at"],
    "test": ["session_state", "status", "version", "device_id"],
    "child": ["external_id"]
}

try:
    if not os.path.exists(DB_FILE):
        print(f"DB not found: {DB_FILE}")
        exit(1)
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("--- Verification Report ---")
    for table, columns in EXPECTED.items():
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        missing = [c for c in columns if c not in existing_cols]
        if missing:
            print(f"[FAIL] {table} missing: {missing}")
        else:
            print(f"[OK] {table} has all checked columns.")
            
    conn.close()
    print("--- End Verification ---")
except Exception as e:
    print(f"Error: {e}")
