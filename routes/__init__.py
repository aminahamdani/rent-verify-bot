"""
Routes Package - Flask Blueprints for RentVerify

This package contains all the Flask blueprints for the RentVerify application.

Blueprints:
    sms_bp: SMS webhook handler for Twilio integration
"""

from routes.sms import sms_bp

__all__ = ['sms_bp']
