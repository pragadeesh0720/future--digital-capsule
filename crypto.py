import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken


ITERATIONS = 600_000


def generate_salt():
    return os.urandom(16)


def derive_key(password, salt):
    password_bytes = password.encode("utf-8")

    key = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt,
        ITERATIONS,
        dklen=32
    )

    return base64.urlsafe_b64encode(key)


def encrypt_message(message, password, salt):
    key = derive_key(password, salt)

    cipher = Fernet(key)

    return cipher.encrypt(
        message.encode("utf-8")
    )


def decrypt_message(encrypted_message, password, salt):

    key = derive_key(password, salt)

    cipher = Fernet(key)

    try:
        decrypted = cipher.decrypt(encrypted_message)

        return decrypted.decode("utf-8")

    except InvalidToken:
        return None