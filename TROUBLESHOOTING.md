# Troubleshooting Guide

## Issue: Messages Disappearing & Tables Not Updating

### Problems Identified:
1. **Flash messages were not displayed** - Dashboard template lacked flash message display code
2. **No auto-refresh** - Dashboard was static and didn't update automatically
3. **Local vs Production mismatch** - App expects PostgreSQL but runs SQLite locally

### Fixes Applied:

#### 1. ✅ Flash Messages Now Display
- Added flash message display section to dashboard.html
- Messages auto-hide after 5 seconds
- Styled with appropriate colors (success=green, error=red, etc.)

#### 2. ✅ Auto-Refresh Enabled
- Dashboard now auto-refreshes every 30 seconds
- Visual indicator shows "Auto-refreshing every 30 seconds"
- New SMS messages will appear automatically

### Testing the Fixes:

#### If Running in Production (Render/Railway):
1. Send an SMS to your Twilio number with "YES" or "NO"
2. Visit your dashboard - it should auto-refresh in 30 seconds
3. New messages will appear in the table

#### If Running Locally:
You have two options:

**Option A: Use SQLite for Local Development**
See LOCAL_SETUP.md for instructions

**Option B: Set up PostgreSQL Locally**
1. Install PostgreSQL
2. Create a local database
3. Set DATABASE_URL in .env file

### Webhook Checklist:
- [ ] Twilio number configured
- [ ] Webhook URL set to: https://your-app.onrender.com/sms
- [ ] App is running (not sleeping on free tier)
- [ ] Database connection is working

### Testing:
1. Login to dashboard
2. Send test SMS
3. Wait 30 seconds or manually refresh
4. Check if message appears in table
