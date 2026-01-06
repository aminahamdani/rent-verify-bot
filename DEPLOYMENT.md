# 🚀 RentVerify - Production Deployment Guide

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:
- ✅ Twilio account with verified phone number
- ✅ GitHub repository (or Git repo)
- ✅ Render or Railway account
- ✅ Admin credentials chosen
- ✅ SECRET_KEY generated

---

## 🔧 DEPLOYMENT PREPARATION

### ✅ Your app.py is already production-ready!

**What was already fixed:**
- ✅ Logging to stdout (not file) - Render/Railway compatible
- ✅ PORT environment variable support
- ✅ Debug mode disabled in production
- ✅ Proper database connection management
- ✅ Session security configured
- ✅ Password hashing implemented
- ✅ All environment variables validated

**No changes needed to app.py!**

---

## 🌍 ENVIRONMENT VARIABLES

### **Required on Hosting Platform Dashboard:**

Copy these to Render/Railway environment variables section:

```env
# Flask Configuration
SECRET_KEY=generate-a-secure-random-64-char-string-here
FLASK_ENV=production

# Admin Credentials
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password_here

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Optional: PORT is usually auto-set by platform
# PORT=10000
```

### **How to Generate SECRET_KEY:**

**Windows PowerShell:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Example output:** `a3f5b2c8d9e1f0a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0`

---

## 📦 DEPLOYMENT FILES

### ✅ Files Created:

1. **Procfile** - Tells platform how to run your app
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
   ```

2. **runtime.txt** - Specifies Python version
   ```
   python-3.11.7
   ```

3. **requirements.txt** - Already correct!
   ```
   Flask==3.0.0
   twilio==8.10.0
   python-dotenv==1.0.0
   gunicorn==21.2.0
   Werkzeug==3.0.1
   ```

---

## 🚀 DEPLOYMENT STEPS

### **Option A: Deploy to Render**

#### Step 1: Create New Web Service
1. Go to https://render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select **RentVerify** repository

#### Step 2: Configure Build Settings
```
Name: rentverify-app
Environment: Python
Region: Oregon (US West) or closest to you
Branch: main (or master)

Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

#### Step 3: Set Environment Variables
Click **"Environment"** tab and add:
```
SECRET_KEY = [your-64-char-secret]
FLASK_ENV = production
ADMIN_USERNAME = [your-username]
ADMIN_PASSWORD = [your-password]
TWILIO_ACCOUNT_SID = [your-twilio-sid]
TWILIO_AUTH_TOKEN = [your-twilio-token]
TWILIO_PHONE_NUMBER = [your-twilio-number]
```

#### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. Your app will be at: `https://rentverify-app.onrender.com`

---

### **Option B: Deploy to Railway**

#### Step 1: Create New Project
1. Go to https://railway.app/
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **RentVerify** repository

#### Step 2: Configure Settings
Railway auto-detects Python and uses Procfile automatically.

#### Step 3: Set Environment Variables
Click **"Variables"** tab and add:
```
SECRET_KEY = [your-64-char-secret]
FLASK_ENV = production
ADMIN_USERNAME = [your-username]
ADMIN_PASSWORD = [your-password]
TWILIO_ACCOUNT_SID = [your-twilio-sid]
TWILIO_AUTH_TOKEN = [your-twilio-token]
TWILIO_PHONE_NUMBER = [your-twilio-number]
```

#### Step 4: Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Click **"Settings"** → **"Generate Domain"**
4. Your app will be at: `https://rentverify-app.up.railway.app`

---

## 📱 TWILIO WEBHOOK CONFIGURATION

### **Critical: Configure Webhook URL After Deployment**

#### Step 1: Get Your Deployed URL
- **Render:** `https://your-app-name.onrender.com`
- **Railway:** `https://your-app-name.up.railway.app`

#### Step 2: Configure Twilio Webhook
1. Go to https://console.twilio.com/
2. Navigate to **Phone Numbers** → **Manage** → **Active Numbers**
3. Click your phone number
4. Scroll to **Messaging Configuration**
5. Under **"A MESSAGE COMES IN"**:
   ```
   Webhook: https://your-app-name.onrender.com/sms
   HTTP Method: POST
   ```
6. Click **"Save"**

#### Step 3: Test the Webhook
1. Send an SMS to your Twilio number: **"YES"**
2. You should receive: **"Thank you! Payment verified."**
3. Send: **"NO"**
4. You should receive: **"Alert: Non-payment recorded."**

---

## 🔍 VERIFY DEPLOYMENT

### **1. Check App is Running**
Visit your deployed URL:
```
https://your-app-name.onrender.com/login
```

You should see the login page.

### **2. Test Login**
- Username: Your ADMIN_USERNAME
- Password: Your ADMIN_PASSWORD

### **3. Test SMS Webhook**
Send "YES" to your Twilio number and check:
- SMS response received
- Dashboard shows new record

### **4. Check Logs**
**Render:** Click "Logs" tab
**Railway:** Click "Deployments" → View logs

Look for:
```
Application started
Database initialized successfully
```

---

## 🐛 TROUBLESHOOTING

### **Problem: "Application failed to start"**
**Solution:** Check environment variables are set correctly

### **Problem: "SECRET_KEY not found"**
**Solution:** Add SECRET_KEY to environment variables on hosting dashboard

### **Problem: "Database error"**
**Solution:** 
- Render: Check instance folder is writable
- Railway: Database auto-created in /app/instance/

### **Problem: "Twilio webhook not working"**
**Solution:**
1. Verify webhook URL: `https://your-domain.com/sms` (no trailing slash)
2. Check HTTP method is POST
3. View Twilio debugger: https://console.twilio.com/debugger
4. Check app logs for incoming requests

### **Problem: "502 Bad Gateway"**
**Solution:**
- Wait 2-3 minutes for cold start
- Check logs for errors
- Verify Procfile is correct

### **Problem: "Can't login"**
**Solution:**
- Verify ADMIN_USERNAME and ADMIN_PASSWORD match in:
  - Environment variables on hosting platform
  - Login form inputs (check for extra spaces)

---

## 📊 MONITORING

### **Check Application Health:**
```
https://your-app-name.onrender.com/
```
Should redirect to login page.

### **Monitor Logs:**
- **Render:** Dashboard → Logs tab
- **Railway:** Dashboard → Deployments → Logs

### **Check Twilio Activity:**
https://console.twilio.com/monitor/logs/sms

---

## 🔒 SECURITY CHECKLIST

- ✅ SECRET_KEY is 64+ characters
- ✅ ADMIN_PASSWORD is strong (12+ chars)
- ✅ `.env` file is in `.gitignore`
- ✅ No hardcoded secrets in code
- ✅ HTTPS enabled (automatic on Render/Railway)
- ✅ Session cookies secure in production
- ✅ Twilio webhook uses HTTPS

---

## 🎯 POST-DEPLOYMENT TASKS

1. **✅ Save your deployed URL**
   - Add to README.md
   - Bookmark in browser

2. **✅ Test all features**
   - Login/logout
   - SMS webhook (YES/NO)
   - Dashboard display
   - CSV export

3. **✅ Configure custom domain** (Optional)
   - Render: Settings → Custom Domains
   - Railway: Settings → Domains

4. **✅ Set up monitoring**
   - Enable email notifications for crashes
   - Monitor Twilio usage/costs

5. **✅ Backup considerations**
   - Export database periodically via CSV
   - Consider external database for production scale

---

## 💰 COST ESTIMATES

### **Render Free Tier:**
- ✅ Web service (sleeps after 15 min inactivity)
- ✅ 750 hours/month free
- ⚠️ Cold starts (15-30 seconds)

### **Railway Free Trial:**
- ✅ $5 free credit/month
- ✅ No sleep time
- ⚠️ Upgrade needed after trial

### **Twilio Costs:**
- ✅ Free trial credit
- SMS: ~$0.0075 per message (US)
- Phone number: $1-2/month

---

## 📞 SUPPORT RESOURCES

- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app/
- **Twilio Docs:** https://www.twilio.com/docs/sms
- **Flask Deployment:** https://flask.palletsprojects.com/en/3.0.x/deploying/

---

## ✅ DEPLOYMENT COMPLETE!

Your RentVerify app is now live and ready to handle SMS webhooks! 🎉

**Next steps:**
1. Test SMS functionality
2. Monitor logs for issues
3. Share dashboard URL with stakeholders
4. Set up regular database exports

---

**Remember:** Your app URL will be:
- **Render:** `https://[your-service-name].onrender.com`
- **Railway:** `https://[your-service-name].up.railway.app`

**Twilio Webhook:** `https://[your-domain]/sms`
