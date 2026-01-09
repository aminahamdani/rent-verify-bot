"""
Render Deployment Verification Script
Tests database connection, table creation, and basic operations
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test 1: Check if DATABASE_URL is set and can connect"""
    print("\n" + "="*60)
    print("TEST 1: Database Connection")
    print("="*60)
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ FAILED: DATABASE_URL not found in environment variables")
        return False
    
    print(f"✓ DATABASE_URL found: {database_url[:20]}...{database_url[-20:]}")
    
    try:
        conn = psycopg2.connect(database_url)
        print("✓ Successfully connected to PostgreSQL database")
        
        # Get database info
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print(f"✓ Database version: {db_version[:50]}...")
        
        conn.close()
        print("✅ PASSED: Database connection successful\n")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ FAILED: Database connection error: {e}\n")
        return False


def test_tables_exist():
    """Test 2: Check if required tables exist"""
    print("="*60)
    print("TEST 2: Table Creation")
    print("="*60)
    
    database_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check for payments table
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'payments'
            );
        """)
        payments_exists = cursor.fetchone()['exists']
        
        if payments_exists:
            print("✓ Table 'payments' exists")
            
            # Get column info
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'payments'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"    - {col['column_name']}: {col['data_type']}")
        else:
            print("❌ Table 'payments' does NOT exist")
        
        # Check for rent_records table
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'rent_records'
            );
        """)
        rent_records_exists = cursor.fetchone()['exists']
        
        if rent_records_exists:
            print("✓ Table 'rent_records' exists")
            
            # Get column info
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'rent_records'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"    - {col['column_name']}: {col['data_type']}")
        else:
            print("❌ Table 'rent_records' does NOT exist")
        
        conn.close()
        
        if payments_exists and rent_records_exists:
            print("✅ PASSED: All required tables exist\n")
            return True
        else:
            print("❌ FAILED: Some tables are missing\n")
            return False
            
    except psycopg2.Error as e:
        print(f"❌ FAILED: Error checking tables: {e}\n")
        return False


def test_insert_and_query():
    """Test 3: Test insert and query operations"""
    print("="*60)
    print("TEST 3: Insert and Query Operations")
    print("="*60)
    
    database_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Test insert
        test_phone = "+1234567890"
        test_reply = "YES"
        test_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO rent_records (phone_number, reply, timestamp) VALUES (%s, %s, %s)",
            (test_phone, test_reply, test_timestamp)
        )
        conn.commit()
        print(f"✓ Successfully inserted test record: {test_phone}")
        
        # Test query
        cursor.execute("SELECT * FROM rent_records WHERE phone_number = %s", (test_phone,))
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Successfully queried record:")
            print(f"  - Phone: {result['phone_number']}")
            print(f"  - Reply: {result['reply']}")
            print(f"  - Timestamp: {result['timestamp']}")
        else:
            print("❌ Could not retrieve inserted record")
            conn.close()
            return False
        
        # Count total records
        cursor.execute("SELECT COUNT(*) as count FROM rent_records")
        count = cursor.fetchone()['count']
        print(f"✓ Total records in rent_records table: {count}")
        
        # Clean up test record
        cursor.execute("DELETE FROM rent_records WHERE phone_number = %s", (test_phone,))
        conn.commit()
        print(f"✓ Test record cleaned up")
        
        conn.close()
        print("✅ PASSED: Insert and query operations working\n")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ FAILED: Error during insert/query: {e}\n")
        return False


def test_environment_variables():
    """Test 4: Check all required environment variables"""
    print("="*60)
    print("TEST 4: Environment Variables")
    print("="*60)
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'ADMIN_USERNAME',
        'ADMIN_PASSWORD'
    ]
    
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if var in ['SECRET_KEY', 'ADMIN_PASSWORD', 'DATABASE_URL']:
                display_value = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_present = False
    
    if all_present:
        print("✅ PASSED: All required environment variables are set\n")
        return True
    else:
        print("❌ FAILED: Some environment variables are missing\n")
        return False


def main():
    """Run all tests"""
    print("\n" + "🔍" + " "*20 + "RENDER DEPLOYMENT VERIFICATION" + " "*20 + "🔍")
    print("Starting verification tests...\n")
    
    results = {
        'Environment Variables': test_environment_variables(),
        'Database Connection': test_database_connection(),
        'Table Creation': test_tables_exist(),
        'Insert/Query Operations': test_insert_and_query()
    }
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Your deployment is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")


if __name__ == '__main__':
    main()
