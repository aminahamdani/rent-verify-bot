"""
Twilio Service - SMS Processing Logic
"""

import os
from datetime import datetime
from twilio.rest import Client

def process_incoming_sms(phone_number, reply, timestamp, db_service, mask_phone_number, logger):
    """
    Process an incoming SMS and store it in the database.
    For landlord replies (yes/no), store in incoming_messages table.
    Also keep legacy rent_records table for backward compatibility.
    
    Args:
        phone_number (str): Sender's phone number
        reply (str): Message body
        timestamp (str): Timestamp
        db_service (module): Database service module
        mask_phone_number (func): Masking function
        logger (Logger): Logger instance
    Returns:
        bool: True if successful, False otherwise
    """
    masked_phone = mask_phone_number(phone_number)
    try:
        conn = db_service.get_db_connection()
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        # Determine record type based on message content
        # Default to landlord (can be overridden via environment variable DEFAULT_RECORD_TYPE)
        default_type = os.getenv('DEFAULT_RECORD_TYPE', 'landlord').lower()
        record_type = default_type if default_type in ['tenant', 'landlord'] else 'landlord'
        
        reply_upper = reply.upper().strip()
        
        # Check for landlord keywords
        landlord_keywords = ['LANDLORD', 'OWNER', 'LL', 'PROPERTY OWNER', 'RENTAL OWNER']
        tenant_keywords = ['TENANT', 'RENTER', 'RESIDENT', 'TT']
        
        # If message contains landlord keywords, set to landlord
        if any(keyword in reply_upper for keyword in landlord_keywords):
            record_type = 'landlord'
        # If message contains tenant keywords, set to tenant
        elif any(keyword in reply_upper for keyword in tenant_keywords):
            record_type = 'tenant'
        
        # Check if message is yes/no for landlords
        is_yes = False
        is_no = False
        if record_type == 'landlord':
            if reply_upper in ['YES', 'Y', '1']:
                is_yes = True
            elif reply_upper in ['NO', 'N', '0']:
                is_no = True
        
        # Store in incoming_messages table for landlord replies
        if record_type == 'landlord':
            if DATABASE_URL:
                # PostgreSQL
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                # Use CURRENT_TIMESTAMP for received_at
                cursor.execute(
                    "INSERT INTO incoming_messages (landlord_phone, message_body, received_at, is_yes, is_no) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s)",
                    (phone_number, reply, is_yes, is_no)
                )
            else:
                # SQLite
                cursor = conn.cursor()
                # Convert boolean to integer for SQLite
                cursor.execute(
                    "INSERT INTO incoming_messages (landlord_phone, message_body, received_at, is_yes, is_no) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)",
                    (phone_number, reply, 1 if is_yes else 0, 1 if is_no else 0)
                )
        
        # Store in appropriate table based on record type
        if record_type == 'landlord':
            # Store in landlord_record table
            if DATABASE_URL:
                # PostgreSQL
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(
                    "INSERT INTO landlord_record (phone_number, reply, timestamp) VALUES (%s, %s, %s)",
                    (masked_phone, reply, timestamp)
                )
            else:
                # SQLite
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO landlord_record (phone_number, reply, timestamp) VALUES (?, ?, ?)",
                    (masked_phone, reply, timestamp)
                )
        else:
            # Store in tenants table for tenant records
            # Note: tenants table requires name and rent_amount, so we use defaults
            if DATABASE_URL:
                # PostgreSQL
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                # Insert with default values for required fields
                cursor.execute(
                    "INSERT INTO tenants (phone_number, reply, timestamp, name, address, rent_amount) VALUES (%s, %s, %s, %s, %s, %s)",
                    (masked_phone, reply, timestamp, 'Unknown', 'Unknown', 0.00)
                )
            else:
                # SQLite
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tenants (phone_number, reply, timestamp, name, address, rent_amount) VALUES (?, ?, ?, ?, ?, ?)",
                    (masked_phone, reply, timestamp, 'Unknown', 'Unknown', 0.0)
                )
        
        conn.commit()
        conn.close()
        logger.info(f"Message recorded in database for {masked_phone} (type: {record_type})")
        return True
    except Exception as e:
        logger.error(f"Error in SMS handler: {e}")
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False


def send_sms_to_landlord(landlord_name, landlord_phone, landlord_address, landlord_email, 
                         message_body, db_service, logger):
    """
    Send SMS message to landlord via Twilio and store in outgoing_messages table.
    
    Args:
        landlord_name (str): Landlord's name
        landlord_phone (str): Landlord's phone number
        landlord_address (str): Landlord's address
        landlord_email (str): Landlord's email (optional)
        message_body (str): SMS message body
        db_service (module): Database service module
        logger (Logger): Logger instance
    
    Returns:
        tuple: (success: bool, message_sid: str or None, error_message: str or None)
    """
    try:
        # Get Twilio credentials
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, twilio_phone]):
            error_msg = "Twilio credentials not configured"
            logger.error(error_msg)
            return False, None, error_msg
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send SMS via Twilio
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone,
            to=landlord_phone
        )
        
        message_sid = message.sid
        logger.info(f"SMS sent to {landlord_phone} (SID: {message_sid})")
        
        # Store in outgoing_messages table
        conn = db_service.get_db_connection()
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if DATABASE_URL:
            # PostgreSQL
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """INSERT INTO outgoing_messages 
                   (landlord_name, landlord_phone, landlord_address, landlord_email, 
                    message_body, sent_at, twilio_message_sid, status) 
                   VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, 'sent')""",
                (landlord_name, landlord_phone, landlord_address, landlord_email, 
                 message_body, message_sid)
            )
        else:
            # SQLite
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO outgoing_messages 
                   (landlord_name, landlord_phone, landlord_address, landlord_email, 
                    message_body, sent_at, twilio_message_sid, status) 
                   VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 'sent')""",
                (landlord_name, landlord_phone, landlord_address, landlord_email, 
                 message_body, message_sid)
            )
        
        conn.commit()
        conn.close()
        logger.info(f"Outgoing message stored in database for {landlord_name} ({landlord_phone})")
        return True, message_sid, None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error sending SMS to landlord: {e}")
        if 'conn' in locals():
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False, None, error_msg
