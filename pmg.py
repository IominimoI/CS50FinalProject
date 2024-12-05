
import hashlib
import random
import string
import json
import os
from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self):
        self.passwords = {}
        self.key_file = 'encryption_key.key'
        self.data_file = 'passwords.json'
        self._init_encryption()

    def _init_encryption(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
        else:
            with open(self.key_file, 'rb') as key_file:
                key = key_file.read()
        self.fernet = Fernet(key)

    def generate_password(self, length=16, complexity=3):
        if complexity == 1:
            # Simple - Word-based password
            words = ['cat', 'dog', 'bird', 'fish', 'lion', 'bear', 'wolf', 'deer', 
                    'book', 'desk', 'lamp', 'tree', 'sun', 'moon', 'star', 'cloud', 
                    'chair', 'car', 'bicycle', 'pot', 'lid', 'door', 'window', 'broom']
            # Pick 2-3 words and add some numbers
            num_words = min(3, length // 4)  # Ensure we don't exceed desired length
            password = ''.join(random.choice(words).capitalize() for _ in range(num_words))
            password += str(random.randint(100, 999))
            return password[:length]
            
        elif complexity == 2:
            # Moderate - Letters + numbers + basic symbols
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = []
            # Ensure one uppercase, one lowercase, one number, one symbol
            password.append(random.choice(string.ascii_uppercase))
            password.append(random.choice(string.ascii_lowercase))
            password.append(random.choice(string.digits))
            password.append(random.choice("!@#$%"))
            # Fill remaining length
            password.extend(random.choice(chars) for _ in range(length-4))
            return ''.join(random.sample(password, len(password)))
            
        else:
            # Complex - Full character set
            chars = string.ascii_letters + string.digits + string.punctuation
            return ''.join(random.choice(chars) for _ in range(length))
        
    def check_password_strength(self, password):
        score = 0
        
        # Length checks
        if len(password) < 4:
            return "Very Weak"
        elif len(password) <= 8:
            score += 1
        elif len(password) <= 13:
            score += 2
        else:
            score += 3
            
        # Character type checks
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in string.punctuation for c in password):
            score += 1
            
        return {
            0: "Very Weak",
            1: "Weak", 
            2: "Moderate",
            3: "Strong",
            4: "Very Strong",
            5: "Excellent",
            6: "Excellent",
            7: "Excellent"
        }[score]
    def save_login(self, website, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        encrypted_data = self.fernet.encrypt(
            json.dumps({
                'username': username,
                'password': hashed_password
            }).encode()
        )
        self.passwords[website] = encrypted_data.decode()
        self._save_to_file()

    def get_login(self, website):
        if website in self.passwords:
            encrypted_data = self.passwords[website].encode()
            decrypted_data = json.loads(self.fernet.decrypt(encrypted_data))
            return decrypted_data['username'], decrypted_data['password']
        return None, None

    def _save_to_file(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.passwords, f)

    def load_passwords(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.passwords = json.load(f)

# Example usage:
if __name__ == "__main__":
    pm = PasswordManager()
    pm.load_passwords()
    
    # Generate a new password
    new_password = pm.generate_password()
    print(f"Generated password: {new_password}")
    print(f"Password strength: {pm.check_password_strength(new_password)}")
    
    # Save a login
    pm.save_login("example.com", "user@example.com", new_password)
    
    # Retrieve a login
    username, password = pm.get_login("example.com")
    if username:
        print(f"Retrieved credentials for example.com:")
        print(f"Username: {username}")
        print(f"Password hash: {password}")
