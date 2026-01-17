"""
Twilio Service - SMS Processing Logic
"""

import os

def process_incoming_sms(phone_number, reply, timestamp, db_service, mask_phone_number, logger):
    """
    Process an incoming SMS and store it in the database.
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
        
        if DATABASE_URL:
            # PostgreSQL - use %s placeholders
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "INSERT INTO rent_records (phone_number, reply, timestamp, record_type) VALUES (%s, %s, %s, %s)",
                (masked_phone, reply, timestamp, record_type)
            )
        else:
            # SQLite - use ? placeholders
            cursor = conn.cursor()
            # Check if record_type column exists
            try:
                cursor.execute(
                    "INSERT INTO rent_records (phone_number, reply, timestamp, record_type) VALUES (?, ?, ?, ?)",
                    (masked_phone, reply, timestamp, record_type)
                )
            except:
                # Fallback for older schema
                cursor.execute(
                    "INSERT INTO rent_records (phone_number, reply, timestamp) VALUES (?, ?, ?)",
                    (masked_phone, reply, timestamp)
                )
        
        conn.commit()
        conn.close()
        logger.info(f"Message recorded in database for {masked_phone}")
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
