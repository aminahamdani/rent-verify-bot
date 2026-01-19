"""
DB Service - Database Interaction Logic
Supports both PostgreSQL (production) and SQLite (local development)
"""
import os
import sqlite3
import logging
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:  # psycopg2 may be unavailable in local dev (e.g., Python 3.14)
    psycopg2 = None
    RealDictCursor = None

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Get database connection.
    Uses PostgreSQL if DATABASE_URL is set, otherwise SQLite for local development.
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if DATABASE_URL:
        # PostgreSQL (production)
        if psycopg2 is None:
            raise ModuleNotFoundError(
                "psycopg2 is required for PostgreSQL mode but is not installed. "
                "Unset DATABASE_URL for SQLite local dev, or install psycopg2-binary on a supported Python version."
            )
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            raise
    else:
        # SQLite (local development)
        DB_PATH = os.path.join(os.path.dirname(__file__), '../instance/rent_data.db')
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def close_db_connection(conn):
    """Close database connection."""
    if conn:
        conn.close()

def execute_query(query, params=None, fetch=False):
    """
    Execute a database query with automatic parameter style detection.
    Returns cursor for PostgreSQL, or executes and returns results for SQLite.
    """
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = get_db_connection()
    
    try:
        if DATABASE_URL:
            # PostgreSQL - use %s placeholders
            cursor = conn.cursor(cursor_factory=RealDictCursor)  # type: ignore[arg-type]
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                results = cursor.fetchall()
                conn.commit()
                cursor.close()
                conn.close()
                return results
            else:
                conn.commit()
                cursor.close()
                conn.close()
                return None
        else:
            # SQLite - use ? placeholders
            if params:
                # Convert %s to ? for SQLite
                query = query.replace('%s', '?')
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                results = cursor.fetchall()
                conn.commit()
                conn.close()
                return results
            else:
                conn.commit()
                conn.close()
                return None
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise
