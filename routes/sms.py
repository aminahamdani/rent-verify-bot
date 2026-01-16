"""
SMS Blueprint - Twilio Webhook Handler

This module defines the SMS blueprint that handles incoming SMS messages from Twilio.
It is designed to work with both the production app (PostgreSQL) and local development 
app (SQLite), using lazy imports to avoid circular dependencies.

Routes:
    POST /sms - Handles incoming SMS messages from Twilio webhook
"""


from flask import Blueprint, request, jsonify
from datetime import datetime
from services.twilio_service import process_incoming_sms
from services import db_service
from utils.validators import validate_sms_payload

# Create the SMS Blueprint
# url_prefix is not set, so routes are registered at the root level
sms_bp = Blueprint('sms', __name__)


@sms_bp.route('/sms', methods=['POST'])
def sms_reply():
    """
    Handle incoming SMS messages from Twilio webhook.
    
    This route processes incoming SMS messages and stores them in the database.
    It works with both PostgreSQL (app.py) and SQLite (app_local.py) through
    lazy imports to avoid circular import issues.
    
    Expected POST parameters (from Twilio):
        From (str): Sender's phone number
        Body (str): Message content
    
    Returns:
        tuple: (message: str, status_code: int)
            - ("Reply recorded", 200) on success
            - ("Error processing message", 500) on failure
    """

    try:
        payload = {
            'From': request.form.get('From'),
            'Body': request.form.get('Body')
        }
        is_valid, errors = validate_sms_payload(payload)
        if not is_valid:
            return jsonify({'error': 'Invalid SMS payload', 'details': errors}), 400

        raw_phone_number = payload['From']
        reply = payload['Body']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Lazy import for environment-specific helpers
        try:
            from app import mask_phone_number, logger
        except Exception:
            from app_local import logger
            def mask_phone_number(phone_number):
                return phone_number

        # Use service layer for SMS processing
        success = process_incoming_sms(
            raw_phone_number, reply, timestamp,
            db_service, mask_phone_number, logger
        )
        if success:
            return "Reply recorded", 200
        else:
            return "Error processing message", 500
    except Exception as e:
        try:
            logger.error(f"Error in SMS handler: {e}")
        except Exception:
            pass
        return "Error processing message", 500
