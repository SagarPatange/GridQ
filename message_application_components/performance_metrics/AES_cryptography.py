# Have to run `pip install cryptography`
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from os import urandom

def encrypt_data(data, password):
    # Generate a random salt
    salt = urandom(16)
    
    # Derive a key from the password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    
    # Generate a random initialization vector (IV)
    iv = urandom(16)
    
    # Create cipher configuration
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    
    # Encryptor object
    encryptor = cipher.encryptor()
    
    # Padding data to ensure it's a multiple of 16 bytes (AES block size)
    data = data + b' ' * (16 - len(data) % 16)
    
    # Perform encryption
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    
    # Return IV, salt, and encrypted data
    return iv, salt, encrypted_data

def decrypt_data(encrypted_data, password, iv, salt):
    # Derive the key using the same parameters and password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    
    # Create cipher configuration
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    
    # Decryptor object
    decryptor = cipher.decryptor()
    
    # Perform decryption
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Remove padding
    return decrypted_data.rstrip(b' ')

# Example usage
password = 'securepassword'
data = b'Hello, world!'

iv, salt, encrypted = encrypt_data(data, password)
print('Encrypted:', encrypted)

decrypted = decrypt_data(encrypted, password, iv, salt)
print('Decrypted:', decrypted)
