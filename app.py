import os
import csv
import sqlite3
import logging
from io import StringIO
from datetime import datetime
from functools import wraps
from flask import Flask, request, render_template, session, redirect, url_for, flash, make_response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== Logging Configuration ====================

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info("Application started")

# ==================== Flask Configuration ====================

# Initialize Flask app with instance folder for database
app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'changeme')

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
        logging.error(f"Database connection error: {e}")
        raise


def init_db():
    """Initialize the database and create tables if they don't exist."""
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
        conn.close()
        logging.info("Database initialized successfully")
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
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
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            logging.info(f"User '{username}' logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            logging.warning(f"Failed login attempt with username: {username}")
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout the admin user."""
    username = session.get('username', 'Unknown')
    session.clear()
    flash('You have been logged out.', 'info')
    logging.info(f"User '{username}' logged out")
    return redirect(url_for('login'))


# ==================== SMS Webhook Route ====================

@app.route('/sms/', methods=['POST'])
def sms_reply():
    """Handle incoming SMS messages from Twilio webhook."""
    try:
        # Get the incoming message and sender's phone number
        incoming_msg = request.form.get('Body', '').strip()
        sender_phone = request.form.get('From', '')
        
        logging.info(f"Received SMS from {sender_phone}: {incoming_msg}")
        
# ==================== Dashboard Route ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display payment records in a web dashboard (protected route)."""
    try:
        logging.info(f"Dashboard accessed by user: {session.get('username', 'Unknown')}")
        
        # Fetch all payment records from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        # Calculate summary counts
        cursor.execute("SELECT COUNT(*) FROM payments WHERE status = 'PAID'")
        paid_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM payments WHERE status = 'NOT_PAID'")
        not_paid_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Convert rows to list of dictionaries for template
        rows_list = [dict(row) for row in rows]
        
        # Render the dashboard template with summary data
        return render_template(
            'dashboard.html',
            rows=rows_list,
            paid_count=paid_count,
            not_paid_count=not_paid_count,
            total_count=len(rows_list)
        )
        
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        flash('Error loading dashboard data.', 'danger')
        return render_template('dashboard.html', rows=[], paid_count=0, not_paid_count=0, total_count=0)


# ==================== CSV Export Route ====================

@app.route('/export')
@login_required
def export_csv():
    """Export all payment records to CSV (protected route)."""
    try:
        logging.info(f"CSV export initiated by user: {session.get('username', 'Unknown')}")
        
        # Fetch all payment records
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
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
        
        logging.info(f"CSV export completed: {len(rows)} records")
        return output
        
    except Exception as e:
        logging.error(f"Error exporting CSV: {e}")
        flash('Error exporting data.', 'danger')
        return redirect(url_for('dashboard')
                resp.message('Thank you! Payment verified.')
                logging.info(f"Payment PAID recorded for {sender_phone}")
            except sqlite3.Error as e:
                logging.error(f"Database error while saving PAID status: {e}")
                resp.message('System error. Please try again later.')
            
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
                conn.close()
                resp.message('Alert: Non-payment recorded.')
                logging.info(f"Payment NOT_PAID recorded for {sender_phone}")
            except sqlite3.Error as e:
                logging.error(f"Database error while saving NOT_PAID status: {e}")
                resp.message('System error. Please try again later.')
            
        else:
            # Invalid response - request YES or NO
            resp.message('Please reply with YES or NO.')
            logging.warning(f"Invalid response from {sender_phone}: {incoming_msg}")
        
        return str(resp)
        
    except Exception as e:
        logging.error(f"Unexpected error in SMS handler: {e}")
        resp = MessagingResponse()
        resp.message('System error. Please contact support.')
        return str(resp)


@app.route('/dashboard')
def dashboard():
    """Display payment records in a web dashboard."""
    # Fetch all payment records from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to list of dictionaries for template
    rows_list = [dict(row) for row in rows]

    # Render the dashboard template
    return render_template('dashboard.html', rows=rows_list)


# ==================== Run Application ====================

if __name__ == '__main__':
    app.run(debug=True)