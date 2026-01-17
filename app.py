# app.py - Application Factory for RentVerify

import os
import sys
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

def create_app():
    """
    Application factory for RentVerify.
    Initializes Flask, loads config, and registers blueprints.
    """
    # Load environment variables
    BASE_DIR = Path(__file__).resolve().parent
    ENV_PATH = BASE_DIR / '.env'
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    else:
        load_dotenv()

    # Logging configuration
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    logger.info("Application factory started")

    # Initialize Flask app
    app = Flask(__name__, instance_relative_config=True)

    # Register error handlers
    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)

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

    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not found - database features may not work")
    else:
        logger.info("DATABASE_URL found - PostgreSQL mode enabled")
        # Initialize database tables
        try:
            init_database(DATABASE_URL, logger)
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            # Continue anyway - tables might already exist

    # Database connection functions
    def get_db_connection():
        """Get PostgreSQL database connection."""
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL not set")
        conn = psycopg2.connect(db_url)
        return conn

    def return_db_connection(conn):
        """Return connection to pool (close for PostgreSQL)."""
        if conn:
            conn.close()

    def mask_phone_number(phone_number):
        """Mask phone number for privacy (show last 4 digits)."""
        if not phone_number or len(phone_number) < 4:
            return phone_number
        return '******' + phone_number[-4:]

    # Make functions available to app and blueprints
    app.get_db_connection = get_db_connection
    app.return_db_connection = return_db_connection
    app.mask_phone_number = mask_phone_number
    app.logger = logger

    # Register blueprints
    from routes.sms import sms_bp
    from routes.dashboard import dashboard_bp
    app.register_blueprint(sms_bp)
    app.register_blueprint(dashboard_bp)
    
    # Register relay blueprint (optional - for forwarding to multiple endpoints)
    try:
        from routes.relay import relay_bp
        app.register_blueprint(relay_bp)
    except ImportError:
        pass  # Relay is optional

    # Import and register authentication and root routes
    from flask import request, render_template, session, redirect, url_for, flash
    from werkzeug.security import generate_password_hash, check_password_hash

    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        logger.error("ADMIN_USERNAME and ADMIN_PASSWORD must be set in environment variables!")
        raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD must be set")
    ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

    def login_required(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    app.login_required = login_required

    # Make logger available globally
    app.logger_instance = logger

    @app.route('/login', methods=['GET', 'POST'])
    def login():
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
        username = session.get('username', 'Unknown')
        session.clear()
        flash('You have been logged out.', 'info')
        logger.info(f"User '{username}' logged out")
        return redirect(url_for('login'))

    @app.route('/')
    def index():
        if 'logged_in' in session:
            return redirect(url_for('dashboard.dashboard'))
        return redirect(url_for('login'))

    return app


def init_database(database_url, logger):
    """Initialize PostgreSQL database tables if they don't exist."""
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create rent_records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rent_records (
                id SERIAL PRIMARY KEY,
                phone_number TEXT NOT NULL,
                reply TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                record_type TEXT DEFAULT 'tenant'
            )
        ''')
        
        # Add record_type column if it doesn't exist (for existing databases)
        cursor.execute('''
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='rent_records' AND column_name='record_type'
                ) THEN
                    ALTER TABLE rent_records ADD COLUMN record_type TEXT DEFAULT 'tenant';
                END IF;
            END $$;
        ''')
        
        # Create payments table (if needed)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                phone_number TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# For flask run compatibility
app = create_app()

# Make functions available at module level for imports
get_db_connection = app.get_db_connection
return_db_connection = app.return_db_connection
mask_phone_number = app.mask_phone_number
login_required = app.login_required
logger = app.logger_instance

# For direct execution
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)