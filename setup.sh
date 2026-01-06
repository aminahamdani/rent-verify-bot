#!/bin/bash
# Quick Setup Script for RentVerify Testing
# Run this after cloning the repository

echo "🚀 RentVerify - Quick Setup"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your actual credentials:"
    echo "   - TWILIO_ACCOUNT_SID"
    echo "   - TWILIO_AUTH_TOKEN"
    echo "   - TWILIO_PHONE_NUMBER"
    echo "   - TEST_RECIPIENT_PHONE"
    echo "   - SECRET_KEY"
    echo "   - ADMIN_USERNAME"
    echo "   - ADMIN_PASSWORD"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Run: python send_test.py (to test Twilio)"
echo "3. Run: python app.py (to start the server)"
echo ""
