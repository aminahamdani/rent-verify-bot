"""
Manual table creation script for PostgreSQL database
Run this to create tables on your Render/Neon database
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables():
    """Create the required database tables"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables!")
        return
    
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Creating 'payments' table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                phone_number TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("Creating 'rent_records' table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rent_records (
                phone_number TEXT,
                reply TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        print("✅ Tables created successfully!")
        
        # Verify tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\nExisting tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        print("\n✅ Database setup complete!")
        
    except psycopg2.Error as e:
        print(f"❌ ERROR: {e}")
        if conn:
            conn.rollback()

if __name__ == '__main__':
    create_tables()
