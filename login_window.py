import customtkinter as ctk
import hashlib
import sqlite3

class LoginWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Login")
        self.window.geometry("400x300")
        
        self.username_label = ctk.CTkLabel(self.window, text="Username:")
        self.username_label.pack(pady=5)
        self.username_entry = ctk.CTkEntry(self.window, width=200)
        self.username_entry.pack(pady=5)
        
        self.password_label = ctk.CTkLabel(self.window, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.window, width=200, show="*")
        self.password_entry.pack(pady=5)
        
        self.login_btn = ctk.CTkButton(self.window, text="Login", command=self._login)
        self.login_btn.pack(pady=10)
        
        self.register_btn = ctk.CTkButton(self.window, text="Register", command=self._register)
        self.register_btn.pack(pady=10)
        
        self.message_label = ctk.CTkLabel(self.window, text="")
        self.message_label.pack(pady=10)
        
        self.user_id = None
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _login(self):
        username = self.username_entry.get()
        password = self._hash_password(self.password_entry.get())
        
        conn = sqlite3.connect('password_manager.db')
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
        
        conn = sqlite3.connect('password_manager.db')
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
