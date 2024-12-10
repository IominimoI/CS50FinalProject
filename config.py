"""
Copyright (c) 2024 [Nico Geromin]
Licensed under the MIT License - see LICENSE file for details
"""
import os

# Create base directory path
BASE_DIR = os.path.join(os.path.expanduser('~'), '.pmg_secure')
DB_PATH = os.path.join(BASE_DIR, 'pmg_secure.db')
KEY_PATH = os.path.join(BASE_DIR, 'pmg_secure.key')
