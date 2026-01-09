# Local Development Setup

## Quick Start

### Running Locally with SQLite

Since you don't have PostgreSQL installed locally, use the local development version:

```powershell
# Run the local version (uses SQLite)
python app_local.py
```

Then open: http://localhost:5000

### Default Credentials
- **Username**: admin
- **Password**: password

*(Or use values from your .env file)*

### Testing the Dashboard

#### Option 1: Add Test Data
1. Login to the dashboard
2. Visit: http://localhost:5000/add-test-data
3. This adds 3 sample SMS messages
4. Dashboard will show them and auto-refresh every 30 seconds

#### Option 2: Send Real SMS (with ngrok)
1. Install ngrok: https://ngrok.com/download
2. Run your app: `python app_local.py`
3. In another terminal: `ngrok http 5000`
4. Copy the ngrok URL (e.g., https://abc123.ngrok.io)
5. Set Twilio webhook to: `https://abc123.ngrok.io/sms`
6. Send SMS to your Twilio number
7. Watch it appear in the dashboard!

## What Was Fixed

### ✅ Flash Messages
- Flash messages now display properly at the top of the dashboard
- Auto-hide after 5 seconds
- Can be closed manually with X button
- Color-coded (green=success, red=error, yellow=warning)

### ✅ Auto-Refresh
- Dashboard refreshes every 30 seconds automatically
- Shows refresh indicator
- New SMS messages appear without manual refresh

### ✅ Local Development
- Created `app_local.py` for SQLite (no PostgreSQL needed)
- Added `/add-test-data` route for quick testing
- Better logging and error messages

## File Structure

- `app.py` - Production version (PostgreSQL for Render/Railway)
- `app_local.py` - Development version (SQLite for local testing)
- `templates/dashboard.html` - Updated with flash messages and auto-refresh

## Production Deployment

For production (Render/Railway), continue using `app.py` which expects PostgreSQL.

The dashboard will:
1. Show flash messages for login/logout/errors
2. Auto-refresh every 30 seconds to show new SMS
3. Display messages in a table with YES/NO/Pending badges

## Troubleshooting

### Messages still not showing?
1. Check if app is receiving webhooks (check terminal logs)
2. Verify Twilio webhook URL is correct
3. Make sure app is publicly accessible (use ngrok locally)
4. Check database has records: `python check_db.py`

### Flash messages disappearing too fast?
Edit the timeout in dashboard.html line ~100:
```javascript
}, 5000); // Change to 10000 for 10 seconds
```

### Want faster refresh?
Edit dashboard.html line ~92:
```javascript
}, 30000); // Change to 10000 for 10 seconds
```
