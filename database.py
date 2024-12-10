"""
Copyright (c) 2024 [Nico Geromin]
Licensed under the MIT License - see LICENSE file for details
"""
import os
import sqlite3
from config import DB_PATH, BASE_DIR

def initialize_database():
    os.makedirs(BASE_DIR, mode=0o700, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if tables exist
    c.execute('''SELECT count(name) FROM sqlite_master 
                 WHERE type='table' AND (name='users' OR name='passwords')''')
    
    if c.fetchone()[0] < 2:  # If both tables don't exist
        # Create tables
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        
        c.execute('''
            CREATE TABLE passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                website TEXT NOT NULL,
                encrypted_username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
    conn.close()