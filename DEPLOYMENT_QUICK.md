# 🚀 RentVerify - Quick Deployment Reference

## ✅ Pre-Deployment Checklist

```
□ app.py - Production ready ✓
□ requirements.txt - Complete ✓
□ Procfile - Created ✓
□ runtime.txt - Created ✓
□ .gitignore - Configured ✓
□ Environment variables prepared
□ Twilio account active
□ GitHub repo created
□ Hosting account (Render/Railway)
```

---

## 📋 Required Environment Variables

Copy these to your hosting dashboard:

```env
SECRET_KEY=your-64-char-secret-key-here
FLASK_ENV=production
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

### Generate SECRET_KEY:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🌐 Deployment Commands

### **Render:**
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

### **Railway:**
```
Uses Procfile automatically (no commands needed)
```

---

## 📱 Twilio Webhook Setup

**After deployment, configure webhook:**

1. **Get your URL:** `https://your-app.onrender.com`
2. **Go to:** https://console.twilio.com/
3. **Navigate:** Phone Numbers → Active Numbers → Your Number
4. **Set webhook:**
   ```
   URL: https://your-app.onrender.com/sms
   Method: POST
   ```
5. **Save**

---

## 🧪 Test Deployment

1. **Visit:** `https://your-app.onrender.com/login`
2. **Login** with your credentials
3. **Send SMS** "YES" to your Twilio number
4. **Check dashboard** for new record
5. **Export CSV** to verify data

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| 502 Error | Wait 2-3 min for cold start |
| Can't login | Check ADMIN credentials match exactly |
| SMS not working | Verify webhook URL (no trailing /) |
| SECRET_KEY error | Add to environment variables |
| Database error | Check logs for permission issues |

---

## 📊 Your URLs

**Main App:**
- Render: `https://[service-name].onrender.com`
- Railway: `https://[service-name].up.railway.app`

**Login:** `/login`
**Dashboard:** `/dashboard`
**CSV Export:** `/export`
**Twilio Webhook:** `/sms`

---

## ⚡ Quick Links

- **Render Dashboard:** https://dashboard.render.com/
- **Railway Dashboard:** https://railway.app/dashboard
- **Twilio Console:** https://console.twilio.com/
- **Twilio Debugger:** https://console.twilio.com/debugger

---

**Status:** 🟢 Ready to Deploy!
