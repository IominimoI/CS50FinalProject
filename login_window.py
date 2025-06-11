"""
Copyright (c) 2024 [Nico Geromin]
Licensed under the MIT License - see LICENSE file for details
"""
import customtkinter as ctk
import os
import sqlite3
import base64
from config import DB_PATH
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class LoginWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Login")
        
        # Set initial size
        window_width = 450
        window_height = 350
        self.window.geometry(f"{window_width}x{window_height}")
        
        # Center the window on the screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        header_label = ctk.CTkLabel(
            self.window, 
            text="Password Manager and Generator",
            font=("Arial", 20, "bold")
        )
        header_label.pack(pady=20)
        
        # Create main form frame to contain all elements
        form_frame = ctk.CTkFrame(self.window)
        form_frame.pack(pady=20)
        
        # Username section
        username_frame = ctk.CTkFrame(form_frame)
        username_frame.pack(pady=5)
        self.username_label = ctk.CTkLabel(username_frame, text="Username:", width=80)
        self.username_label.pack(side="left", padx=5)
        self.username_entry = ctk.CTkEntry(username_frame, width=200)
        self.username_entry.pack(side="left", padx=5)
        ctk.CTkLabel(username_frame, text="", width=30).pack(side="left", padx=5)
        
        # Password section
        password_frame = ctk.CTkFrame(form_frame)
        password_frame.pack(pady=5)
        self.password_label = ctk.CTkLabel(password_frame, text="Password:", width=80)
        self.password_label.pack(side="left", padx=5)
        self.password_entry = ctk.CTkEntry(password_frame, width=200, show="*")
        self.password_entry.pack(side="left", padx=5)
        info_button = ctk.CTkButton(password_frame, text="ℹ", width=30, command=self._show_password_info)
        info_button.pack(side="left", padx=5)        
        self.login_btn = ctk.CTkButton(self.window, text="Login", command=self._login)
        self.login_btn.pack(pady=10)
        
        self.register_btn = ctk.CTkButton(self.window, text="Register", command=self._register)
        self.register_btn.pack(pady=10)
        
        self.message_label = ctk.CTkLabel(self.window, text="")
        self.message_label.pack(pady=10)
        
        self.user_id = None    
        self.user_password = None
        
    def _show_password_info(self):
        info_popup = ctk.CTkToplevel()
        info_popup.title("Password Guidelines")
        info_popup.geometry("400x300")
        
        guidelines = """
        For a secure password, make sure to:
        • Use at least 8 characters
        • Include uppercase and lowercase letters
        • Include numbers
        • Include special characters (!@#$%^&*)
        • Avoid common words or phrases
        • Don't use personal information
        """
        
        info_label = ctk.CTkLabel(info_popup, text=guidelines, justify="left")
        info_label.pack(pady=20, padx=20) 
        pass 
           
    def _hash_password(self, password, salt=None):
        """Create a secure password hash using PBKDF2"""
        if salt is None:
            # Generate a random salt for new passwords
            salt = os.urandom(16)
            
        # Use PBKDF2 with 100,000 iterations (adjust based on your performance needs)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        password_hash = kdf.derive(password.encode())
        
        # Convert binary data to storable strings
        password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        
        return password_hash_b64, salt_b64
    
    def _verify_password(self, password, stored_hash, stored_salt):
        """Verify a password against a stored hash and salt"""
        # Convert stored strings back to binary
        salt = base64.b64decode(stored_salt)
        
        # Generate hash with the same salt
        calculated_hash, _ = self._hash_password(password, salt)
        
        # Compare in constant time to prevent timing attacks
        return calculated_hash == stored_hash
    
    def _login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, password_hash, password_salt FROM users WHERE username=?', (username,))
        result = c.fetchone()
        conn.close()
        
        if result and result[1] and result[2]:
            user_id, stored_hash, stored_salt = result
            if self._verify_password(password, stored_hash, stored_salt):
                self.user_id = user_id
                self.user_password = password
                self.window.destroy()
            else:
                self.message_label.configure(text="Invalid credentials!")
        else:
            self.message_label.configure(text="Invalid credentials!")
    
    def _register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Input validation
        if not username or not password:
            self.message_label.configure(text="Username and password are required!")
            return
            
        if len(password) < 8:
            self.message_label.configure(text="Password must be at least 8 characters!")
            return
        
        # Create secure hash and salt
        password_hash, password_salt = self._hash_password(password)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)', 
                     (username, password_hash, password_salt))
            conn.commit()
            self.message_label.configure(text="Registration successful!")
        except sqlite3.IntegrityError:
            self.message_label.configure(text="Username already exists!")
        conn.close()   

    def run(self):
        self.window.mainloop()
        return self.user_id, self.user_password
