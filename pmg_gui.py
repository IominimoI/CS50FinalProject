print("Starting Password Manager...")

import customtkinter as ctk
from pmg import PasswordManager
import pyperclip

class PasswordManagerGUI:
    def __init__(self):
        self.pm = PasswordManager()
        self.pm.load_passwords()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk()
        self.window.title("Secure Password Manager")
        self.window.geometry("800x600")
        
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.tab_generate = self.tabview.add("Generate Password")
        self.tab_store = self.tabview.add("Store Login")
        self.tab_retrieve = self.tabview.add("Retrieve Login")
        self.tab_check = self.tabview.add("Check Password")
        
        self._setup_generate_tab()
        self._setup_store_tab()
        self._setup_retrieve_tab()
        self._setup_check_tab()

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
        
        # Modify your PasswordManager to handle complexity levels
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
            self.pm.save_login(website, username, password)
            self.website_entry.delete(0, "end")
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")

    def _retrieve_login(self):
        website = self.retrieve_website_entry.get()
        username, password = self.pm.get_login(website)
        
        self.results_display.delete("1.0", "end")
        if username:
            self.results_display.insert("1.0", f"Username: {username}\nPassword Hash: {password}")
        else:
            self.results_display.insert("1.0", "No login found for this website.")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PasswordManagerGUI()
    app.run()
