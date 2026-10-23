import sqlite3
from flask import current_app, g

# =====================================================================
# 1. DATABASE LIFECYCLE MANAGEMENT
# =====================================================================
def get_db():
    """
    Data Access Layer: Establishes or retrieves a thread-safe database 
    connection bound to the active application lifecycle context.
    """
    if "db" not in g:
        db_file = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_file)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """
    Data Access Layer: Cleanly releases the database connection back 
    to the system when the request lifecycle tears down.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


# =====================================================================
# 2. SCHEMA INITIALIZATION ROUTINE
# =====================================================================
def init_db(app):
    """
    Data Access Layer: One-off synchronization routine that connects directly 
    to the configured path and establishes the base database schema.
    """
    db_file = app.config["DATABASE"]
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Establish the users table schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        );
    """)
    
    # Establish the recipes table schema with explicit owner tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT,
            is_public INTEGER NOT NULL DEFAULT 1,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    
    conn.commit()
    conn.close()


# =====================================================================
# 3. RESOURCE SCALAR DATA QUERIES
# =====================================================================
def get_recipe_count(conn):
    """
    Data Access Layer: Executes a scalar count query against the recipes table 
    and returns the total number of records as an integer.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recipes")
    row = cursor.fetchone()
    return row[0] if row else 0
