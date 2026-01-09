import sqlite3
import os

db_path = os.path.join('instance', 'rent_data.db')
print(f"Checking database: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nTables: {[t[0] for t in tables]}")
    
    # Check rent_records
    if any('rent_records' in str(t) for t in tables):
        cursor.execute("SELECT COUNT(*) FROM rent_records")
        count = cursor.fetchone()[0]
        print(f"Records in rent_records: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM rent_records LIMIT 5")
            records = cursor.fetchall()
            print(f"\nSample records: {records}")
    
    conn.close()
