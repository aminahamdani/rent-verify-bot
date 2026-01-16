"""
Dashboard Blueprint for RentVerify

This blueprint contains all dashboard-related routes, including:
- Dashboard HTML view
- CSV export endpoint
- Test data endpoint (local only)

Business logic and template rendering are unchanged.
"""


from flask import Blueprint, render_template, request, session, redirect, url_for, flash, make_response
from utils.validators import validate_dashboard_form
from datetime import datetime
import csv
from io import StringIO
from services import db_service

# Create the dashboard blueprint
# url_prefix is not set, so routes are registered at the root level

dashboard_bp = Blueprint('dashboard', __name__)

# ==================== Dashboard Route ====================
@dashboard_bp.route('/dashboard')
def dashboard():
    """Display payment records in a web dashboard (protected route)."""
    # Lazy import to avoid circular dependencies
    try:
        from app import get_db_connection, mask_phone_number, logger, login_required, return_db_connection
        use_mask = True
        is_local = False
    except ImportError:
        from app_local import get_db_connection, logger, login_required
        use_mask = False
        is_local = True
        def mask_phone_number(phone_number):
            return phone_number
        def return_db_connection(conn):
            if conn:
                conn.close()
    # Apply login protection
    @login_required
    def inner_dashboard():
        # Example: Validate login form if POST (extend as needed)
        if request.method == 'POST':
            is_valid, errors = validate_dashboard_form(request.form)
            if not is_valid:
                for field, error in errors.items():
                    flash(f"{field}: {error}", 'danger')
                return redirect(url_for('dashboard'))
        try:
            logger.info(f"Dashboard accessed by user: {session.get('username', 'Unknown')}")
            conn = db_service.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            db_service.close_db_connection(conn)
            logger.info(f"Retrieved {len(rows)} messages from database")
            messages = []
            for row in rows:
                phone = mask_phone_number(row['phone_number']) if use_mask else row['phone_number']
                messages.append({
                    'phone': phone,
                    'body': row['reply'],
                    'status': row['reply'].upper(),
                    'timestamp': row['timestamp']
                })
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
    return inner_dashboard()

# ==================== CSV Export Route ====================
@dashboard_bp.route('/export')
def export_csv():
    """Export all payment records to CSV (protected route)."""
    try:
        from app import get_db_connection, mask_phone_number, logger, login_required, return_db_connection
        use_mask = True
        is_local = False
    except ImportError:
        from app_local import get_db_connection, logger, login_required
        use_mask = False
        is_local = True
        def mask_phone_number(phone_number):
            return phone_number
        def return_db_connection(conn):
            if conn:
                conn.close()
    @login_required
    def inner_export_csv():
        try:
            logger.info(f"CSV export initiated by user: {session.get('username', 'Unknown')}")
            conn = db_service.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            db_service.close_db_connection(conn)
            si = StringIO()
            writer = csv.writer(si)
            writer.writerow(['Phone Number', 'Reply', 'Timestamp'])
            for row in rows:
                phone = mask_phone_number(row['phone_number']) if use_mask else row['phone_number']
                writer.writerow([phone, row['reply'], row['timestamp']])
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = f"attachment; filename=payment_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output.headers["Content-type"] = "text/csv"
            logger.info(f"CSV export completed: {len(rows)} records")
            return output
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            flash('Error exporting data.', 'danger')
            return redirect(url_for('dashboard'))
    return inner_export_csv()

# ==================== Test Data Route (Development Only) ====================
@dashboard_bp.route('/add-test-data')
def add_test_data():
    """Add test SMS messages to database for testing (development only)."""
    try:
        from app_local import get_db_connection, logger, login_required
    except ImportError:
        return redirect(url_for('dashboard'))
    @login_required
    def inner_add_test_data():
        try:
            test_messages = [
                ('+1234567890', 'YES', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ('+9876543210', 'NO', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ('+5555555555', 'Maybe', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ]
            conn = db_service.get_db_connection()
            cursor = conn.cursor()
            for phone, reply, timestamp in test_messages:
                cursor.execute(
                    "INSERT INTO rent_records (phone_number, reply, timestamp) VALUES (?, ?, ?)",
                    (phone, reply, timestamp)
                )
            conn.commit()
            db_service.close_db_connection(conn)
            flash(f'Added {len(test_messages)} test messages successfully!', 'success')
            logger.info(f"Test data added: {len(test_messages)} records")
        except Exception as e:
            logger.error(f"Error adding test data: {e}")
            flash('Error adding test data.', 'danger')
        return redirect(url_for('dashboard'))
    return inner_add_test_data()
