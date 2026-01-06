# 📱 RentVerify - Twilio SMS Testing Guide

## 🔍 Overview
This guide explains how to safely test Twilio SMS functionality before deploying your RentVerify application.

---

## ✅ What Was Fixed in send_test.py

### Issues Found and Fixed:
1. ✅ **Hardcoded phone numbers** → Now uses environment variables
2. ✅ **No error handling** → Comprehensive try-catch blocks added
3. ✅ **No validation** → Validates all required variables before running
4. ✅ **Poor feedback** → Detailed success/error messages
5. ✅ **Deployment risk** → Added to .gitignore
6. ✅ **No documentation** → Full docstrings and comments

---

## 🚀 How to Run Safely

### Step 1: Set Up Environment Variables

1. Copy the example file:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```env
   # Twilio credentials (from https://console.twilio.com/)
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_actual_token_here
   TWILIO_PHONE_NUMBER=+16802082305
   TEST_RECIPIENT_PHONE=+16464089380
   ```

### Step 2: Install Dependencies

```powershell
pip install twilio python-dotenv
```

### Step 3: Run the Test Script

```powershell
python send_test.py
```

### Expected Output:

#### ✅ Success:
```
✓ Loaded .env from: C:\...\RentVerify\.env
✓ All environment variables loaded successfully

==================================================
TWILIO SMS TEST
==================================================
From: +16802082305
To: +16464089380
--------------------------------------------------
✓ Twilio client initialized
✓ Message sent successfully!

Message Details:
  - SID: SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  - Status: queued
  - Direction: outbound-api
  - Date Created: 2026-01-06 12:34:56+00:00
==================================================

✅ TEST PASSED: Check your phone for the message!
```

#### ❌ Failure (Missing .env):
```
❌ ERROR: .env file not found at: C:\...\RentVerify\.env
Please create a .env file with your Twilio credentials.
```

#### ❌ Failure (Invalid Credentials):
```
❌ TWILIO API ERROR:
   Error Code: 20003
   Error Message: Authentication Error - No credentials
   Status: 401

Common issues:
  - Invalid phone number format (use E.164: +1234567890)
  - Twilio account not verified
  - Insufficient Twilio credits
  - Invalid credentials
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Store sensitive data in `.env` file
- Keep `.env` in `.gitignore`
- Use `.env.example` as a template (without real values)
- Test locally before deploying
- Use environment variables for phone numbers

### ❌ DON'T:
- Commit `.env` to Git/GitHub
- Hardcode phone numbers in code
- Share your Twilio credentials
- Deploy `send_test.py` to production
- Use test scripts in production environment

---

## 📋 Checklist Before Deployment

- [ ] `.env` file exists locally with correct credentials
- [ ] `.env` is in `.gitignore`
- [ ] `send_test.py` is in `.gitignore`
- [ ] Test SMS sent successfully
- [ ] Phone numbers in E.164 format (+1234567890)
- [ ] Twilio webhook URL configured
- [ ] Environment variables set on Render/Railway
- [ ] No hardcoded secrets in code

---

## 🐛 Troubleshooting

### Problem: "Authentication Error"
**Solution:** Check your TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in `.env`

### Problem: "Invalid 'To' Phone Number"
**Solution:** Ensure phone number is in E.164 format: `+1234567890` (no spaces/dashes)

### Problem: "Message Not Received"
**Solution:** 
1. Check Twilio trial account verification
2. Verify recipient phone is verified in Twilio console
3. Check Twilio logs at https://console.twilio.com/

### Problem: ".env file not found"
**Solution:** 
1. Ensure `.env` exists in project root
2. Copy from `.env.example`: `Copy-Item .env.example .env`
3. Fill in your actual credentials

---

## 🌐 Local vs. Deployed Testing

### Local Testing (send_test.py):
- Use for development only
- Tests Twilio credentials
- Sends test messages manually
- NOT deployed to Render/Railway

### Production Testing (app.py):
- Real webhook integration
- Automated SMS responses
- Deployed to Render/Railway
- Uses environment variables from hosting platform

---

## 📞 Twilio Phone Number Format

Always use E.164 format:
```
✅ Correct: +16802082305
❌ Wrong:   6802082305
❌ Wrong:   (680) 208-2305
❌ Wrong:   +1 680-208-2305
```

---

## 🎯 Next Steps After Testing

1. **Verify test SMS received** → Check your phone
2. **Configure Twilio webhook** → Point to your deployed URL
3. **Set production environment variables** → On Render/Railway dashboard
4. **Deploy app.py** → Push to Render/Railway
5. **Test webhook** → Send "YES" or "NO" to Twilio number

---

## 💡 Tips

- **Test locally first** before deploying
- **Keep send_test.py** for troubleshooting (but don't deploy it)
- **Monitor Twilio logs** to debug issues
- **Check Twilio trial limits** if messages fail
- **Verify phone numbers** in Twilio console for trial accounts

---

## 📧 Support

If issues persist:
1. Check Twilio status: https://status.twilio.com/
2. Review Twilio logs: https://console.twilio.com/
3. Verify account balance/credits
4. Check phone number verification status

---

**Remember:** `send_test.py` is for LOCAL TESTING ONLY. It should NEVER be deployed to production!
