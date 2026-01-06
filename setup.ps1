# Quick Setup Script for RentVerify Testing (PowerShell)
# Run this after cloning the repository

Write-Host "🚀 RentVerify - Quick Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "📋 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env with your actual credentials:" -ForegroundColor Red
    Write-Host "   - TWILIO_ACCOUNT_SID"
    Write-Host "   - TWILIO_AUTH_TOKEN"
    Write-Host "   - TWILIO_PHONE_NUMBER"
    Write-Host "   - TEST_RECIPIENT_PHONE"
    Write-Host "   - SECRET_KEY"
    Write-Host "   - ADMIN_USERNAME"
    Write-Host "   - ADMIN_PASSWORD"
    Write-Host ""
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env with your credentials" -ForegroundColor White
Write-Host "2. Run: python send_test.py (to test Twilio)" -ForegroundColor White
Write-Host "3. Run: python app.py (to start the server)" -ForegroundColor White
Write-Host ""
