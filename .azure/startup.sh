#!/bin/bash
# Azure App Service startup script for RentVerify Flask app
# This script is used by Azure App Service to start the application

# Azure automatically sets the PORT environment variable
# Use PORT if available, otherwise default to 8000
PORT=${PORT:-8000}

# Start Gunicorn with the Flask app
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
