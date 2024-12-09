import os

# Create base directory path
BASE_DIR = os.path.join(os.path.expanduser('~'), '.pmg_secure')
DB_PATH = os.path.join(BASE_DIR, 'pmg_secure.db')
KEY_PATH = os.path.join(BASE_DIR, 'pmg_secure.key')
