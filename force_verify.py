import sqlite3
import sys

print("Starting verification...")
try:
    conn = sqlite3.connect('sql_app.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(item)")
    rows = c.fetchall()
    print("Columns in item table:")
    for r in rows:
        print(r)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
print("Verification complete.")
