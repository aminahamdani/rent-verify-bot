import os
import csv
import psycopg2
import psycopg2.extras
from psycopg2 import pool
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

# Database connection URL from environment (PostgreSQL on Render)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    logger.error("DATABASE_URL not found in environment variables!")
    raise ValueError("DATABASE_URL must be set in environment variables")

# Initialize connection pool for better performance
try:
    connection_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=DATABASE_URL
    )
    if connection_pool:
        logger.info("Connection pool created successfully")
except psycopg2.Error as e:
    logger.error(f"Error creating connection pool: {e}")
    raise


# ==================== Database Functions ====================

def get_db_connection():
    """Get a connection from the pool."""
    try:
        conn = connection_pool.getconn()
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def return_db_connection(conn):
    """Return a connection to the pool."""
    if conn:
        connection_pool.putconn(conn)


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                phone_number TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rent_records (
                phone_number TEXT,
                reply TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        logger.info("Database initialized successfully")
    except psycopg2.Error as e:
        logger.error(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        return_db_connection(conn)


# Initialize the database on startup
init_db()


# ==================== Phone Number Masking ====================

def mask_phone_number(phone_number):
    """Mask phone number, showing only last 4 digits.
    
    Args:
        phone_number (str): The phone number to mask (e.g., '+12345679380')
    
    Returns:
        str: Masked phone number (e.g., '******9380')
    """
    if not phone_number:
        return '******0000'
    
    # Remove any non-digit characters except '+'
    cleaned = ''.join(c for c in phone_number if c.isdigit())
    
    # Get last 4 digits
    last_four = cleaned[-4:] if len(cleaned) >= 4 else cleaned.zfill(4)
    
    # Return masked format
    return f"******{last_four}"


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

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Handle incoming SMS messages from Twilio webhook."""
    conn = None
    try:
        # Capture raw phone number from Twilio
        raw_phone_number = request.form.get("From")
        reply = request.form.get("Body")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Mask the phone number immediately
        masked_phone = mask_phone_number(raw_phone_number)
        
        # Log only the masked version
        logger.info(f"Received SMS from {masked_phone}: {reply}")

        # Save only the masked phone number to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rent_records (phone_number, reply, timestamp) VALUES (%s, %s, %s)", (masked_phone, reply, timestamp))
        conn.commit()
        
        logger.info(f"Message recorded in database for {masked_phone}")
        return "Reply recorded", 200
        
    except Exception as e:
        logger.error(f"Error in SMS handler: {e}")
        return "Error processing message", 500
    finally:
        return_db_connection(conn)


# ==================== Dashboard Route ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display payment records in a web dashboard (protected route)."""
    conn = None
    try:
        logger.info(f"Dashboard accessed by user: {session.get('username', 'Unknown')}")
        
        # Fetch all records from rent_records database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        logger.info(f"Retrieved {len(rows)} messages from database")
        
        # Convert rows to list of dictionaries and transform for template
        # Mask phone numbers at display time (handles both new masked and old unmasked numbers)
        messages = []
        for row in rows:
            # Get phone number and ensure it's masked
            phone_from_db = row['phone_number']
            # If already masked (starts with ******), use as-is; otherwise mask it
            if phone_from_db and phone_from_db.startswith('******'):
                masked_phone = phone_from_db
            else:
                masked_phone = mask_phone_number(phone_from_db)
            
            messages.append({
                'phone': masked_phone,
                'body': row['reply'],
                'status': row['reply'].upper(),
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
        return_db_connection(conn)


# ==================== CSV Export Route ====================

@app.route('/export')
@login_required
def export_csv():
    """Export all payment records to CSV (protected route)."""
    conn = None
    try:
        logger.info(f"CSV export initiated by user: {session.get('username', 'Unknown')}")
        
        # Fetch all records from rent_records
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        # Create CSV in memory
        si = StringIO()
        writer = csv.writer(si)
        
        # Write header
        writer.writerow(['Phone Number', 'Reply', 'Timestamp'])
        
        # Write data rows with masked phone numbers
        for row in rows:
            phone_from_db = row['phone_number']
            # If already masked (starts with ******), use as-is; otherwise mask it
            if phone_from_db and phone_from_db.startswith('******'):
                masked_phone = phone_from_db
            else:
                masked_phone = mask_phone_number(phone_from_db)
            writer.writerow([masked_phone, row['reply'], row['timestamp']])
        
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
        return_db_connection(conn)


# ==================== Run Application ====================

if __name__ == '__main__':
    # Get port from environment (for Render/Railway deployment)
    port = int(os.getenv('PORT', 5000))
    # Disable debug in production
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)