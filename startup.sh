#!/bin/bash
# Azure App Service startup script for RentVerify Flask app

# Install dependencies if needed
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run the Flask app with Gunicorn
# Azure App Service sets PORT automatically
gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 60 --log-level info
