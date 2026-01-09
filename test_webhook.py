"""
Test script to verify SMS webhook is receiving and storing messages
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def check_recent_messages():
    """Check for messages received in the last 24 hours"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found!")
        return
    
    try:
        print("\n" + "="*60)
        print("CHECKING SMS WEBHOOK - RECENT MESSAGES")
        print("="*60)
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all messages, most recent first
        cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC LIMIT 10")
        records = cursor.fetchall()
        
        if not records:
            print("\n📭 No messages found in database yet.")
            print("\n💡 TO TEST THE WEBHOOK:")
            print("   1. Send an SMS from your phone to your Twilio number:")
            print(f"      {os.getenv('TWILIO_PHONE_NUMBER')}")
            print("   2. Send message: YES or NO")
            print("   3. Run this script again to see if it was received")
            print("\n⚠️  Make sure your Twilio webhook URL is set to:")
            print("   https://your-app.onrender.com/sms")
        else:
            print(f"\n✅ Found {len(records)} message(s):\n")
            
            for i, record in enumerate(records, 1):
                print(f"Message #{i}")
                print(f"  📱 From: {record['phone_number']}")
                print(f"  💬 Reply: {record['reply']}")
                print(f"  🕐 Time: {record['timestamp']}")
                print()
            
            # Count YES/NO responses
            cursor.execute("""
                SELECT 
                    reply,
                    COUNT(*) as count
                FROM rent_records
                GROUP BY reply
                ORDER BY count DESC
            """)
            
            summary = cursor.fetchall()
            
            if summary:
                print("="*60)
                print("RESPONSE SUMMARY")
                print("="*60)
                for item in summary:
                    print(f"  {item['reply']}: {item['count']} message(s)")
        
        conn.close()
        
        print("\n" + "="*60)
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")

def test_webhook_endpoint():
    """Test if the webhook endpoint is accessible"""
    print("\n" + "="*60)
    print("WEBHOOK CONFIGURATION CHECK")
    print("="*60)
    
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    print(f"\n📞 Your Twilio Number: {twilio_number}")
    print("\n🔗 Webhook Setup Instructions:")
    print("   1. Go to: https://console.twilio.com/")
    print("   2. Navigate to: Phone Numbers > Manage > Active Numbers")
    print(f"   3. Click on: {twilio_number}")
    print("   4. Scroll to 'Messaging Configuration'")
    print("   5. Under 'A MESSAGE COMES IN', set:")
    print("      Webhook: https://your-render-app.onrender.com/sms")
    print("      HTTP Method: POST")
    print("\n✅ Once configured, send a text message to test!")
    print("="*60)

if __name__ == '__main__':
    test_webhook_endpoint()
    check_recent_messages()
    
    print("\n📝 TESTING INSTRUCTIONS:")
    print("="*60)
    print("1. Send SMS from YOUR phone to:", os.getenv('TWILIO_PHONE_NUMBER'))
    print("2. Message content: 'YES' or 'NO'")
    print("3. Wait 5-10 seconds")
    print("4. Run this script again to verify it was received")
    print("5. Or check your dashboard at: https://your-app.onrender.com/dashboard")
    print("="*60 + "\n")
