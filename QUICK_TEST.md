# Quick Test Guide for RentVerify

## Start the Local Server

```powershell
python app_local.py
```

The server should start at: http://127.0.0.1:5000

## Test the Application

### Option 1: Run Automated Tests (Recommended)

1. Keep the server running in one terminal
2. Open a new PowerShell terminal
3. Run:
```powershell
python test_local.py
```

### Option 2: Manual Testing

1. Visit http://127.0.0.1:5000/login
2. Login with:
   - Username: `admin`
   - Password: `password`
3. You should see the dashboard

### Simulate SMS Messages

In a new terminal window (while server is running):

```powershell
# Send test SMS
python test_webhook.py
```

Or manually send test messages:

```powershell
curl -X POST http://127.0.0.1:5000/sms -d "From=+12345678901&Body=YES"
curl -X POST http://127.0.0.1:5000/sms -d "From=+12345678902&Body=NO"
```

## Check Database

```powershell
python check_db.py
```

## Expected Results

✓ Server starts without errors
✓ Login page loads
✓ Can login with credentials
✓ Dashboard displays messages
✓ Flash messages appear and fade
✓ SMS webhook receives messages
✓ Messages appear in database
✓ Dashboard updates with new data

## Common Issues

### Issue: "Module not found"
**Solution:** Install requirements
```powershell
pip install -r requirements.txt
```

### Issue: "Database locked"
**Solution:** Close any other database connections and restart

### Issue: "Port already in use"
**Solution:** Kill the process using port 5000
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "Flash messages not showing"
**Solution:** Already fixed in templates/dashboard.html - messages now appear and auto-fade

### Issue: "Messages not updating"
**Solution:** Refresh the page (F5) or use the refresh button in dashboard
---

## Diagnostic Checkpoint - January 9, 2026

### Loading State Troubleshooting

**SYMPTOM:** Repeated loading state when accessing local server

**INVESTIGATION COMPLETED:**

✅ **Step 1: Code Analysis**
- Examined app_local.py thoroughly (lines 1-337)
- ✓ No infinite loops detected
- ✓ No blocking calls found
- ✓ All routes properly registered (/, /login, /logout, /dashboard, /sms, /export, /add-test-data)
- ✓ Database operations use proper commit/close patterns
- ✓ No unhandled exceptions that would cause hanging

✅ **Step 2: Flask Configuration**
- Entry point: `if __name__ == '__main__'` on line 326
- Server config: `app.run(host='0.0.0.0', port=port, debug=True)` on line 336
- ✓ Debug mode enabled (auto-reload on file changes)
- ✓ All decorators properly applied (@login_required, @app.route)

✅ **Step 3: Thread/Process Check**
- No Python processes currently running
- No blocking threads detected in code
- No input() or blocking I/O operations

✅ **Step 4: Log Analysis**
- Last log entry: 2026-01-06 01:03:56 - GET /static/styles.css successful
- Server was working correctly at last test
- Multiple auto-reloads due to file change detection (app.py modifications)
- User 'amina' successfully logged in and accessed dashboard

**ROOT CAUSE IDENTIFIED:**
The loading state is likely caused by:
1. **Auto-reload loop**: Flask's debug mode detecting changes in app.py causing repeated restarts
2. **Browser cache issue**: Static resources (CSS) not loading causing incomplete page render
3. **No active server**: Python process not currently running (server stopped)

**SOLUTION:**
1. Ensure app.py is stable (no active editing)
2. Clear browser cache or hard refresh (Ctrl+F5)
3. Restart server with: `python app_local.py`
4. Access clean session at: http://127.0.0.1:5000
5. Login with credentials from .env: username=amina, password=0000

**LAST SUCCESSFUL STATE:**
- Database: Initialized successfully
- Routes: All registered and functional
- Authentication: Working (user 'amina' logged in)
- Dashboard: Rendered successfully with data

**NEXT ACTION:** Restart server and test with clean browser session