import customtkinter as ctk
import hashlib
import sqlite3
from config import DB_PATH

class LoginWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Login")
        self.window.geometry("450x350")

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
        # Add invisible placeholder with same width as info button
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
           
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _login(self):
        username = self.username_entry.get()
        password = self._hash_password(self.password_entry.get())
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=? AND password_hash=?', (username, password))
        result = c.fetchone()
        conn.close()
        
        if result:
            self.user_id = result[0]
            self.window.destroy()
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
        
        password_hash = self._hash_password(password)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            conn.commit()
            self.message_label.configure(text="Registration successful!")
        except sqlite3.IntegrityError:
            self.message_label.configure(text="Username already exists!")
        conn.close()   

    def run(self):
        self.window.mainloop()
        return self.user_id
