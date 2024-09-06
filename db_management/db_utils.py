# db_utils.py
from flask import g
import sqlite3
from db_management.db_manager import DatabaseManager


def get_db_manager():
    # Create a DatabaseManager instance for the request if it doesn't exist yet
    if 'db_manager' not in g:
        g.db_manager = DatabaseManager('example.db')
        g.db_manager.conn = sqlite3.connect(g.db_manager.db_path)
        g.db_manager.cursor = g.db_manager.conn.cursor()
    return g.db_manager


def close_db_manager(exception=None):
    # Close the DatabaseManager instance at the end of the request
    db_manager = g.pop('db_manager', None)
    if db_manager:
        db_manager.conn.close()
