import os
import sqlite3

def initialize_database():
    # Check if database exists
    if not os.path.exists('password_manager.db'):
        conn = sqlite3.connect('password_manager.db')
        c = conn.cursor()
        
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
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()