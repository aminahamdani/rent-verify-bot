"""
DB Service - Database Interaction Logic
"""
import os
import sqlite3
import logging

def get_db_connection():
    """Get SQLite connection."""
    DB_PATH = os.path.join(os.path.dirname(__file__), '../instance/rent_data.db')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def close_db_connection(conn):
    if conn:
        conn.close()
