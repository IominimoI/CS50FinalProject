print("Starting Password Manager...")

import customtkinter as ctk
from pmg import PasswordManager
import pyperclip
import sqlite3
from login_window import LoginWindow
from database import initialize_database
from config import DB_PATH

class PasswordManagerGUI:
    def __init__(self, user_id, password):
        self.user_id = user_id
        self.pm = PasswordManager(password)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk()
        self.window.title("Secure Password Manager & Generator")
        self.window.geometry("920x600")

        # Logout button in header
        self.header_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=(5,0))
        self.logout_btn = ctk.CTkButton(
            self.header_frame,
            text="Logout",
            command=self._logout,
            width=70,
            height=20
        )
        self.logout_btn.pack(side="right", padx=10, pady=5)

        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(padx=20, pady=(0,20), fill="both", expand=True)
        
        self.tab_generate = self.tabview.add("Generate Password")
        self.tab_store = self.tabview.add("Store Login")
        self.tab_retrieve = self.tabview.add("Search Login")
        self.tab_browse = self.tabview.add("Browse Login")
        self.tab_check = self.tabview.add("Check Password")
        
        self._setup_generate_tab()
        self._setup_store_tab()
        self._setup_retrieve_tab()
        self._setup_check_tab()
        self._setup_browse_tab()

    def _setup_check_tab(self):
        self.check_password_label = ctk.CTkLabel(self.tab_check, text="Enter Password to Check:")
        self.check_password_label.pack(pady=5)
        
        self.check_password_entry = ctk.CTkEntry(self.tab_check, width=300)
        self.check_password_entry.pack(pady=5)
        
        self.check_btn = ctk.CTkButton(
            self.tab_check,
            text="Check Strength",
            command=self._check_password_strength
        )
        self.check_btn.pack(pady=20)
        
        self.check_result = ctk.CTkLabel(self.tab_check, text="")
        self.check_result.pack(pady=10)

    def _check_password_strength(self):
        password = self.check_password_entry.get()
        if password:
            strength = self.pm.check_password_strength(password)
            self.check_result.configure(text=f"Password Strength: {strength}")

    def _setup_generate_tab(self):
        self.length_label = ctk.CTkLabel(self.tab_generate, text="Password Length: 16")
        self.length_label.pack(pady=10)
        
        self.length_slider = ctk.CTkSlider(self.tab_generate, from_=8, to=32, number_of_steps=24, command=self._update_length_label)
        self.length_slider.pack(pady=10)
        self.length_slider.set(16)
        
        self.complexity_label = ctk.CTkLabel(self.tab_generate, text="Password Complexity: Complex")
        self.complexity_label.pack(pady=10)
        
        self.complexity_slider = ctk.CTkSlider(self.tab_generate, from_=1, to=3, number_of_steps=2, command=self._update_complexity_label)
        self.complexity_slider.pack(pady=10)
        self.complexity_slider.set(3)
        
        self.generate_btn = ctk.CTkButton(
            self.tab_generate, 
            text="Generate Password", 
            command=self._generate_password
        )
        self.generate_btn.pack(pady=20)
        
        self.password_display = ctk.CTkTextbox(self.tab_generate, height=100)
        self.password_display.pack(pady=20, padx=20, fill="x")
        
        self.strength_label = ctk.CTkLabel(self.tab_generate, text="Password Strength: ")
        self.strength_label.pack(pady=10)
        
        self.copy_btn = ctk.CTkButton(
            self.tab_generate, 
            text="Copy to Clipboard", 
            command=self._copy_to_clipboard
        )
        self.copy_btn.pack(pady=10)

    def _update_length_label(self, value):
        self.length_label.configure(text=f"Password Length: {int(value)}")

    def _update_complexity_label(self, value):
        complexity_text = {1: "Simple", 2: "Moderate", 3: "Complex"}
        self.complexity_label.configure(text=f"Password Complexity: {complexity_text[int(value)]}")

    def _generate_password(self):
        length = int(self.length_slider.get())
        complexity = int(self.complexity_slider.get())
        
        # Handle complexity levels
        password = self.pm.generate_password(length, complexity)
        strength = self.pm.check_password_strength(password)
        
        self.password_display.delete("1.0", "end")
        self.password_display.insert("1.0", password)
        self.strength_label.configure(text=f"Password Strength: {strength}")

    def _setup_store_tab(self):
        self.website_label = ctk.CTkLabel(self.tab_store, text="Website:")
        self.website_label.pack(pady=5)
        self.website_entry = ctk.CTkEntry(self.tab_store, width=300)
        self.website_entry.pack(pady=5)
        
        self.username_label = ctk.CTkLabel(self.tab_store, text="Username:")
        self.username_label.pack(pady=5)
        self.username_entry = ctk.CTkEntry(self.tab_store, width=300)
        self.username_entry.pack(pady=5)
        
        self.password_label = ctk.CTkLabel(self.tab_store, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.tab_store, width=300, show="*")
        self.password_entry.pack(pady=5)
        
        self.save_btn = ctk.CTkButton(
            self.tab_store, 
            text="Save Login", 
            command=self._save_login
        )
        self.save_btn.pack(pady=20)

    def _setup_retrieve_tab(self):
        self.retrieve_website_label = ctk.CTkLabel(self.tab_retrieve, text="Website:")
        self.retrieve_website_label.pack(pady=5)
        self.retrieve_website_entry = ctk.CTkEntry(self.tab_retrieve, width=300)
        self.retrieve_website_entry.pack(pady=5)
        
        self.retrieve_btn = ctk.CTkButton(
            self.tab_retrieve, 
            text="Retrieve Login", 
            command=self._retrieve_login
        )
        self.retrieve_btn.pack(pady=20)
        
        self.results_display = ctk.CTkTextbox(self.tab_retrieve, height=150)
        self.results_display.pack(pady=20, padx=20, fill="x")
    
    def _setup_browse_tab(self):
        # Create frame for the list
        self.browse_frame = ctk.CTkFrame(self.tab_browse)
        self.browse_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create scrollable frame
        self.browse_list = ctk.CTkScrollableFrame(self.browse_frame)
        self.browse_list.pack(fill="both", expand=True)
        
        # Add refresh button
        self.refresh_btn = ctk.CTkButton(
            self.tab_browse,
            text="Refresh List",
            command=self._refresh_browse_list
        )
        self.refresh_btn.pack(pady=10)

    def _refresh_browse_list(self):
        # Clear existing widgets
        for widget in self.browse_list.winfo_children():
            widget.destroy()
        
        try:
            # Get all logins for current user
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT id, website, encrypted_username FROM passwords WHERE user_id=?', (self.user_id,))
            logins = c.fetchall()
            conn.close()
            
            # Create buttons for each login
            for login_id, website, username in logins:
                login_frame = ctk.CTkFrame(self.browse_list)
                login_frame.pack(fill="x", padx=5, pady=2)
                
                website_label = ctk.CTkLabel(login_frame, text=f"Website: {website}")
                website_label.pack(side="left", padx=5)
                
                show_btn = ctk.CTkButton(
                    login_frame,
                    text="Show Details",
                    command=lambda id=login_id: self._show_login_details(id)
                )
                show_btn.pack(side="right", padx=5)
                
        except sqlite3.OperationalError:
            error_label = ctk.CTkLabel(
                self.browse_list,
                text="Database Error: The database structure appears to be corrupted.\nPlease restore from backup.",
                text_color="red"
            )
            error_label.pack(pady=20)
            
    def _show_login_details(self, login_id):
        website, username, password = self.pm.get_login_by_id(login_id)

        if website:
            popup = ctk.CTkToplevel()
            popup.title("Login Details")
            popup.geometry("400x300")
        
            # Center the popup relative to main window
            popup.withdraw()  # Hide window initially
            popup.update()  # Update window size
        
            # Calculate center position
            x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (popup.winfo_height() // 2)
        
            # Set position and show window
            popup.geometry(f"+{x//2}+{y//2}")
            popup.deiconify()  # Show window

            # Website section
            website_frame = ctk.CTkFrame(popup)
            website_frame.pack(pady=10, fill="x", padx=20)
            ctk.CTkLabel(website_frame, text=f"Website: {website}").pack(side="left")
            ctk.CTkButton(website_frame, text="Copy", 
                 command=lambda: pyperclip.copy(website)).pack(side="right")
    
            # Username section
            username_frame = ctk.CTkFrame(popup)
            username_frame.pack(pady=10, fill="x", padx=20)
            ctk.CTkLabel(username_frame, text=f"Username: {username}").pack(side="left")
            ctk.CTkButton(username_frame, text="Copy", 
                 command=lambda: pyperclip.copy(username)).pack(side="right")
    
            # Password section
            password_frame = ctk.CTkFrame(popup)
            password_frame.pack(pady=10, fill="x", padx=20)
    
            password_var = ctk.StringVar(value="********")
            ctk.CTkLabel(password_frame, text="Password: ").pack(side="left")
            password_label = ctk.CTkLabel(password_frame, textvariable=password_var)
            password_label.pack(side="left")
    
            def toggle_password():
                if password_var.get() == "********":
                    password_var.set(password)
                else:
                    password_var.set("********")
    
            ctk.CTkButton(password_frame, text="Copy", 
                 command=lambda: pyperclip.copy(password)).pack(side="right")
            ctk.CTkButton(password_frame, text="👁", 
                 command=toggle_password,
                 width=30).pack(side="right", padx=5)

    def _generate_password(self):
        length = int(self.length_slider.get())
        complexity = int(self.complexity_slider.get())
        password = self.pm.generate_password(length, complexity)
        strength = self.pm.check_password_strength(password)
        
        self.password_display.delete("1.0", "end")
        self.password_display.insert("1.0", password)
        self.strength_label.configure(text=f"Password Strength: {strength}")

    def _copy_to_clipboard(self):
        password = self.password_display.get("1.0", "end-1c")
        pyperclip.copy(password)

    def _save_login(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if website and username and password:
            self.pm.save_login(self.user_id, website, username, password)
            self.website_entry.delete(0, "end")
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")

    def _retrieve_login(self):
        website = self.retrieve_website_entry.get()
        username, password = self.pm.get_login(self.user_id, website)
        
        self.results_display.delete("1.0", "end")
        if username:
            self.results_display.insert("1.0", f"Username: {username}\nPassword: {password}")
        else:
            self.results_display.insert("1.0", "No login found for this website.")

    def run(self):
        self.window.mainloop()

    def _logout(self):
        self.window.destroy()  # Close the current window
        initialize_database()   # Reset database connection
        login = LoginWindow()   # Create new login window
        user_id, password = login.run()
        if user_id:
            app = PasswordManagerGUI(user_id, password)
            app.run()

if __name__ == "__main__":
    initialize_database() 
    
    login = LoginWindow()
    user_id, password = login.run()
    
    # Only launch main app if login is successful
    if user_id:
        app = PasswordManagerGUI(user_id, password)
        app.run()
