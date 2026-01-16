"""
Twilio Service - SMS Processing Logic
"""

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
        cursor = conn.cursor()
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
        return False
