# 🚀 RENDER DEPLOYMENT - READY TO GO!

## Your Deployment is 100% Ready! Just Follow These Steps:

### Step 1: Open Render and Create Web Service
**I'll open Render for you - just click the link below:**

👉 **[CLICK HERE TO GO TO RENDER](https://dashboard.render.com/)**

Then:
1. Click **"New +"** → **"Web Service"**
2. Connect to GitHub repository: `aminahamdani/rent-verify-bot`
3. Click **"Connect"**

---

### Step 2: Basic Configuration

Copy and paste these settings:

```
Name: rentverify-app
Environment: Python 3
Region: Oregon (or closest to you)
Branch: main

Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

---

### Step 3: Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these **EXACT VALUES**:

```
SECRET_KEY
8ecf4b0387239d9941b8871a4374dde452bd77fb62bf78053a62cf3e18bae2b8

FLASK_ENV
production

ADMIN_USERNAME
amina

ADMIN_PASSWORD
0000

TWILIO_ACCOUNT_SID
AC17efd4d5f4a68b402abba142a1258343

TWILIO_AUTH_TOKEN
0aa93cf55621f111b0c7aa0fdb970d02

TWILIO_PHONE_NUMBER
+16802082305

DATABASE_URL
postgresql://neondb_owner:npg_VCl41aLdkqJN@ep-divine-smoke-ahao7irw-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**IMPORTANT:** Copy each variable name and value exactly as shown above!

---

### Step 4: Deploy!
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. Once deployed, Render will show your URL (e.g., `https://rentverify-app.onrender.com`)
4. **COPY YOUR URL!** You'll need it for Twilio.

---

### Step 5: Configure Twilio Webhook

**I'll open Twilio for you:**

👉 **[CLICK HERE TO GO TO TWILIO](https://console.twilio.com/us1/develop/phone-numbers/manage/active)**

Then:
1. Click your phone number: **+16802082305**
2. Scroll to **"Messaging Configuration"**
3. Under **"A MESSAGE COMES IN"**:
   - Webhook: `https://YOUR-APP-NAME.onrender.com/sms` (use YOUR deployed URL + /sms)
   - HTTP Method: **POST**
4. Click **"Save"**

---

### Step 6: Test Your App! 🎉

1. Visit your deployed URL: `https://your-app-name.onrender.com/login`
2. Login with:
   - Username: **amina**
   - Password: **0000**
3. Send SMS to **+16802082305** with "YES" or "NO"
4. Check dashboard - message should appear!

---

## 📋 Quick Checklist

- [ ] Go to Render (link above)
- [ ] Create new Web Service from GitHub repo
- [ ] Set Build/Start commands
- [ ] Add all 8 environment variables
- [ ] Deploy and wait for completion
- [ ] Copy your deployed URL
- [ ] Configure Twilio webhook with your URL
- [ ] Test login
- [ ] Send test SMS
- [ ] Verify message appears in dashboard

---

## ⚠️ Important Notes

- **Free Tier:** App sleeps after 15 min inactivity (wakes in ~30 sec on first request)
- **Database:** You're already using Neon PostgreSQL (included in your DATABASE_URL)
- **Always On:** Upgrade to paid tier ($7/mo) if you need 24/7 uptime

---

## 🆘 Need Help?

If deployment fails, check:
1. All environment variables are added correctly
2. No typos in variable names or values
3. Render logs (click "Logs" tab in Render dashboard)
4. Your GitHub repo is up to date (already done ✓)

---

**Everything is ready! Just follow the steps above. It will take about 5 minutes total.**
