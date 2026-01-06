#!/usr/bin/env python3
"""
RentVerify - Twilio SMS Test Script
-----------------------------------
This script tests the Twilio SMS functionality by sending a test message.
DO NOT DEPLOY THIS FILE - It's for local testing only.

Usage:
    python send_test.py

Requirements:
    - .env file with TWILIO credentials
    - twilio and python-dotenv packages installed
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# ==================== Environment Configuration ====================

# Get the absolute path to the .env file
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

# Load environment variables
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print(f"✓ Loaded .env from: {ENV_PATH}")
else:
    print(f"❌ ERROR: .env file not found at: {ENV_PATH}")
    print("Please create a .env file with your Twilio credentials.")
    sys.exit(1)

# ==================== Validate Environment Variables ====================

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TEST_RECIPIENT_PHONE = os.getenv("TEST_RECIPIENT_PHONE")

# Validate all required environment variables
missing_vars = []
if not TWILIO_ACCOUNT_SID:
    missing_vars.append("TWILIO_ACCOUNT_SID")
if not TWILIO_AUTH_TOKEN:
    missing_vars.append("TWILIO_AUTH_TOKEN")
if not TWILIO_PHONE_NUMBER:
    missing_vars.append("TWILIO_PHONE_NUMBER")
if not TEST_RECIPIENT_PHONE:
    missing_vars.append("TEST_RECIPIENT_PHONE")

if missing_vars:
    print("❌ ERROR: Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nPlease add these to your .env file.")
    sys.exit(1)

print("✓ All environment variables loaded successfully")

# ==================== Send Test SMS ====================

def send_test_sms():
    """Send a test SMS using Twilio."""
    try:
        print("\n" + "="*50)
        print("TWILIO SMS TEST")
        print("="*50)
        print(f"From: {TWILIO_PHONE_NUMBER}")
        print(f"To: {TEST_RECIPIENT_PHONE}")
        print("-"*50)
        
        # Create Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✓ Twilio client initialized")
        
        # Send SMS
        message = client.messages.create(
            body="🎉 RentVerify SMS Test: Your Twilio integration is working perfectly!",
            from_=TWILIO_PHONE_NUMBER,
            to=TEST_RECIPIENT_PHONE
        )
        
        # Print success details
        print("✓ Message sent successfully!")
        print(f"\nMessage Details:")
        print(f"  - SID: {message.sid}")
        print(f"  - Status: {message.status}")
        print(f"  - Direction: {message.direction}")
        print(f"  - Date Created: {message.date_created}")
        print("="*50)
        print("\n✅ TEST PASSED: Check your phone for the message!")
        
        return True
        
    except TwilioRestException as e:
        print("\n❌ TWILIO API ERROR:")
        print(f"   Error Code: {e.code}")
        print(f"   Error Message: {e.msg}")
        print(f"   Status: {e.status}")
        print("\nCommon issues:")
        print("  - Invalid phone number format (use E.164: +1234567890)")
        print("  - Twilio account not verified")
        print("  - Insufficient Twilio credits")
        print("  - Invalid credentials")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("Please check your internet connection and credentials.")
        return False

# ==================== Main Execution ====================

if __name__ == '__main__':
    print("\n🚀 Starting Twilio SMS test...")
    success = send_test_sms()
    sys.exit(0 if success else 1)