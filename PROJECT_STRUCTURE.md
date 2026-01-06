# 📁 RentVerify - Project Structure

```
RentVerify/
│
├── 📄 app.py                      # Main Flask application (webhook + dashboard)
├── 📄 send_test.py                # Twilio SMS testing script (local only)
├── 📄 requirements.txt            # Python dependencies
├── 📄 Procfile                    # Gunicorn production command
├── 📄 runtime.txt                 # Python version specification
├── 📄 .env                        # Environment variables (LOCAL - not in Git)
├── 📄 .env.example                # Environment template (safe to commit)
├── 📄 .gitignore                  # Git exclusion rules
│
├── 📄 README.md                   # Project documentation
├── 📄 DEPLOYMENT.md               # Complete deployment guide
├── 📄 DEPLOYMENT_QUICK.md         # Quick deployment reference
├── 📄 TESTING_GUIDE.md            # SMS testing instructions
│
├── 📄 setup.ps1                   # Windows setup script
├── 📄 setup.sh                    # Linux/Mac setup script
│
├── 📁 templates/                  # Jinja2 HTML templates
│   ├── 📄 login.html              # Admin login page
│   └── 📄 dashboard.html          # Payment records dashboard
│
├── 📁 static/                     # Static assets (CSS, JS, images)
│   └── 📄 styles.css              # Custom CSS styles
│
├── 📁 instance/                   # Flask instance folder (auto-created)
│   └── 📄 rent_data.db            # SQLite database (auto-generated)
│
└── 📁 .git/                       # Git repository data
```

---

## 📋 File Descriptions

### **Core Application Files**

| File | Purpose | Deploy? |
|------|---------|---------|
| `app.py` | Main Flask app with routes, webhook, auth | ✅ Yes |
| `requirements.txt` | Python package dependencies | ✅ Yes |
| `Procfile` | Production server command (gunicorn) | ✅ Yes |
| `runtime.txt` | Specifies Python 3.11.7 | ✅ Yes |
| `.gitignore` | Excludes sensitive/temp files from Git | ✅ Yes |

### **Configuration Files**

| File | Purpose | Deploy? |
|------|---------|---------|
| `.env` | Actual credentials (SECRET_KEY, Twilio) | ❌ No (local only) |
| `.env.example` | Template without sensitive data | ✅ Yes |

### **Testing & Development**

| File | Purpose | Deploy? |
|------|---------|---------|
| `send_test.py` | Twilio SMS test script | ❌ No (local testing) |
| `setup.ps1` | Windows quick setup | ✅ Optional |
| `setup.sh` | Linux/Mac quick setup | ✅ Optional |

### **Documentation**

| File | Purpose | Deploy? |
|------|---------|---------|
| `README.md` | Project overview & local setup | ✅ Yes |
| `DEPLOYMENT.md` | Full deployment guide | ✅ Yes |
| `DEPLOYMENT_QUICK.md` | Quick deployment reference | ✅ Yes |
| `TESTING_GUIDE.md` | SMS testing instructions | ✅ Yes |

### **Frontend Templates**

| File | Purpose | Deploy? |
|------|---------|---------|
| `templates/login.html` | Admin authentication page | ✅ Yes |
| `templates/dashboard.html` | Payment records display | ✅ Yes |
| `static/styles.css` | Custom CSS styling | ✅ Yes |

### **Database**

| File | Purpose | Deploy? |
|------|---------|---------|
| `instance/rent_data.db` | SQLite database (auto-created) | ❌ Auto-generated |

---

## 🚀 Deployment Files

### **Procfile**
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --log-level info
```

### **runtime.txt**
```
python-3.11.7
```

### **requirements.txt**
```
Flask==3.0.0
twilio==8.10.0
python-dotenv==1.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
```

---

## 🔒 Security & Git

### **Files in `.gitignore`:**
```gitignore
# Sensitive
.env

# Development
__pycache__/
*.pyc
instance/
*.db
*.log

# Testing
send_test.py

# OS
.DS_Store
Thumbs.db
```

### **Safe to Commit:**
- ✅ `.env.example` (template without secrets)
- ✅ All `.py` files except `send_test.py`
- ✅ All documentation files
- ✅ Templates and static files
- ✅ Configuration files (Procfile, runtime.txt, requirements.txt)

### **Never Commit:**
- ❌ `.env` (contains secrets)
- ❌ `instance/` folder (database)
- ❌ `*.db` files
- ❌ `*.log` files
- ❌ `send_test.py` (testing script)

---

## 📊 Routes & URLs

### **Web Routes (Browser Access)**
```
/                   → Redirects to /login or /dashboard
/login              → Admin login page (GET/POST)
/logout             → Clear session and redirect to login
/dashboard          → Payment records display (protected)
/export             → Download CSV of all records (protected)
```

### **API Routes (Twilio Webhook)**
```
/sms                → POST - Twilio webhook for incoming SMS
```

---

## 🗄️ Database Schema

### **Table: payments**
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    status TEXT NOT NULL,              -- 'PAID' or 'NOT_PAID'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Example Records:**
| id | phone_number | status | timestamp |
|----|--------------|--------|-----------|
| 1 | +16464089380 | PAID | 2026-01-06 14:30:22 |
| 2 | +19175551234 | NOT_PAID | 2026-01-06 15:45:10 |

---

## 🌐 Environment Variables

### **Local (.env file):**
```env
SECRET_KEY=your-64-char-secret
FLASK_ENV=development
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password
TWILIO_ACCOUNT_SID=ACxxxxx...
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
TEST_RECIPIENT_PHONE=+1234567890
```

### **Production (Hosting Dashboard):**
```env
SECRET_KEY=production-secret-key
FLASK_ENV=production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
TWILIO_ACCOUNT_SID=ACxxxxx...
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
# Note: No TEST_RECIPIENT_PHONE in production
```

---

## 📦 Dependencies Breakdown

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework |
| twilio | 8.10.0 | Twilio SMS API client |
| python-dotenv | 1.0.0 | Load environment variables |
| gunicorn | 21.2.0 | Production WSGI server |
| Werkzeug | 3.0.1 | Password hashing utilities |

---

## 🎯 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     RentVerify Workflow                      │
└─────────────────────────────────────────────────────────────┘

1. Tenant sends SMS "YES" to Twilio number
                    ↓
2. Twilio forwards to webhook: POST /sms
                    ↓
3. app.py receives request and validates
                    ↓
4. Save to database: INSERT INTO payments
                    ↓
5. Send response: "Thank you! Payment verified."
                    ↓
6. Admin views dashboard: GET /dashboard
                    ↓
7. Export data: GET /export → CSV download
```

---

## 💾 Data Flow

```
Tenant Phone
     ↓
  Twilio
     ↓
POST /sms (webhook)
     ↓
  app.py
     ↓
SQLite Database (instance/rent_data.db)
     ↓
Dashboard (/dashboard)
     ↓
CSV Export (/export)
```

---

## 🔄 Deployment Flow

```
Local Development
     ↓
Git Commit & Push
     ↓
GitHub Repository
     ↓
Render/Railway (auto-deploy)
     ↓
Production Server
     ↓
Configure Twilio Webhook
     ↓
Live & Ready! 🎉
```

---

**This structure ensures:**
- ✅ Clean separation of concerns
- ✅ Secure credential management
- ✅ Easy deployment to cloud platforms
- ✅ Comprehensive documentation
- ✅ Production-ready configuration
