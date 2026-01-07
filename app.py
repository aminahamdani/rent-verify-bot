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

# Get the absolute path to the .env file
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

# Load environment variables
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv()  # Try default location

# ==================== Logging Configuration ====================

# Use stdout for production (Render/Railway compatible)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger.info("Application started")

# ==================== Flask Configuration ====================

# Initialize Flask app with instance folder for database
app = Flask(__name__, instance_relative_config=True)

# Secret key configuration
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    logger.error("SECRET_KEY not found in environment variables!")
    raise ValueError("SECRET_KEY must be set in environment variables")
app.secret_key = SECRET_KEY

# Session security configuration
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    logger.error("ADMIN_USERNAME and ADMIN_PASSWORD must be set in environment variables!")
    raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD must be set")

# Hash the password for secure comparison (one-time hash)
# Note: In production, store hashed passwords in a secure database
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Database path in instance folder
DATABASE_PATH = os.path.join(app.instance_path, 'rent_data.db')


# ==================== Database Functions ====================

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        if conn:
            conn.close()


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
    # Redirect to dashboard if already logged in
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Secure password comparison using hashing
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True  # Use permanent session timeout
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

@app.route('/sms', methods=['POST'])
def sms_reply():
    """Handle incoming SMS messages from Twilio webhook."""
    conn = None
    try:
        # Get the incoming message and sender's phone number
        incoming_msg = request.form.get('Body', '').strip()
        sender_phone = request.form.get('From', '')
        
        logger.info(f"Received SMS from {sender_phone}: {incoming_msg}")
        
        # Create Twilio response object
        resp = MessagingResponse()
        
        # Validate and process the message
        if incoming_msg.upper() == 'YES':
            try:
                # Save PAID status to database
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO payments (phone_number, status) VALUES (?, ?)",
                    (sender_phone, 'PAID')
                )
                conn.commit()
                resp.message('Thank you! Payment verified.')
                logger.info(f"Payment PAID recorded for {sender_phone}")
            except sqlite3.Error as e:
                logger.error(f"Database error while saving PAID status: {e}")
                resp.message('System error. Please try again later.')
            finally:
                if conn:
                    conn.close()
            
        elif incoming_msg.upper() == 'NO':
            try:
                # Save NOT_PAID status to database
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO payments (phone_number, status) VALUES (?, ?)",
                    (sender_phone, 'NOT_PAID')
                )
                conn.commit()
                resp.message('Alert: Non-payment recorded.')
                logger.info(f"Payment NOT_PAID recorded for {sender_phone}")
            except sqlite3.Error as e:
                logger.error(f"Database error while saving NOT_PAID status: {e}")
                resp.message('System error. Please try again later.')
            finally:
                if conn:
                    conn.close()
            
        else:
            # Invalid response - request YES or NO
            resp.message('Please reply with YES or NO.')
            logger.warning(f"Invalid response from {sender_phone}: {incoming_msg}")
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"Unexpected error in SMS handler: {e}")
        resp = MessagingResponse()
        resp.message('System error. Please contact support.')
        return str(resp)


# ==================== Dashboard Route ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display payment records in a web dashboard (protected route)."""
    conn = None
    try:
        logger.info(f"Dashboard accessed by user: {session.get('username', 'Unknown')}")
        
        # Fetch all payment records from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries and transform for template
        messages = []
        for row in rows:
            messages.append({
                'phone': row['phone_number'],
                'body': f"Payment status: {row['status']}",
                'status': 'YES' if row['status'] == 'PAID' else 'NO',
                'timestamp': row['timestamp']
            })
        
        # Calculate summary counts
        total_messages = len(messages)
        yes_count = sum(1 for msg in messages if msg['status'] == 'YES')
        no_count = sum(1 for msg in messages if msg['status'] == 'NO')
        pending_count = total_messages - yes_count - no_count
        
        # Render the dashboard template with summary data
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
        return render_template('dashboard.html', rows=[], paid_count=0, not_paid_count=0, total_count=0)
    finally:
        if conn:
            conn.close()


# ==================== CSV Export Route ====================

@app.route('/export')
@login_required
def export_csv():
    """Export all payment records to CSV (protected route)."""
    conn = None
    try:
        logger.info(f"CSV export initiated by user: {session.get('username', 'Unknown')}")
        
        # Fetch all payment records
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        # Create CSV in memory
        si = StringIO()
        writer = csv.writer(si)
        
        # Write header
        writer.writerow(['ID', 'Phone Number', 'Status', 'Timestamp'])
        
        # Write data rows
        for row in rows:
            writer.writerow([row['id'], row['phone_number'], row['status'], row['timestamp']])
        
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
    finally:
        if conn:
            conn.close()


# ==================== Run Application ====================

if __name__ == '__main__':
    # Get port from environment (for Render/Railway deployment)
    port = int(os.getenv('PORT', 5000))
    # Disable debug in production
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)