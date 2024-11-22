import sqlite3
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

# Load the public key for password encryption
def load_public_key():
    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key

# Encrypt the password using RSA public key
def encrypt_password(password):
    public_key = load_public_key()
    encrypted = public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

# Function to add a new admin to the database
def add_admin(username, password, mailID):
    encrypted_password = encrypt_password(password)
    conn = sqlite3.connect('access_control.db')
    cursor = conn.cursor()
    
    # Insert the new admin record into the admin table
    cursor.execute('''
        INSERT INTO admin (adminUsername, password, mailID)
        VALUES (?, ?, ?)
    ''', (username, encrypted_password, mailID))
    
    conn.commit()
    conn.close()
    print("Admin added successfully!")

# Add admin details
add_admin("Azim", "azim11", "baldiwaalazim@gmail.com")
