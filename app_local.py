"""
Local Development Version - Uses SQLite instead of PostgreSQL
Run this for local testing when you don't have PostgreSQL installed
"""

import os
import csv
import sqlite3
import logging
import sys
from io import StringIO
from datetime import datetime
from functools import wraps
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, session, redirect, url_for, flash, make_response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# ==================== Environment Configuration ====================

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv()

# ==================== Logging Configuration ====================

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger.info("Local Development Application started (SQLite mode)")

# ==================== Flask Configuration ====================

app = Flask(__name__, instance_relative_config=True)

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.secret_key = SECRET_KEY

app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for local dev
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# SQLite Database Path
DB_PATH = os.path.join(app.instance_path, 'rent_data.db')
logger.info(f"Using SQLite database at: {DB_PATH}")

# ==================== Database Functions ====================

def get_db_connection():
    """Get SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create rent_records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rent_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                reply TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("SQLite database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


# Initialize the database on startup
init_db()


# ==================== Authentication Decorator ====================

def login_required(f):
    """Decorator to protect routes - requires login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== Authentication Routes ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            flash('Login successful!', 'success')
            logger.info(f"User '{username}' logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            logger.warning(f"Failed login attempt with username: {username}")
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout the admin user."""
    username = session.get('username', 'Unknown')
    session.clear()
    flash('You have been logged out.', 'info')
    logger.info(f"User '{username}' logged out")
    return redirect(url_for('login'))


# ==================== Root Route ====================

@app.route('/')
def index():
    """Root route - redirect to dashboard if logged in, otherwise to login."""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ==================== SMS Webhook Route ====================

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Handle incoming SMS messages from Twilio webhook."""
    try:
        phone_number = request.form.get("From")
        reply = request.form.get("Body")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"Received SMS from {phone_number}: {reply}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rent_records (phone_number, reply, timestamp) VALUES (?, ?, ?)",
            (phone_number, reply, timestamp)
        )
        conn.commit()
        conn.close()
        
        logger.info(f"Message recorded in database for {phone_number}")
        return "Reply recorded", 200
        
    except Exception as e:
        logger.error(f"Error in SMS handler: {e}")
        return "Error processing message", 500


# ==================== Dashboard Route ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display payment records in a web dashboard (protected route)."""
    try:
        logger.info(f"Dashboard accessed by user: {session.get('username', 'Unknown')}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        logger.info(f"Retrieved {len(rows)} messages from database")
        
        # Convert rows to list of dictionaries
        messages = []
        for row in rows:
            messages.append({
                'phone': row['phone_number'],
                'body': row['reply'],
                'status': row['reply'].upper(),
                'timestamp': row['timestamp']
            })
        
        # Calculate summary counts
        total_messages = len(messages)
        yes_count = sum(1 for msg in messages if msg['status'] == 'YES')
        no_count = sum(1 for msg in messages if msg['status'] == 'NO')
        pending_count = total_messages - yes_count - no_count
        
        return render_template(
            'dashboard.html',
            messages=messages,
            total_messages=total_messages,
            yes_count=yes_count,
            no_count=no_count,
            pending_count=pending_count
        )
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        flash('Error loading dashboard data.', 'danger')
        return render_template('dashboard.html', messages=[], total_messages=0, yes_count=0, no_count=0, pending_count=0)


# ==================== CSV Export Route ====================

@app.route('/export')
@login_required
def export_csv():
    """Export all payment records to CSV (protected route)."""
    try:
        logger.info(f"CSV export initiated by user: {session.get('username', 'Unknown')}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        # Create CSV in memory
        si = StringIO()
        writer = csv.writer(si)
        
        # Write header
        writer.writerow(['Phone Number', 'Reply', 'Timestamp'])
        
        # Write data rows
        for row in rows:
            writer.writerow([row['phone_number'], row['reply'], row['timestamp']])
        
        # Create response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=payment_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output.headers["Content-type"] = "text/csv"
        
        logger.info(f"CSV export completed: {len(rows)} records")
        return output
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        flash('Error exporting data.', 'danger')
        return redirect(url_for('dashboard'))


# ==================== Test Data Route (Development Only) ====================

@app.route('/add-test-data')
@login_required
def add_test_data():
    """Add test SMS messages to database for testing (development only)."""
    try:
        test_messages = [
            ('+1234567890', 'YES', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ('+9876543210', 'NO', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ('+5555555555', 'Maybe', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for phone, reply, timestamp in test_messages:
            cursor.execute(
                "INSERT INTO rent_records (phone_number, reply, timestamp) VALUES (?, ?, ?)",
                (phone, reply, timestamp)
            )
        
        conn.commit()
        conn.close()
        
        flash(f'Added {len(test_messages)} test messages successfully!', 'success')
        logger.info(f"Test data added: {len(test_messages)} records")
        
    except Exception as e:
        logger.error(f"Error adding test data: {e}")
        flash('Error adding test data.', 'danger')
    
    return redirect(url_for('dashboard'))


# ==================== Run Application ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n{'='*60}")
    print(f"🚀 LOCAL DEVELOPMENT SERVER")
    print(f"{'='*60}")
    print(f"📍 URL: http://localhost:{port}")
    print(f"👤 Username: {ADMIN_USERNAME}")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print(f"💾 Database: {DB_PATH}")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', port=port, debug=True)
