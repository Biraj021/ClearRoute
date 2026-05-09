import sqlite3
import os

db_path = "users.db"

# Backup old db just in case
if os.path.exists(db_path):
    os.rename(db_path, db_path + ".bak")
    print(f"Backed up existing {db_path} to {db_path}.bak")

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT UNIQUE,
    mobile TEXT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    location TEXT,
    diseases TEXT,
    weight REAL
)
""")

conn.commit()
conn.close()
print("Database recreated with full schema.")
