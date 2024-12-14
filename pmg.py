"""
Copyright (c) 2024 [Nico Geromin]
Licensed under the MIT License - see LICENSE file for details
"""
import hashlib
import random
import string
import os
import sqlite3
import stat
import nltk
import base64
from config import DB_PATH, KEY_PATH, BASE_DIR
from nltk.corpus import words
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class PasswordManager:
    def __init__(self, user_password):
        self.db_path = DB_PATH
        self.key_file = KEY_PATH
        os.makedirs(os.path.dirname(self.db_path), mode=0o700, exist_ok=True)
        self._init_encryption(user_password)
        self._secure_files()
        if not self.verify_database_integrity():
            raise Exception("Database integrity check failed. Please ensure the database is not corrupted.")
        try:
            nltk.data.find('corpora/words')
        except LookupError:
            nltk.download('words')
        self.passwords = {}
        self.word_list = words.words()

    def _derive_key(self, password, salt=None):
        if  salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
        
    def _init_encryption(self, user_password):
        if not os.path.exists(self.key_file):
            key, salt = self._derive_key(user_password)
            self.fernet = Fernet(key)
            with open(self.key_file, 'wb') as key_file:
                key_file.write(salt)  # Store only the salt
        else:
            with open(self.key_file, 'rb') as key_file:
                salt = key_file.read()
                key, _ = self._derive_key(user_password, salt)  # Recreate key using stored salt
                self.fernet = Fernet(key)

    def _secure_files(self):
        if os.path.exists(self.db_path):
            os.chmod(self.db_path, stat.S_IRUSR | stat.S_IWUSR)
            os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)

    def _verify_key(self, key):
        try:
            # Try to create a Fernet instance with the key
            Fernet(key)
            return True
        except Exception:
            return False

    def generate_password(self, length=16, complexity=3):
        if complexity == 1:
            filtered_words = [word for word in self.word_list if 4 <= len(word) <= 8]
            num_words = min(3, length // 4)
            password = ''.join(random.choice(filtered_words).capitalize() for _ in range(num_words))
            password += str(random.randint(100, 999))
            return password[:length]
            
        elif complexity == 2:
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = []
            password.append(random.choice(string.ascii_uppercase))
            password.append(random.choice(string.ascii_lowercase))
            password.append(random.choice(string.digits))
            password.append(random.choice("!@#$%"))
            password.extend(random.choice(chars) for _ in range(length-4))
            return ''.join(random.sample(password, len(password)))
            
        else:
            chars = string.ascii_letters + string.digits + string.punctuation
            return ''.join(random.choice(chars) for _ in range(length))
        
    def check_password_strength(self, password):
        score = 0
        feedback = []

        # Length scoring - more granular
        if len(password) < 8:
            return "Very Weak - Too Short"
        elif len(password) <= 10:
            score += 1
            feedback.append("Consider using a longer password")
        elif len(password) <= 12:
            score += 1.5
            feedback.append("Good length")
        elif len(password) <= 16:
            score += 2
            feedback.append("Very good length")
        else:
            score += 3
            feedback.append("Excellent length")

        # Character type scoring
        lowercase = sum(1 for c in password if c.islower())
        uppercase = sum(1 for c in password if c.isupper())
        digits = sum(1 for c in password if c.isdigit())
        special = sum(1 for c in password if c in string.punctuation)

        # Reward high counts of each type
        if lowercase >= 1: score += 0.5
        if lowercase >= 3: score += 0.5
        if uppercase >= 1: score += 0.5
        if uppercase >= 3: score += 0.5
        if digits >= 1: score += 0.5
        if digits >= 3: score += 0.5
        if digits <= 1: score -= 1.0
        if special >= 1: score += 1.0
        if special >= 3: score += 1.0

        # Add feedback for missing elements
        if not special:
            feedback.append("Add special characters for higher strength")
        if digits < 2:
            feedback.append("Add more numbers")
        if lowercase < 2:
            feedback.append("Add more lowercase letters")
        if uppercase < 2:
            feedback.append("Add more uppercase letters")

        # Character variety bonus
        char_variety = len(set(password)) / len(password)
        if char_variety > 0.8: 
            score += 1.5
            feedback.append("Excellent character variety")
        elif char_variety > 0.7:
            score += 1.0
        elif char_variety < 0.5:
            score -= 1
            feedback.append("Too many repeated characters")

        # Common patterns check
        common_patterns = ['123', '321', 'abc', 'cba', '!!!', '...', '###', 'Password', 
                          '123456', 'qwerty', 'password', 'p@ssword', '12345678']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 2
            feedback.append("Avoid common patterns")

        # Map final score to strength categories with proper recognition of exceptional passwords
        strength = {
            0: "Very Weak",
            1: "Weak",
            2: "Moderate",
            3: "Good",
            4: "Pretty Good",
            5: "Strong",
            6: "Very Strong",
            7: "Excellent"
        }[max(0, min(int(score), 7))]

        return f"{strength} - {'; '.join(feedback)}" if feedback else strength
      
    def save_login(self, user_id, website, username, password):
        if not self.verify_database_integrity():
            raise Exception("Database integrity check failed")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        encrypted_username = self.fernet.encrypt(username.encode()).decode()
        encrypted_password = self.fernet.encrypt(password.encode()).decode()
        c.execute(
            'INSERT INTO passwords (user_id, website, encrypted_username, password_hash, encrypted_password) VALUES (?, ?, ?, ?, ?)',
            (user_id, website, encrypted_username, self.hash_password(password), encrypted_password)
        )
        conn.commit()
        conn.close()
        self._secure_files()

    def get_login(self, user_id, website):
        if not self.verify_database_integrity():
            raise Exception("Database integrity check failed")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            'SELECT encrypted_username, encrypted_password FROM passwords WHERE user_id=? AND website=?',
            (user_id, website)
        )
        result = c.fetchone()
        conn.close()
        
        if result:
            encrypted_username, encrypted_password = result
            decrypted_password = self.fernet.decrypt(encrypted_password.encode()).decode()
            decrypted_username = self.fernet.decrypt(encrypted_username.encode()).decode()
            return decrypted_username, decrypted_password
        return None, None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def get_login_by_id(self, login_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT website, encrypted_username, encrypted_password FROM passwords WHERE id=?', (login_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            website, encrypted_username, encrypted_password = result
            decrypted_password = self.fernet.decrypt(encrypted_password.encode()).decode()
            decrypted_username = self.fernet.decrypt(encrypted_username.encode()).decode()
            return website, decrypted_username, decrypted_password
        return None, None, None

    def verify_database_integrity(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('PRAGMA integrity_check')
            result = c.fetchone()
            return result[0] == 'ok'
        finally:
            conn.close()

    def delete_login(self, login_id):
        if not self.verify_database_integrity():
            raise Exception("Database integrity check failed")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM passwords WHERE id=?', (login_id,))
        conn.commit()
        conn.close()
        self._secure_files()