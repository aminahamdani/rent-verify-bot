import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = "+16802082305"

# Your personal phone number (replace with your actual number)
my_personal_phone = "+16464089380"

# Create Twilio client
client = Client(account_sid, auth_token)

# Send SMS
message = client.messages.create(
    body="Hello Amina! The bot is working.",
    from_=from_number,
    to=my_personal_phone
)

# Print message ID
print(f"Message sent! Message ID: {message.sid}")