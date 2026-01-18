"""Simple test to verify database table structure"""
import sqlite3
from pathlib import Path

def test_database():
    db_path = Path('instance/rent_data.db')
    
    if not db_path.exists():
        print(f"[FAIL] Database not found at {db_path}")
        print("Please run 'python app_local.py' first to initialize the database")
        return False
    
    print(f"[OK] Database found at {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check required tables
    required_tables = ['outgoing_messages', 'incoming_messages', 'landlord_record', 'tenants']
    
    print("\n[TEST] Checking table existence:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    all_exist = True
    for table in required_tables:
        exists = table in existing_tables
        status = "[OK]" if exists else "[FAIL]"
        print(f"  {status} {table}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n[FAIL] Some required tables are missing!")
        conn.close()
        return False
    
    # Check tenants table columns
    print("\n[TEST] Checking tenants table structure:")
    cursor.execute("PRAGMA table_info(tenants)")
    tenant_cols = [col[1] for col in cursor.fetchall()]
    print(f"  Columns: {', '.join(tenant_cols)}")
    
    has_reply = 'reply' in tenant_cols
    has_timestamp = 'timestamp' in tenant_cols
    
    print(f"  [{'OK' if has_reply else 'FAIL'}] 'reply' column")
    print(f"  [{'OK' if has_timestamp else 'FAIL'}] 'timestamp' column")
    
    # Check landlord_record table structure
    print("\n[TEST] Checking landlord_record table structure:")
    cursor.execute("PRAGMA table_info(landlord_record)")
    landlord_cols = [col[1] for col in cursor.fetchall()]
    print(f"  Columns: {', '.join(landlord_cols)}")
    
    required_landlord_cols = ['phone_number', 'reply', 'timestamp']
    landlord_ok = all(col in landlord_cols for col in required_landlord_cols)
    
    print(f"  [{'OK' if landlord_ok else 'FAIL'}] Required columns present")
    
    # Count records
    print("\n[INFO] Record counts:")
    for table in required_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
        except Exception as e:
            print(f"  {table}: Error - {e}")
    
    conn.close()
    
    success = all_exist and has_reply and has_timestamp and landlord_ok
    return success

if __name__ == '__main__':
    print("=" * 60)
    print("TESTING DATABASE STRUCTURE")
    print("=" * 60)
    
    success = test_database()
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] All database structure tests passed!")
    else:
        print("[FAIL] Some tests failed. Please check the output above.")
    print("=" * 60)
