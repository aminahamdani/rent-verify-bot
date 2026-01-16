# 🚀 Quick Azure Deployment Guide

## One-Minute Setup

### 1. Create App Service
```
Azure Portal → Create a resource → Web App
- Name: rentverify-app
- Runtime: Python 3.11
- OS: Linux
- Plan: Free (F1)
```

### 2. Connect GitHub
```
App Service → Deployment Center → GitHub
- Repository: aminahamdani/rent-verify-bot
- Branch: main
```

### 3. Add Environment Variables
```
App Service → Configuration → Application settings
Add:
- SECRET_KEY
- FLASK_ENV=production
- ADMIN_USERNAME
- ADMIN_PASSWORD
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
- DATABASE_URL
```

### 4. Set Startup Command
```
Configuration → General settings → Startup Command
gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --timeout 60 --log-level info
```

### 5. Done! 🎉
Visit: `https://rentverify-app.azurewebsites.net`

---

## Environment Variables Template

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
ADMIN_USERNAME=amina
ADMIN_PASSWORD=0000
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
DATABASE_URL=postgresql://user:pass@host/db
PORT=8000
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| App won't start | Check startup command format |
| 502 Error | Restart app service |
| DB connection fails | Verify DATABASE_URL |
| Env vars not working | Restart after adding |

---

**Full Guide:** See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
