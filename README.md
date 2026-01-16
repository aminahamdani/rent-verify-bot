# RentVerify Bot

**Automated rent payment verification via SMS — simple, fast, trackable.**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Twilio](https://img.shields.io/badge/Twilio-SMS-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- 📱 **SMS-based verification** — Tenants reply YES/NO to confirm rent payments
- 💾 **PostgreSQL database** — Production-ready with connection pooling
- 📊 **Secure admin dashboard** — Password-protected web interface
- 🔒 **Phone number masking** — Privacy protection with masked display (******9380)
- 📥 **CSV export** — Download all records with timestamps
- 🔐 **Full authentication** — Login/logout with secure sessions
- ⚡ **Production-ready** — Deployed on Render with gunicorn

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core language |
| **Flask** | Web framework for webhook handling |
| **PostgreSQL** | Production database with connection pooling |
| **Twilio** | SMS API for sending/receiving messages |
| **Gunicorn** | Production WSGI server |
| **python-dotenv** | Environment variable management |
| **Werkzeug** | Password hashing and security |
| **psycopg2** | PostgreSQL adapter |

---

## Project Structure (2026)

The project now uses modular blueprints, a service layer, centralized error handling, and explicit input validation contracts.

See [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) for a step-by-step development history.

```
RentVerify/
├── 📄 app.py                      # Application factory, blueprint registration
├── 📄 app_local.py                # Local development entry point
├── 📄 requirements.txt            # Python dependencies
├── 📄 Procfile                    # Production server (gunicorn)
├── 📄 runtime.txt                 # Python version (3.11.7)
├── 📄 alembic.ini                 # Database migration config
├── 📁 alembic/                    # Database migrations
│   ├── env.py
│   └── versions/
│       └── 001_initial_migration.py
├── 📁 templates/                  # HTML templates
│   ├── login.html                 # Admin login page
│   └── dashboard.html             # Main dashboard with masking
├── 📁 static/                     # CSS stylesheets
│   ├── login.css
│   ├── dashboard.css
│   └── styles.css
├── 📁 routes/                     # Modular route blueprints
│   ├── sms.py                    # SMS webhook blueprint (input validation)
│   ├── dashboard.py              # Dashboard blueprint (input validation)
│   └── __init__.py               # Route package initializer
├── 📁 services/                  # Business logic layer
│   ├── twilio_service.py         # SMS processing logic
│   └── db_service.py             # DB connection logic
├── 📁 utils/                     # Utilities
│   ├── error_handlers.py         # Centralized error handling
│   └── validators.py             # Input validation contracts
└── 📄 .env                        # Environment variables (not in Git)
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete file descriptions.
See [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) for a chronological log of development steps.

---

## How It Works

### SMS Flow
1. **Tenant receives SMS** — "Did you pay rent this month?"
2. **Tenant replies** — YES or NO via text message
3. **Webhook processes response** — Flask receives POST at `/sms`
4. **Phone masking** — Number masked to ******9380 format for privacy
5. **Database update** — Masked number, reply, and timestamp saved
6. **Admin dashboard** — View all responses in real-time

### Privacy Protection
All phone numbers are automatically masked:
- **Incoming**: `+1234567890` → **Stored/Displayed**: `******7890`
- Database stores only masked versions
- Dashboard displays masked numbers
- CSV exports include masked numbers only

### Response Handling
```
YES  →  Saved with YES status      →  Dashboard: YES badge (green)
NO   →  Saved with NO status        →  Dashboard: NO badge (red)
Other → Saved as Pending             →  Dashboard: Pending badge (yellow)
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL installed locally OR use remote PostgreSQL (Render, Neon, etc.)

### 1. Clone the repository
```bash
git clone https://github.com/aminahamdani/rent-verify-bot.git
cd rent-verify-bot
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rentverify

# Security
SECRET_KEY=your-64-char-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxx...
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Flask
FLASK_ENV=development
PORT=5000
```

### 5. Initialize database
```bash
python create_tables.py
```

### 6. Run the Flask app
```bash
python app.py
```
The app runs on `http://localhost:5000`

### 7. Expose webhook (for testing)
Use **ngrok** to expose your local server:
```bash
ngrok http 5000
```
Configure the ngrok URL in your Twilio console: `https://your-ngrok-url/sms`

### 8. Access dashboard
- Navigate to `http://localhost:5000/dashboard`
- Login with your `ADMIN_USERNAME` and `ADMIN_PASSWORD`

---

## Sending a Test SMS

Use `send_test.py` to send a test message:

```bash
python send_test.py
```

Update the phone numbers in the script before running.

---

## Dashboard Overview

Visit `/dashboard` to view and manage payment records:

### Features
| Feature | Description |
|---------|-------------|
| **Secure Login** | Password-protected admin access with session management |
| **Real-time Stats** | Total messages, YES/NO counts, Pending count |
| **Message Table** | View all responses with masked phone numbers |
| **Phone Masking** | Privacy protection - only last 4 digits shown (******9380) |
| **Auto-refresh** | Dashboard refreshes every 30 seconds |
| **CSV Export** | Download all records with masked numbers |
| **Flash Messages** | Success/error notifications |
| **Responsive Design** | Mobile-friendly Bootstrap UI |

### Dashboard Stats Cards
- **Total Messages**: Total SMS responses received
- **YES**: Count of confirmed payments
- **NO**: Count of non-payments
- **Pending**: Other responses or unclear replies

### Access
- **Local**: `http://localhost:5000/dashboard`
- **Production**: `https://your-app.onrender.com/dashboard`

### Security
- Session-based authentication
- Secure cookie configuration
- Password hashing with Werkzeug
- Auto-logout after 1 hour of inactivity

---

## 🚀 Production Deployment

### Quick Deploy on Render

1. **Create PostgreSQL Database**
   - Go to Render Dashboard → New → PostgreSQL
   - Copy the Internal Database URL

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Deploy Web Service**
   - Go to https://render.com/ → New → Web Service
   - Connect your GitHub repository
   - Build: `pip install -r requirements.txt`
   - Start: Uses `Procfile` automatically

4. **Set Environment Variables**
   Add these in Render Dashboard → Environment:
   ```env
   DATABASE_URL=<your-postgres-internal-url>
   SECRET_KEY=<64-char-random-string>
   FLASK_ENV=production
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<strong-password>
   TWILIO_ACCOUNT_SID=ACxxxxx...
   TWILIO_AUTH_TOKEN=<your-token>
   TWILIO_PHONE_NUMBER=+1234567890
   PORT=10000
   ```

5. **Run Migrations**
   - In Render Dashboard → Shell:
   ```bash
   python create_tables.py
   ```

6. **Configure Twilio Webhook**
   - Twilio Console → Phone Numbers → Your Number
   - Webhook URL: `https://your-app.onrender.com/sms`
   - Method: POST
   - Save

### Generate SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Deployment Files Included

✅ **Procfile** (gunicorn configuration)
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
```

✅ **runtime.txt** (Python version)
```
python-3.11.7
```

✅ **requirements.txt** (all dependencies)
```
Flask==3.0.0
twilio==8.10.0
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
Werkzeug==3.0.1
```

### Database Migrations
Using Alembic for schema management:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions.

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview and setup (you are here) |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Complete production deployment guide |
| [DEPLOYMENT_QUICK.md](DEPLOYMENT_QUICK.md) | Quick reference for deployment |
| [LOCAL_SETUP.md](LOCAL_SETUP.md) | Detailed local development setup |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | SMS testing and webhook validation |
| [MIGRATIONS.md](MIGRATIONS.md) | Database migration instructions |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Complete file structure reference |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) | Chronological log of development steps |

---

## 🔒 Security Features

### Authentication & Authorization
- ✅ Password hashing with Werkzeug (bcrypt-based)
- ✅ Session-based authentication with secure cookies
- ✅ Login/logout functionality
- ✅ Session timeout (1 hour inactivity)
- ✅ Flash message notifications

### Data Protection
- ✅ **Phone number masking** - Only last 4 digits displayed (******9380)
- ✅ Masked storage in database
- ✅ Masked display in dashboard
- ✅ Masked exports in CSV files
- ✅ No real phone numbers in logs

### Application Security
- ✅ Environment variable protection
- ✅ SQL injection prevention (parameterized queries)
- ✅ Database connection pooling
- ✅ HTTPS enforced in production
- ✅ Secure cookie configuration (HTTPOnly, SameSite)

### Best Practices
🔐 **Never commit your `.env` file**

The `.gitignore` ensures your API credentials stay local:
```
.env
instance/
__pycache__/
*.pyc
```

All sensitive data loaded from environment variables, not hardcoded.

---

## Roadmap

- [x] PostgreSQL database integration ✅
- [x] Admin authentication system ✅
- [x] Export payment records to CSV ✅
- [x] Phone number masking for privacy ✅
- [x] Template-level masking ✅
- [x] Deploy to Render ✅
- [x] Connection pooling ✅
- [x] Flash message notifications ✅
- [ ] Email notifications for non-payments
- [ ] Multi-tenant support
- [ ] SMS reminder scheduling
- [ ] Analytics dashboard

---

## 💰 Costs

**Free Tier Options:**
- **Render**: Free PostgreSQL (90 days) + Web Service (750 hrs/month)
- **Neon**: Free PostgreSQL (500 MB storage)
- **Twilio**: Free trial + ~$0.0075/SMS after

**Estimated Monthly Cost:** $0-15 depending on usage

**Production Setup:**
- Render PostgreSQL: $7/month
- Render Web Service: Free tier sufficient for most use cases
- Twilio: Pay-as-you-go (~$0.0075 per SMS)

---

## 🛠️ Utility Scripts

| Script | Purpose |
|--------|---------|
| `app.py` | Main Flask application |
| `app_local.py` | Local development with SQLite |
| `create_tables.py` | Initialize PostgreSQL tables |
| `check_db.py` | Verify database connection |
| `send_test.py` | Send test SMS via Twilio |
| `test_webhook.py` | Test webhook locally |
| `verify_deployment.py` | Check production deployment |
| `generate_qr.py` | Generate QR code for app URL |

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Support

- **Issues**: [Open a GitHub issue](https://github.com/aminahamdani/rent-verify-bot/issues)
- **Twilio Docs**: https://www.twilio.com/docs/sms
- **Flask Docs**: https://flask.palletsprojects.com/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## License

MIT License - See [LICENSE](LICENSE) for details

---

**Built with ❤️ for landlords who value automation and privacy**

---

## 🌐 Live Demo

Try the app: https://rent-verify-bot.onrender.com

**Admin Dashboard**: Login with credentials to view masked phone records

### 📱 Scan to Open
![QR Code](assets/qr_rent-verify-bot.png)

---

## Tech Highlights

- 🔐 **Security First**: Password hashing, session management, phone masking
- 📊 **Real-time Dashboard**: Auto-refresh, responsive design
- 💾 **Production Database**: PostgreSQL with connection pooling
- 🎨 **Modern UI**: Bootstrap-based, mobile-friendly
- 📥 **Data Export**: CSV download with masked data
- 🚀 **Cloud Ready**: Deployed on Render with gunicorn
