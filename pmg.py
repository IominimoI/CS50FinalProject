import hashlib
import random
import string
import os
import sqlite3
import stat
import nltk
from nltk.corpus import words
from cryptography.fernet import Fernet


class PasswordManager:
    def __init__(self):
        self.passwords = {}
        self.key_file = 'encryption_key.key'
        self._init_encryption()
        self._secure_database()
        if not self.verify_database_integrity():
            raise Exception("Database integrity check failed. Please ensure the database is not corrupted.")
        try:
            nltk.data.find('corpora/words')
        except LookupError:
            nltk.download('words')
        self.word_list = words.words()

    def _init_encryption(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
        else:
            with open(self.key_file, 'rb') as key_file:
                key = key_file.read()
        self.fernet = Fernet(key)

    def _secure_database(self):
        if os.path.exists('password_manager.db'):
            os.chmod('password_manager.db', stat.S_IRUSR | stat.S_IWUSR)

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
    
        if len(password) < 8:
            return "Very Weak - Too Short"
        elif len(password) <= 10:
            score += 1
            feedback.append("Consider using a longer password")
        elif len(password) <= 14:
            score += 2
            feedback.append("Good length")
        else:
            score += 3
            feedback.append("Excellent length")
    
        lowercase = sum(1 for c in password if c.islower())
        uppercase = sum(1 for c in password if c.isupper())
        digits = sum(1 for c in password if c.isdigit())
        special = sum(1 for c in password if c in string.punctuation)
    
        if lowercase >= 2: score += 1
        if uppercase >= 2: score += 1
        if digits >= 2: score += 1
        if special >= 1: score += 1
    
        if len(password) > 12 and (lowercase and uppercase and digits):
            score += 1
    
        char_variety = len(set(password)) / len(password)
        if char_variety < 0.7:
            score -= 1
            feedback.append("Too many repeated characters")
    
        common_patterns = ['123', '321', 'abc', 'cba', '!!!', '...', '###']
        for pattern in common_patterns:
            if pattern in password.lower():
                score -= 1
                feedback.append("Avoid common patterns")
                break
    
        if digits < 1 or special < 1:
            score = min(score, 2)
            if digits < 1: feedback.append("Add numbers for higher strength")
            if special < 1: feedback.append("Add special characters for higher strength")
    
        strength = {
            0: "Very Weak",
            1: "Weak",
            2: "Moderate",
            3: "Strong",
            4: "Strong",
            5: "Very Strong",
            6: "Excellent",
            7: "Excellent"
        }[max(0, min(score, 7))]
    
        return f"{strength} - {'; '.join(feedback)}" if feedback else strength  
      
    def save_login(self, user_id, website, username, password):
        if not self.verify_database_integrity():
            raise Exception("Database integrity check failed")
        
        conn = sqlite3.connect('password_manager.db')
        c = conn.cursor()
        encrypted_password = self.fernet.encrypt(password.encode()).decode()
        c.execute(
            'INSERT INTO passwords (user_id, website, username, password_hash, encrypted_password) VALUES (?, ?, ?, ?, ?)',
            (user_id, website, username, self.hash_password(password), encrypted_password)
        )
        conn.commit()
        conn.close()
        self._secure_database()

    def get_login(self, user_id, website):
        if not self.verify_database_integrity():
            raise Exception("Database integrity check failed")
        
        conn = sqlite3.connect('password_manager.db')
        c = conn.cursor()
        c.execute(
            'SELECT username, encrypted_password FROM passwords WHERE user_id=? AND website=?',
            (user_id, website)
        )
        result = c.fetchone()
        conn.close()
        
        if result:
            username, encrypted_password = result
            decrypted_password = self.fernet.decrypt(encrypted_password.encode()).decode()
            return username, decrypted_password
        return None, None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def get_login_by_id(self, login_id):
        conn = sqlite3.connect('password_manager.db')
        c = conn.cursor()
        c.execute('SELECT website, username, encrypted_password FROM passwords WHERE id=?', (login_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            website, username, encrypted_password = result
            decrypted_password = self.fernet.decrypt(encrypted_password.encode()).decode()
            return website, username, decrypted_password
        return None, None, None

    def verify_database_integrity(self):
        conn = sqlite3.connect('password_manager.db')
        c = conn.cursor()
        try:
            c.execute('PRAGMA integrity_check')
            result = c.fetchone()
            return result[0] == 'ok'
        finally:
            conn.close()
