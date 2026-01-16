import os
import csv

# app.py - Application Factory for RentVerify

import os
import sys
import logging
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

    # Register blueprints
    from routes.sms import sms_bp
    from routes.dashboard import dashboard_bp
    app.register_blueprint(sms_bp)
    app.register_blueprint(dashboard_bp)

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

# For flask run compatibility
app = create_app()

# For direct execution
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)