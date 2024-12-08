import os

# Create base directory path
BASE_DIR = os.path.join(os.path.expanduser('~'), '.password_manager')
DB_PATH = os.path.join(BASE_DIR, 'password_manager.db')
KEY_PATH = os.path.join(BASE_DIR, 'encryption_key.key')
