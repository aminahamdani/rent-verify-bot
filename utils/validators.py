"""
Input Validators for RentVerify
"""
import re

# --- SMS Payload Validator ---
def validate_sms_payload(payload):
    """
    Validate incoming SMS payload from Twilio webhook.
    Args:
        payload (dict): Should contain 'From' and 'Body' keys.
    Returns:
        (bool, dict): (is_valid, errors)
    """
    errors = {}
    if 'From' not in payload or not isinstance(payload['From'], str) or not re.match(r'^\+?\d{10,15}$', payload['From']):
        errors['From'] = 'Invalid or missing phone number.'
    if 'Body' not in payload or not isinstance(payload['Body'], str) or not payload['Body'].strip():
        errors['Body'] = 'Message body is required.'
    return (len(errors) == 0, errors)

# --- Dashboard Form Validator ---
def validate_dashboard_form(form):
    """
    Validate dashboard form input (example: login form).
    Args:
        form (dict): Should contain 'username' and 'password' keys.
    Returns:
        (bool, dict): (is_valid, errors)
    """
    errors = {}
    if 'username' not in form or not isinstance(form['username'], str) or not form['username'].strip():
        errors['username'] = 'Username is required.'
    if 'password' not in form or not isinstance(form['password'], str) or not form['password'].strip():
        errors['password'] = 'Password is required.'
    return (len(errors) == 0, errors)
