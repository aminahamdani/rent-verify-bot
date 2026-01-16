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
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            flash('Login successful!', 'success')
            logger.info(f"User '{username}' logged in successfully")
            return redirect(url_for('dashboard.dashboard'))
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
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('login'))



# ==================== SMS Webhook Route (moved) ====================
# The SMS webhook handler was moved to `routes/sms.py` as the `sms_bp` blueprint.
from routes.sms import sms_bp
app.register_blueprint(sms_bp)

from routes.dashboard import dashboard_bp
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
