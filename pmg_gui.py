"""
Copyright (c) 2024 [Nico Geromin]
Licensed under the MIT License - see LICENSE file for details
"""
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
        self.window.withdraw()  # Hide window during setup
        self.window.iconbitmap("")
        self.window.title("Secure Password Manager & Generator")
        
        # Set initial size
        window_width = 1000
        window_height = 600
        
        # Center the window on the screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Now make the window visible again
        self.window.deiconify()
        self.window.title("Secure Password Manager & Generator")
        self.window.geometry("1000x600")

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
        
        self.check_password_entry.bind('<KeyRelease>', self._check_password_strength_realtime)
        
        self.check_result = ctk.CTkLabel(self.tab_check, text="")
        self.check_result.pack(pady=10)

    def _check_password_strength_realtime(self, event):
        password = self.check_password_entry.get()
        if password:
            strength = self.pm.check_password_strength(password)
            self.check_result.configure(text=f"Password Strength: {strength}", wraplength=800, justify="center")
        else:
            self.check_result.configure(text="")

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
        
        self.strength_label = ctk.CTkLabel(self.tab_generate, text="Password Strength: ", wraplength=800, justify="center")
        self.strength_label.pack(pady=5, padx=10, fill="x")
        
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
        
        password = self.pm.generate_password(length, complexity)
        strength = self.pm.check_password_strength(password)
        
        self.password_display.delete("1.0", "end")
        self.password_display.insert("1.0", password)
        self.strength_label.configure(text=f"Password Strength: {strength}", wraplength=800)

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
        self.browse_frame = ctk.CTkFrame(self.tab_browse)
        self.browse_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.browse_list = ctk.CTkScrollableFrame(self.browse_frame)
        self.browse_list.pack(fill="both", expand=True)
        
        self.refresh_btn = ctk.CTkButton(
            self.tab_browse,
            text="Refresh List",
            command=self._refresh_browse_list
        )
        self.refresh_btn.pack(pady=10)

    def _refresh_browse_list(self):
        for widget in self.browse_list.winfo_children():
            widget.destroy()
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT id, website, encrypted_username FROM passwords WHERE user_id=?', (self.user_id,))
            logins = c.fetchall()
            conn.close()
            
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
        try:
            website, username, password = self.pm.get_login_by_id(login_id)
        
            if not website:
                return
        
            popup = ctk.CTkToplevel(self.window)
            popup.title("Login Details")
            popup.geometry("400x350")
            popup.withdraw()
        
            main_frame = ctk.CTkFrame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
            title_label = ctk.CTkLabel(
                main_frame, 
                text=f"Details for {website}", 
                font=("Arial", 16, "bold")
            )
            title_label.pack(pady=(15, 20))
        
            # Website info
            website_frame = ctk.CTkFrame(main_frame)
            website_frame.pack(fill="x", padx=15, pady=5)
        
            website_label = ctk.CTkLabel(website_frame, text=f"Website:", width=80, anchor="w")
            website_label.pack(side="left", padx=5, pady=8)
        
            website_value = ctk.CTkLabel(website_frame, text=website, anchor="w")
            website_value.pack(side="left", fill="x", expand=True, padx=5)
        
            website_copy = ctk.CTkButton(
                website_frame, 
                text="Copy", 
                width=60,
                command=lambda: pyperclip.copy(website)
            )
            website_copy.pack(side="right", padx=5)
        
            # Username info
            username_frame = ctk.CTkFrame(main_frame)
            username_frame.pack(fill="x", padx=15, pady=5)
        
            username_label = ctk.CTkLabel(username_frame, text=f"Username:", width=80, anchor="w")
            username_label.pack(side="left", padx=5, pady=8)
        
            username_value = ctk.CTkLabel(username_frame, text=username, anchor="w")
            username_value.pack(side="left", fill="x", expand=True, padx=5)
        
            username_copy = ctk.CTkButton(
                username_frame, 
                text="Copy", 
                width=60,
                command=lambda: pyperclip.copy(username)
            )
            username_copy.pack(side="right", padx=5)
        
            # Password info
            password_frame = ctk.CTkFrame(main_frame)
            password_frame.pack(fill="x", padx=15, pady=5)
        
            password_label = ctk.CTkLabel(password_frame, text=f"Password:", width=80, anchor="w")
            password_label.pack(side="left", padx=5, pady=8)
        
            password_var = ctk.StringVar(value="••••••••")
            password_value = ctk.CTkLabel(password_frame, textvariable=password_var, anchor="w")
            password_value.pack(side="left", fill="x", expand=True, padx=5)
        
            def toggle_password():
                current = password_var.get()
                if current == "••••••••":
                    password_var.set(password)
                else:
                    password_var.set("••••••••")
        
            password_toggle = ctk.CTkButton(
                password_frame, 
                text="👁", 
                width=30,
                command=toggle_password
            )
            password_toggle.pack(side="right", padx=5)
        
            password_copy = ctk.CTkButton(
                password_frame, 
                text="Copy", 
                width=60,
                command=lambda: pyperclip.copy(password)
            )
            password_copy.pack(side="right", padx=5)
        
            # Delete button
            delete_frame = ctk.CTkFrame(main_frame)
            delete_frame.pack(fill="x", padx=15, pady=(20, 5))
        
            def delete_login():
                try:
                    self.pm.delete_login(login_id)
                    popup.destroy()
                    self._refresh_browse_list()
                except Exception as e:
                    print(f"Error deleting login: {e}")
        
            delete_btn = ctk.CTkButton(
                delete_frame,
                text="Delete Login",
                fg_color="#c75d5d",
                hover_color="#aa4a4a",
                command=delete_login
            )
            delete_btn.pack(fill="x")
        
            # Force window to be drawn first, then add grab functionality later
            popup.update_idletasks()
        
            # Position the window in the center of the screen BEFORE showing it
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - 400) // 2  # Using hardcoded width since window isn't visible yet
            y = (screen_height - 350) // 2  # Using hardcoded height
            popup.geometry(f"+{x}+{y}")
        
            # Now make the window visible at the correct position
            popup.deiconify()
        
            # NOW we can make it modal and grab focus
            popup.transient(self.window)
            popup.focus_force()
            popup.grab_set()
        
        except Exception as e:
            print(f"Error in _show_login_details: {str(e)}")
            import traceback
            traceback.print_exc()

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
        self.window.destroy() 
        initialize_database()
        login = LoginWindow()
        user_id, password = login.run()
        if user_id:
            app = PasswordManagerGUI(user_id, password)
            app.run()

import sys
import os
import subprocess

if __name__ == "__main__":
    # Check for --daemon flag
    if "--daemon" in sys.argv:
        # Relaunch the script in the background with no additional arguments
        # Just use the Python interpreter and script name
        cmd = [sys.executable, sys.argv[0]]
        
        subprocess.Popen(cmd, 
                        stdout=open(os.devnull, 'w'),
                        stderr=open(os.devnull, 'w'), 
                        start_new_session=True)
        print("Password Manager started in background")
        sys.exit(0)
    
    # Normal startup code
    initialize_database() 
    login = LoginWindow()
    user_id, password = login.run()
    if user_id:
        app = PasswordManagerGUI(user_id, password)
        app.run()
