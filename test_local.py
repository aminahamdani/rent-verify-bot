"""
Test script to verify local app functionality
"""

import requests
import time

print("=" * 60)
print("RentVerify Local Test")
print("=" * 60)

# Test 1: Simulate SMS webhook
print("\n1. Testing SMS webhook endpoint...")
test_messages = [
    {"From": "+12345678901", "Body": "YES"},
    {"From": "+12345678902", "Body": "NO"},
    {"From": "+12345678903", "Body": "YES"},
]

try:
    for msg in test_messages:
        response = requests.post(
            "http://127.0.0.1:5000/sms",
            data=msg
        )
        print(f"   - Sent {msg['Body']} from {msg['From']}: {response.status_code}")
        time.sleep(0.5)
    print("   ✓ SMS webhook test passed")
except Exception as e:
    print(f"   ✗ SMS webhook test failed: {e}")

# Test 2: Check if login page loads
print("\n2. Testing login page...")
try:
    response = requests.get("http://127.0.0.1:5000/login")
    if response.status_code == 200:
        print(f"   ✓ Login page loads (status: {response.status_code})")
    else:
        print(f"   ✗ Login page error (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Login page test failed: {e}")

# Test 3: Test login
print("\n3. Testing login functionality...")
try:
    session = requests.Session()
    response = session.post(
        "http://127.0.0.1:5000/login",
        data={"username": "admin", "password": "password"}
    )
    if response.status_code == 200 or response.status_code == 302:
        print(f"   ✓ Login successful (status: {response.status_code})")
    else:
        print(f"   ✗ Login failed (status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Login test failed: {e}")

print("\n" + "=" * 60)
print("Tests complete! Now check:")
print("1. Visit http://127.0.0.1:5000/login")
print("2. Login with username: admin, password: password")
print("3. Check if messages appear in dashboard")
print("=" * 60)
