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

| File | Description |
|------|-------------|
| `app.py` | Main Flask application with `/sms` webhook and `/dashboard` route |
| `send_test.py` | Script to send test SMS messages |
| `.env` | Environment variables (API credentials) |
| `.gitignore` | Excludes sensitive files from version control |
| `rent_data.db` | SQLite database (auto-created on first run) |

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

## Roadmap

- [ ] Add tenant name field to database
- [ ] Export payment records to CSV
- [ ] Email notifications for non-payments
- [ ] Multi-tenant support with unique links
- [ ] Deploy to Heroku/Railway/Render

---

## License

MIT (placeholder — update as needed)

---

**Built with ❤️ for landlords who value automation**
