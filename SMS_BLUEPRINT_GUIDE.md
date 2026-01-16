# SMS Blueprint Quick Reference

## Overview
The SMS blueprint handles all Twilio webhook integration for the RentVerify application.

---

## Blueprint Details

| Property | Value |
|----------|-------|
| **Blueprint Name** | `sms_bp` |
| **Location** | `routes/sms.py` |
| **Route** | `POST /sms` |
| **Purpose** | Handle incoming SMS messages from Twilio |

---

## How to Use

### Basic Import
```python
from routes.sms import sms_bp
```

### Register in Flask App
```python
from flask import Flask
from routes.sms import sms_bp

app = Flask(__name__)
app.register_blueprint(sms_bp)
```

### Alternative Import (via package)
```python
from routes import sms_bp

app.register_blueprint(sms_bp)
```

---

## Endpoint Details

### POST /sms
Receives and processes incoming SMS messages from Twilio.

**Twilio Webhook Configuration:**
```
URL: https://yourapp.com/sms
Method: POST
```

**Expected Parameters** (sent by Twilio):
| Parameter | Type | Description |
|-----------|------|-------------|
| `From` | string | Sender's phone number (e.g., `+1234567890`) |
| `Body` | string | Message content |

**Response Codes:**
| Code | Meaning |
|------|---------|
| 200 | Success - Message recorded |
| 500 | Error - Check logs |

---

## Function: `sms_reply()`

**Location**: `routes/sms.py`, line 20

**Responsibility**:
- Extract SMS data from Twilio webhook
- Query database helpers (lazy imported)
- Mask phone number if in production
- Insert message into `rent_records` table
- Return appropriate HTTP response

**Key Features**:
- ✅ Lazy imports (no circular dependencies)
- ✅ PostgreSQL/SQLite support
- ✅ Phone number masking (production only)
- ✅ Comprehensive error handling
- ✅ Database connection cleanup

---

## Database Operations

### Table: `rent_records`
```sql
CREATE TABLE rent_records (
    id INTEGER PRIMARY KEY,
    phone_number TEXT,
    reply TEXT,
    timestamp TEXT
)
```

### INSERT Operation
The blueprint inserts SMS data:
```python
INSERT INTO rent_records (phone_number, reply, timestamp) 
VALUES (masked_phone, reply, timestamp)
```

---

## Environment Support

### PostgreSQL (app.py)
- Uses connection pooling
- Phone numbers masked
- Uses `%s` SQL parameter style
- Production-ready

### SQLite (app_local.py)
- Direct connection
- Phone numbers NOT masked
- Uses `?` SQL parameter style
- Local development

---

## Lazy Import Pattern

The blueprint uses lazy imports to work with both app.py and app_local.py:

```python
# Try production app (PostgreSQL)
try:
    from app import get_db_connection, return_db_connection, mask_phone_number, logger
except:
    # Fallback to local app (SQLite)
    from app_local import get_db_connection, logger
    # Provide adapter functions
```

**Benefits**:
- No circular imports
- Works in both environments
- Graceful fallback

---

## Logging

The blueprint logs important events:

```
INFO: Received SMS from ******9380: YES
INFO: Message recorded in database for ******9380
ERROR: Error in SMS handler: <error details>
```

Logs include:
- Incoming SMS (masked phone number)
- Database insertion confirmation
- Any errors encountered

---

## Error Handling

The blueprint handles errors gracefully:

1. **Database connection error**: Logs and returns 500
2. **Invalid SMS data**: Skipped gracefully
3. **Logger unavailable**: Execution continues
4. **Connection cleanup**: Attempted even on error

```python
try:
    # Process SMS
except Exception as e:
    logger.error(f"Error in SMS handler: {e}")
    return "Error processing message", 500
finally:
    # Always cleanup
    return_db_connection(conn)
```

---

## Testing

### Manual Test (curl)
```bash
curl -X POST http://localhost:5000/sms \
  -d "From=+1234567890" \
  -d "Body=YES"
```

### Expected Response
```
HTTP/1.1 200 OK
Reply recorded
```

### Check Database
```python
# app_local.py
python -c "
import sqlite3
conn = sqlite3.connect('instance/rent_data.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM rent_records ORDER BY timestamp DESC LIMIT 1')
print(cursor.fetchone())
"
```

---

## Security Considerations

1. **Phone Number Masking**: Production app masks phone numbers (`******9380`)
2. **No Authentication**: Twilio webhook is public (relies on Twilio's security)
3. **Database Injection**: Uses parameterized queries (`%s`, `?`)
4. **Error Messages**: Generic errors to avoid information leaks

---

## Future Enhancements

Possible improvements:
- Add request signature verification (Twilio auth token)
- Implement SMS response messaging (send TwiML response)
- Add rate limiting
- Support for multiple Twilio numbers
- SMS history/conversation tracking

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| SMS not recorded | Check database connection, check logs |
| Phone number not masked | Check if running in production mode |
| Import error | Ensure `app.py` or `app_local.py` in same directory |
| Circular import | Use lazy imports (already implemented) |

---

## Related Files

- [routes/sms.py](routes/sms.py) - Blueprint implementation
- [app.py](app.py) - Production app (registers blueprint)
- [app_local.py](app_local.py) - Local dev app (registers blueprint)
- [BLUEPRINT_REFACTORING.md](BLUEPRINT_REFACTORING.md) - Full refactoring documentation
