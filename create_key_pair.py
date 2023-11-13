from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Specify the key size for the RSA key pair (2048 or 4096 are common choices)
key_size = 2048

# Generate the private key
private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())

# Serialize the private key to PEM format
pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),  # Use BestAvailableEncryption for a password-protected key
)

# Write the private key to a file
with open("private_key.pem", "wb") as f:
    f.write(pem_private_key)

# Generate the public key from the private key
public_key = private_key.public_key()

# Serialize the public key to PEM format
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Write the public key to a file
with open("public_key.pem", "wb") as f:
    f.write(pem_public_key)

print("Public and private keys have been generated and saved to 'public_key.pem' and 'private_key.pem'.")
print("Move the private key somewhere safe!")
