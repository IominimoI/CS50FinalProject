# PMG Secure - Password Manager & Generator

A robust password management solution built with Python, focusing on security, usability, and modern cryptographic standards.

## Features

### Password Generation
- Customizable length (8-32 characters)
- Three complexity tiers:
  - **Simple**: Dictionary-based, memorable combinations
  - **Moderate**: Mixed character sets with guaranteed variety
  - **Complex**: Full ASCII character set with maximum entropy

### Security Architecture
- Multi-layer encryption:
  - PBKDF2 key derivation (100,000 iterations)
  - Fernet symmetric encryption (AES-128 in CBC mode)
  - SHA-256 password hashing with unique salts

### User Interface
- Modern dark-mode design with CustomTkinter
- Organized tabs for different functions:
  1. **Generate Password**: Create and evaluate new passwords
  2. **Store Login**: Save website credentials securely
  3. **Search Login**: Find credentials by website name
  4. **Browse Login**: View and manage all stored credentials
  5. **Check Password**: Analyze password strength in real-time

## Technical Details

### Storage Structure
```
~/.pmg_secure/ 
  ├── pmg_secure.db  # Encrypted SQLite database 
  └── pmg_secure.key # Key storage file
```

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Iomin161/CS50FinalProject.git
   cd CS50FinalProject
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Make the app callable from terminal**:
   ```bash
   # Create a simple shell script in a directory that is in your PATH
   echo '#!/bin/bash
   cd /path/to/CS50FinalProject
   source venv/bin/activate
   python pmg_gui.py' > ~/bin/pmgsecure
   
   # Make it executable
   chmod +x ~/bin/pmgsecure
   ```
   
   Note: If `~/bin` isn't in your PATH, add it or use another directory that is.
   
   Alternatively, add an alias to your `.bashrc` or `.zshrc`:
   ```bash
   echo 'alias pmgsecure="cd /path/to/CS50FinalProject && source venv/bin/activate && python pmg_gui.py"' >> ~/.bashrc
   source ~/.bashrc
   ```

5. **Run the application**:
   ```bash
   pmgsecure
   ```
   Use the ```--daemon``` flag to run the app in the background.
## Usage

- **First Use**: Register a new account with a strong master password
- **Password Management**: Generate, store, and retrieve passwords through the intuitive interface
- **Security**: All sensitive data is encrypted before storage, with multiple layers of protection

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Developed as a final project for Harvard CS50x. Special thanks to the CS50 teaching team for their exceptional educational resources.
