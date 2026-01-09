# RentVerify Bot

**Automated rent payment verification via SMS — simple, fast, trackable.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Twilio](https://img.shields.io/badge/Twilio-SMS-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- 📱 **SMS-based verification** — Tenants reply YES/NO to confirm rent payments
- 💾 **SQLite database** — All responses stored with timestamps
- 📊 **Built-in dashboard** — View payment records at `/dashboard`
- 🔒 **Secure credentials** — Environment variables via `.env`
- ⚡ **Lightweight** — Flask-powered, easy to deploy

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core language |
| **Flask** | Web framework for webhook handling |
| **Twilio** | SMS API for sending/receiving messages |
| **SQLite** | Lightweight database for payment records |
| **python-dotenv** | Environment variable management |

---

## Project Structure

```
RentVerify/
├── 📄 app.py                      # Main Flask application
├── 📄 requirements.txt            # Python dependencies
├── 📄 Procfile                    # Production server command
├── 📄 runtime.txt                 # Python version (3.11.7)
├── 📁 templates/                  # HTML templates (login, dashboard)
├── 📁 static/                     # CSS, JS, images
├── 📁 instance/                   # Database storage (auto-created)
└── 📄 .env                        # Environment variables (not in Git)
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete file descriptions.

---

## How It Works

1. **Tenant receives SMS** — "Did you pay rent this month?"
2. **Tenant replies** — YES or NO
3. **Webhook processes response** — Flask receives POST request at `/sms`
4. **Database update** — Payment status saved with phone number and timestamp
5. **Automated reply** — Confirmation message sent back

```
YES  →  "Thank you! Payment verified."      →  Status: PAID
NO   →  "Alert: Non-payment recorded."       →  Status: NOT_PAID
Other → "Please reply with YES or NO."       →  No database entry
```

---

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/aminahamdani/rent-verify-bot.git
cd rent-verify-bot
```

### 2. Install dependencies
```bash
pip install flask twilio python-dotenv
```

### 3. Create `.env` file
Create a `.env` file in the root directory:
```env
TWILIO_ACCOUNT_SID="your_account_sid"
TWILIO_AUTH_TOKEN="your_auth_token"
```

### 4. Run the Flask app
```bash
python app.py
```
The app runs on `http://localhost:5000`

### 5. Expose webhook (for testing)
Use **ngrok** to expose your local server:
```bash
ngrok http 5000
```
Configure the ngrok URL in your Twilio console: `https://your-ngrok-url/sms`

---

## Sending a Test SMS

Use `send_test.py` to send a test message:

```bash
python send_test.py
```

Update the phone numbers in the script before running.

---

## Dashboard Overview

Visit `http://localhost:5000/dashboard` to view all payment records:

- **ID** — Unique record identifier
- **Phone Number** — Tenant's phone
- **Status** — PAID or NOT_PAID
- **Timestamp** — When the response was received

---

## Security Notes

🔐 **Never commit your `.env` file**

The `.gitignore` file ensures your API credentials stay local:
```
.env
```

All sensitive data (Twilio SID, Auth Token) is loaded from environment variables, not hardcoded.

---

## Dashboard Overview

Visit `/dashboard` to view all payment records:

| Feature | Description |
|---------|-------------|
| **View Records** | See all payment responses with timestamps |
| **Summary Stats** | Total PAID vs NOT_PAID counts |
| **Export CSV** | Download all records for analysis |
| **Secure Login** | Password-protected admin access |

**Dashboard URL:** `http://localhost:5000/dashboard` (local) or `https://your-app.onrender.com/dashboard` (production)

---

## 🚀 Production Deployment

### Quick Deploy (Render or Railway)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to https://render.com/
   - New Web Service → Connect GitHub repo
   - Build: `pip install -r requirements.txt`
   - Start: Uses `Procfile` automatically

3. **Set Environment Variables**
   ```env
   SECRET_KEY=your-64-char-secret-key
   FLASK_ENV=production
   ADMIN_USERNAME=your_username
   ADMIN_PASSWORD=your_password
   TWILIO_ACCOUNT_SID=ACxxxxx...
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

4. **Configure Twilio Webhook**
   - Webhook URL: `https://your-app.onrender.com/sms`
   - Method: POST

### Generate SECRET_KEY
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### Deployment Files

✅ **Procfile** (production server)
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
```

✅ **runtime.txt** (Python version)
```
python-3.11.7
```

✅ **requirements.txt** (dependencies)
```
Flask==3.0.0
twilio==8.10.0
python-dotenv==1.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
```

### Complete Deployment Guide
See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions.

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview and setup |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Complete deployment guide |
| [DEPLOYMENT_QUICK.md](DEPLOYMENT_QUICK.md) | Quick reference card |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | SMS testing instructions |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | File structure diagram |

---

## 🔒 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Session-based authentication
- ✅ Secure cookie configuration
- ✅ Environment variable protection
- ✅ SQL injection prevention (parameterized queries)
- ✅ HTTPS enforced in production

---

## Roadmap

- [x] Add tenant name field to database
- [x] Export payment records to CSV ✅
- [ ] Email notifications for non-payments
- [ ] Multi-tenant support with unique links
- [x] Deploy to Heroku/Railway/Render ✅

---

## 💰 Costs

**Free Tier Options:**
- Render: 750 hours/month free (sleeps after 15 min)
- Railway: $5 free credit/month
- Twilio: Free trial + ~$0.0075/SMS

**Total:** $0-20/month depending on usage

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 Support

- **Issues:** Open a GitHub issue
- **Twilio Docs:** https://www.twilio.com/docs/sms
- **Flask Docs:** https://flask.palletsprojects.com/

---

## License

MIT (placeholder — update as needed)

---

**Built with ❤️ for landlords who value automation**

---

## 🌐 Live Demo
Try the app here: https://rent-verify-bot.onrender.com

### 📱 Scan to Open
![QR Code](assets/qr_rent-verify-bot.png)
