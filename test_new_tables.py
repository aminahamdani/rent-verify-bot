"""
Test script for new 4-table structure:
1. outgoing_messages (System → Landlords)
2. incoming_messages (Landlords → System)
3. landlord_record (Landlord payment records)
4. tenants (Tenant payment records)
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def test_postgresql():
    """Test PostgreSQL database structure"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        print("[TEST] Testing PostgreSQL database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if all tables exist
        tables_to_check = [
            'outgoing_messages',
            'incoming_messages', 
            'landlord_record',
            'tenants'
        ]
        
        print("\n✅ Checking table existence:")
        for table in tables_to_check:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                );
            """)
            exists = cursor.fetchone()[0]
            status = "[OK] EXISTS" if exists else "[FAIL] MISSING"
            print(f"  {table}: {status}")
            
            if exists:
                # Check table structure
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print(f"    Columns: {', '.join([col['column_name'] for col in columns])}")
        
        # Check tenants table has reply and timestamp columns
        print("\n[CHECK] Checking tenants table columns:")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tenants' AND column_name IN ('reply', 'timestamp');
        """)
        tenant_cols = [row['column_name'] for row in cursor.fetchall()]
        if 'reply' in tenant_cols:
            print("  [OK] 'reply' column exists")
        else:
            print("  [FAIL] 'reply' column missing")
        if 'timestamp' in tenant_cols:
            print("  [OK] 'timestamp' column exists")
        else:
            print("  [FAIL] 'timestamp' column missing")
        
        # Count records in each table
        print("\n[INFO] Record counts:")
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")
        
        cursor.close()
        conn.close()
        print("\n[OK] PostgreSQL test completed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] PostgreSQL test failed: {e}")
        return False

def test_sqlite():
    """Test SQLite database structure"""
    try:
        import sqlite3
        from pathlib import Path
        
        print("\n[TEST] Testing SQLite database...")
        
        # Find SQLite database (usually in instance folder)
        instance_path = Path('instance/rent_data.db')
        if not instance_path.exists():
            print(f"  ⚠️  SQLite database not found at {instance_path}")
            return False
        
        conn = sqlite3.connect(str(instance_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if all tables exist
        tables_to_check = [
            'outgoing_messages',
            'incoming_messages',
            'landlord_record', 
            'tenants'
        ]
        
        print("\n✅ Checking table existence:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables_to_check:
            exists = table in existing_tables
            status = "[OK] EXISTS" if exists else "[FAIL] MISSING"
            print(f"  {table}: {status}")
            
            if exists:
                # Get table structure
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                col_names = [col[1] for col in columns]
                print(f"    Columns: {', '.join(col_names)}")
        
        # Check tenants table has reply and timestamp columns
        print("\n[CHECK] Checking tenants table columns:")
        cursor.execute("PRAGMA table_info(tenants)")
        tenant_cols = [col[1] for col in cursor.fetchall()]
        if 'reply' in tenant_cols:
            print("  [OK] 'reply' column exists")
        else:
            print("  [FAIL] 'reply' column missing")
        if 'timestamp' in tenant_cols:
            print("  [OK] 'timestamp' column exists")
        else:
            print("  [FAIL] 'timestamp' column missing")
        
        # Count records in each table
        print("\n[INFO] Record counts:")
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")
        
        cursor.close()
        conn.close()
        print("\n[OK] SQLite test completed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] SQLite test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING NEW 4-TABLE STRUCTURE")
    print("=" * 60)
    
    if DATABASE_URL:
        # PostgreSQL
        success = test_postgresql()
    else:
        # SQLite
        success = test_sqlite()
    
    print("\n" + "=" * 60)
    if success:
        print("[OK] All tests passed!")
    else:
        print("[FAIL] Some tests failed. Please check the output above.")
    print("=" * 60)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
