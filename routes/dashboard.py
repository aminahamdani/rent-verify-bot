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
        from app import mask_phone_number, logger, login_required
        use_mask = True
    except ImportError:
        try:
            from app_local import logger, login_required
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
            def login_required(f):
                from functools import wraps
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    if 'logged_in' not in session:
                        flash('Please log in to access this page.', 'warning')
                        return redirect(url_for('login'))
                    return f(*args, **kwargs)
                return decorated_function
        use_mask = False
        def mask_phone_number(phone_number):
            return phone_number
    
    # Apply login protection
    @login_required
    def inner_dashboard():
        # Example: Validate login form if POST (extend as needed)
        if request.method == 'POST':
            is_valid, errors = validate_dashboard_form(request.form)
            if not is_valid:
                for field, error in errors.items():
                    flash(f"{field}: {error}", 'danger')
                return redirect(url_for('dashboard.dashboard'))
        try:
            logger.info(f"Dashboard accessed by user: {session.get('username', 'Unknown')}")
            conn = db_service.get_db_connection()
            
            # Use appropriate cursor based on database type
            import os
            DATABASE_URL = os.getenv('DATABASE_URL')
            if DATABASE_URL:
                # PostgreSQL
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                # SQLite - row_factory is set on connection, not cursor
                cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            db_service.close_db_connection(conn)
            logger.info(f"Retrieved {len(rows)} messages from database")
            
            # Separate messages by type
            tenant_messages = []
            landlord_messages = []
            all_messages = []
            
            for row in rows:
                # Handle both dict-like (PostgreSQL) and tuple-like (SQLite) rows
                if isinstance(row, dict):
                    phone = mask_phone_number(row['phone_number']) if use_mask else row['phone_number']
                    record_type = row.get('record_type', 'tenant')
                    msg_data = {
                        'phone': phone,
                        'body': row['reply'],
                        'status': row['reply'].upper(),
                        'timestamp': row['timestamp'],
                        'type': record_type
                    }
                else:
                    # SQLite Row object
                    phone = mask_phone_number(row['phone_number']) if use_mask else row['phone_number']
                    record_type = row.get('record_type', 'tenant') if hasattr(row, 'get') else 'tenant'
                    msg_data = {
                        'phone': phone,
                        'body': row['reply'],
                        'status': row['reply'].upper(),
                        'timestamp': row['timestamp'],
                        'type': record_type
                    }
                
                all_messages.append(msg_data)
                if record_type == 'landlord':
                    landlord_messages.append(msg_data)
                else:
                    tenant_messages.append(msg_data)
            
            # Calculate statistics
            total_messages = len(all_messages)
            yes_count = sum(1 for msg in all_messages if msg['status'] == 'YES')
            no_count = sum(1 for msg in all_messages if msg['status'] == 'NO')
            pending_count = total_messages - yes_count - no_count
            
            # Tenant statistics
            tenant_total = len(tenant_messages)
            tenant_yes = sum(1 for msg in tenant_messages if msg['status'] == 'YES')
            tenant_no = sum(1 for msg in tenant_messages if msg['status'] == 'NO')
            tenant_pending = tenant_total - tenant_yes - tenant_no
            
            # Landlord statistics
            landlord_total = len(landlord_messages)
            landlord_yes = sum(1 for msg in landlord_messages if msg['status'] == 'YES')
            landlord_no = sum(1 for msg in landlord_messages if msg['status'] == 'NO')
            landlord_pending = landlord_total - landlord_yes - landlord_no
            
            return render_template(
                'dashboard.html',
                messages=all_messages,
                tenant_messages=tenant_messages,
                landlord_messages=landlord_messages,
                total_messages=total_messages,
                yes_count=yes_count,
                no_count=no_count,
                pending_count=pending_count,
                tenant_total=tenant_total,
                tenant_yes=tenant_yes,
                tenant_no=tenant_no,
                tenant_pending=tenant_pending,
                landlord_total=landlord_total,
                landlord_yes=landlord_yes,
                landlord_no=landlord_no,
                landlord_pending=landlord_pending
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
        from app import mask_phone_number, logger, login_required
        use_mask = True
    except ImportError:
        try:
            from app_local import logger, login_required
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
            def login_required(f):
                from functools import wraps
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    if 'logged_in' not in session:
                        flash('Please log in to access this page.', 'warning')
                        return redirect(url_for('login'))
                    return f(*args, **kwargs)
                return decorated_function
        use_mask = False
        def mask_phone_number(phone_number):
            return phone_number
    
    @login_required
    def inner_export_csv():
        try:
            logger.info(f"CSV export initiated by user: {session.get('username', 'Unknown')}")
            conn = db_service.get_db_connection()
            
            # Use appropriate cursor based on database type
            import os
            DATABASE_URL = os.getenv('DATABASE_URL')
            if DATABASE_URL:
                # PostgreSQL
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                # SQLite
                cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM rent_records ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            db_service.close_db_connection(conn)
            si = StringIO()
            writer = csv.writer(si)
            writer.writerow(['Phone Number', 'Reply', 'Type', 'Timestamp'])
            for row in rows:
                # Handle both dict-like (PostgreSQL) and tuple-like (SQLite) rows
                if isinstance(row, dict):
                    phone = mask_phone_number(row['phone_number']) if use_mask else row['phone_number']
                    record_type = row.get('record_type', 'tenant')
                    writer.writerow([phone, row['reply'], record_type, row['timestamp']])
                else:
                    phone = mask_phone_number(row['phone_number']) if use_mask else row['phone_number']
                    record_type = row.get('record_type', 'tenant') if hasattr(row, 'get') else 'tenant'
                    writer.writerow([phone, row['reply'], record_type, row['timestamp']])
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = f"attachment; filename=payment_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output.headers["Content-type"] = "text/csv"
            logger.info(f"CSV export completed: {len(rows)} records")
            return output
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            flash('Error exporting data.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
    return inner_export_csv()

# ==================== Test Data Route (Development Only) ====================
@dashboard_bp.route('/add-test-data')
def add_test_data():
    """Add test SMS messages to database for testing (development only)."""
    try:
        from app_local import get_db_connection, logger, login_required
    except ImportError:
        return redirect(url_for('dashboard.dashboard'))
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


# ==================== Update Records to Landlord Route ====================
@dashboard_bp.route('/update-to-landlord', methods=['POST'])
def update_to_landlord():
    """Update all existing records to have record_type = 'landlord' (admin only)."""
    # Lazy import to avoid circular dependencies
    try:
        from app import login_required, logger
    except ImportError:
        try:
            from app_local import login_required, logger
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
            def login_required(f):
                return f
    
    @login_required
    def inner_update_to_landlord():
        try:
            import os
            DATABASE_URL = os.getenv('DATABASE_URL')
            conn = db_service.get_db_connection()
            
            if DATABASE_URL:
                # PostgreSQL
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Count records to update
                cursor.execute("SELECT COUNT(*) as count FROM rent_records WHERE record_type IS NULL OR record_type = 'tenant'")
                count_result = cursor.fetchone()
                count_to_update = count_result['count'] if count_result else 0
                
                if count_to_update > 0:
                    cursor.execute("UPDATE rent_records SET record_type = 'landlord' WHERE record_type IS NULL OR record_type = 'tenant'")
                    conn.commit()
                    flash(f'Successfully updated {count_to_update} record(s) to "landlord"!', 'success')
                    logger.info(f"Updated {count_to_update} records to landlord")
                else:
                    flash('No records to update (all records are already "landlord")', 'info')
                
            else:
                # SQLite
                cursor = conn.cursor()
                
                # Check if record_type column exists
                cursor.execute("PRAGMA table_info(rent_records)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'record_type' not in columns:
                    cursor.execute("ALTER TABLE rent_records ADD COLUMN record_type TEXT DEFAULT 'tenant'")
                    conn.commit()
                
                # Count records to update
                cursor.execute("SELECT COUNT(*) FROM rent_records WHERE record_type IS NULL OR record_type = 'tenant'")
                count_to_update = cursor.fetchone()[0]
                
                if count_to_update > 0:
                    cursor.execute("UPDATE rent_records SET record_type = 'landlord' WHERE record_type IS NULL OR record_type = 'tenant'")
                    conn.commit()
                    flash(f'Successfully updated {count_to_update} record(s) to "landlord"!', 'success')
                    logger.info(f"Updated {count_to_update} records to landlord")
                else:
                    flash('No records to update (all records are already "landlord")', 'info')
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating records: {e}")
            flash('Error updating records. Please try again.', 'danger')
        
        return redirect(url_for('dashboard.dashboard'))
    
    return inner_update_to_landlord()
