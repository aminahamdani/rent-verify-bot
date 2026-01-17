"""
Update existing records to landlord type
This script updates all records in the database to have record_type = 'landlord'
"""

import os
import sys
from dotenv import load_dotenv
from services import db_service

# Load environment variables
load_dotenv()

def update_records_to_landlord():
    """Update all existing records to have record_type = 'landlord'"""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    try:
        conn = db_service.get_db_connection()
        
        # First, ensure record_type column exists (for SQLite)
        if not DATABASE_URL:
            cursor = conn.cursor()
            # Check if record_type column exists in SQLite
            cursor.execute("PRAGMA table_info(rent_records)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'record_type' not in columns:
                print("Adding record_type column to SQLite database...")
                cursor.execute("ALTER TABLE rent_records ADD COLUMN record_type TEXT DEFAULT 'tenant'")
                conn.commit()
        
        # Update all records to 'landlord'
        if DATABASE_URL:
            # PostgreSQL
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Count records to update
            cursor.execute("SELECT COUNT(*) as count FROM rent_records WHERE record_type IS NULL OR record_type = 'tenant'")
            count_result = cursor.fetchone()
            count_to_update = count_result['count'] if count_result else 0
            
            if count_to_update > 0:
                print(f"Found {count_to_update} record(s) to update...")
                cursor.execute("UPDATE rent_records SET record_type = 'landlord' WHERE record_type IS NULL OR record_type = 'tenant'")
                conn.commit()
                print(f"✅ Successfully updated {count_to_update} record(s) to 'landlord'")
            else:
                print("No records to update (all records are already 'landlord' or empty table)")
            
            # Show updated records
            cursor.execute("SELECT COUNT(*) as count, record_type FROM rent_records GROUP BY record_type")
            results = cursor.fetchall()
            print("\n📊 Current record distribution:")
            for row in results:
                print(f"  - {row['record_type'] or 'NULL'}: {row['count']} record(s)")
        
        else:
            # SQLite
            cursor = conn.cursor()
            
            # Count records to update
            cursor.execute("SELECT COUNT(*) FROM rent_records WHERE record_type IS NULL OR record_type = 'tenant'")
            count_to_update = cursor.fetchone()[0]
            
            if count_to_update > 0:
                print(f"Found {count_to_update} record(s) to update...")
                cursor.execute("UPDATE rent_records SET record_type = 'landlord' WHERE record_type IS NULL OR record_type = 'tenant'")
                conn.commit()
                print(f"✅ Successfully updated {count_to_update} record(s) to 'landlord'")
            else:
                print("No records to update (all records are already 'landlord' or empty table)")
            
            # Show updated records
            cursor.execute("SELECT COUNT(*) as count, record_type FROM rent_records GROUP BY record_type")
            results = cursor.fetchall()
            print("\n📊 Current record distribution:")
            for row in results:
                print(f"  - {row[1] or 'NULL'}: {row[0]} record(s)")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Update complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating records: {e}")
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False


if __name__ == '__main__':
    print("="*60)
    print("Updating Records to 'landlord' Type")
    print("="*60)
    
    # Check which database
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        print(f"📊 Database: PostgreSQL (Production)")
        # Mask the password in the URL for display
        display_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL[:50]
        print(f"📍 Location: {display_url}")
    else:
        print(f"📊 Database: SQLite (Local)")
        print(f"📍 Location: instance/rent_data.db")
    
    print()
    
    success = update_records_to_landlord()
    
    if success:
        print("\n💡 Tip: Refresh your dashboard to see the updated records in the 'Landlords' tab")
        sys.exit(0)
    else:
        print("\n❌ Update failed. Please check the error message above.")
        sys.exit(1)
