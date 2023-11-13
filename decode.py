from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from pathlib import Path
import zipfile
import io
import sys


def decrypt_data_with_aes(encrypted_data, key, iv):
    # Create an AES cipher object with the key and IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    # Decrypt the data
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    # Unpad the data
    unpadder = sym_padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return decrypted_data


def run(last_n=1):
    # Load your private key
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend(),  # Replace with your key's password if it's encrypted
        )

    files = list(Path("logs").glob("*.log"))

    for file in files[-last_n:]:
        print(f"Decrypting {file}...")
        # Read the encrypted AES key and data from the file
        with open(file, "rb") as f:
            encrypted_aes_key = f.read(private_key.key_size // 8)
            iv = f.read(16)
            encrypted_data = f.read()

        # Decrypt the AES key with the private key
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )

        # Decrypt the data with the AES key
        original_data = decrypt_data_with_aes(encrypted_data, aes_key, iv)

        # decode with zip, and print the content of key_logs.txt and mouse_logs.txt
        # with zipfile.ZipFile(io.BytesIO(original_data)) as zipf:
        #     key_logs = zipf.read("key_logs.txt").decode()
        #     mouse_logs = zipf.read("mouse_logs.txt").decode()
        #     print(key_logs)
        #     print(mouse_logs)
        with zipfile.ZipFile(io.BytesIO(original_data), "r") as zipf:
            # List all file names in the zip
            for file_name in zipf.namelist():
                # Extract the file's contents
                with zipf.open(file_name) as f:
                    file_contents = f.read().decode("utf-8")
                    print(f"Contents of {file_name} in {file}:")
                    print(file_contents)
                    print("-" * 20)


if __name__ == "__main__":
    try:
        last_n = int(sys.argv[1])
    except:
        last_n = 1
    run(last_n)
