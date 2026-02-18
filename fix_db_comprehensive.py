import sqlite3
import os

DB_FILE = "sql_app.db"

# Schema mapping based on models
# Table -> { Column: (Type, Default/Constraints) }
SCHEMA_DEFINITIONS = {
    "item": {
        "id": "INTEGER PRIMARY KEY",
        "module": "VARCHAR NOT NULL",
        "difficulty": "FLOAT NOT NULL",
        "max_time_s": "FLOAT",
        "prompt_text": "TEXT",
        "prompt_media": "VARCHAR",
        "correct_option": "VARCHAR",
        "options_json": "TEXT",
        "is_active": "BOOLEAN DEFAULT 1",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
    "child": {
        "id": "INTEGER PRIMARY KEY",
        "external_id": "VARCHAR",
        "name": "VARCHAR",
        "dob": "DATETIME",
        "gender": "VARCHAR",
        "language": "VARCHAR",
        "notes": "TEXT",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
    "test": {
        "id": "INTEGER PRIMARY KEY",
        "child_id": "INTEGER",
        "start_time": "DATETIME",
        "end_time": "DATETIME",
        "final_risk_label": "VARCHAR",
        "final_risk_score": "FLOAT",
        "final_risk_entropy": "FLOAT",
        "total_items": "INTEGER",
        "total_time_s": "FLOAT",
        "final_fatigue_level": "FLOAT",
        "device_id": "VARCHAR",
        "version": "VARCHAR",
        "notes": "TEXT",
        "session_state": "TEXT", # JSON
        "status": "VARCHAR DEFAULT 'in_progress'",
        "created_at": "DATETIME",
        "updated_at": "DATETIME"
    },
}

def fix_database():
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"Connected to {DB_FILE}")

    for table, columns_def in SCHEMA_DEFINITIONS.items():
        print(f"Checking table '{table}'...")
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"  [WARNING] Table '{table}' does not exist. Skipping.")
            continue

        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        for col_name, col_def in columns_def.items():
            if col_name not in existing_cols:
                print(f"  [MISSING] Column '{col_name}' is missing. Adding...")
                try:
                    sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"
                    print(f"    Executing: {sql}")
                    cursor.execute(sql)
                    print(f"    [SUCCESS] Added '{col_name}'")
                except Exception as e:
                    print(f"    [ERROR] Failed to add '{col_name}': {e}")
            else:
                pass 

    conn.commit()
    conn.close()
    print("Database repair complete.")

if __name__ == "__main__":
    fix_database()
