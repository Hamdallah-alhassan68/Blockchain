from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Generate keys once
key = RSA.generate(2048)
private_key = key
public_key = key.publickey()

def encrypt_data(data):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted = cipher.encrypt(data.encode())
    return encrypted

def decrypt_data(encrypted_data):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted = cipher.decrypt(encrypted_data)
    return decrypted.decode()
