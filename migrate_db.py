import sqlite3
import os

db_path = r"c:\Users\VICTUS 16\OneDrive\Desktop\detch website\flask deutchAI\instance\deutschai.db"

if not os.path.exists(db_path):
    # Check if instance folder is not used
    db_path = r"c:\Users\VICTUS 16\OneDrive\Desktop\detch website\flask deutchAI\deutschai.db"

print(f"Targeting database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'target_language' not in columns:
        print("Adding target_language column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN target_language VARCHAR(10) NOT NULL DEFAULT 'de'")
        conn.commit()
        print("Column added successfully.")
    else:
        print("Column 'target_language' already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
