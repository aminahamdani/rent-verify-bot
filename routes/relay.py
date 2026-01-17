"""
Relay Blueprint - Forwards SMS webhooks to multiple endpoints
This allows sending the same SMS to both Azure and Render (or other platforms)
"""

from flask import Blueprint, request
import requests
import logging

relay_bp = Blueprint('relay', __name__)
logger = logging.getLogger(__name__)


@relay_bp.route('/sms-relay', methods=['POST'])
def sms_relay():
    """
    Relay SMS webhook to multiple endpoints.
    Receives from Twilio and forwards to both Azure and Render.
    """
    try:
        # Get the payload from Twilio
        payload = dict(request.form)
        
        # List of endpoints to forward to
        endpoints = []
        
        # Azure endpoint (your current Azure URL)
        azure_url = 'https://rentverify-app-fbbbazaagbd8e0hn.canadacentral-01.azurewebsites.net/sms'
        endpoints.append(('Azure', azure_url))
        
        # Render endpoint (if you have one)
        render_url = 'https://rent-verify-bot.onrender.com/sms'
        endpoints.append(('Render', render_url))
        
        results = []
        
        # Forward to each endpoint
        for name, url in endpoints:
            try:
                response = requests.post(url, data=payload, timeout=10)
                if response.status_code == 200:
                    results.append(f"{name}: Success")
                    logger.info(f"Successfully forwarded to {name}: {url}")
                else:
                    results.append(f"{name}: Error {response.status_code}")
                    logger.warning(f"Failed to forward to {name}: {response.status_code}")
            except Exception as e:
                results.append(f"{name}: Error - {str(e)}")
                logger.error(f"Error forwarding to {name}: {e}")
        
        # Return success if at least one worked
        if any("Success" in r for r in results):
            return f"Relayed to: {', '.join(results)}", 200
        else:
            return f"All relays failed: {', '.join(results)}", 500
            
    except Exception as e:
        logger.error(f"Error in relay: {e}")
        return "Error processing relay", 500

