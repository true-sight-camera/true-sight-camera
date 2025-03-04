import os
import requests
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from binascii import hexlify


BASE_URL = "http://3.133.137.72:5000"
PRIVATE_KEY_FILE_NAME = "shadow/private_key.pem"


# class SSLAdapter(HTTPAdapter):
#     def init_poolmanager(self, *args, **kwargs):
#         context = ssl.create_default_context()
#         context.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384')
#         kwargs['ssl_context'] = context
#         return super().init_poolmanager(*args, **kwargs)


def load_private_key(file_path: str) -> rsa.RSAPrivateKey:
    """Load an RSA private key from a PEM file."""
    try:
        with open(file_path, 'r') as key_file:
            pem_data = key_file.read()
            private_key_bytes = pem_data.encode("utf-8")
            private_key: rsa.RSAPrivateKey = load_pem_private_key(private_key_bytes, None)
            if not isinstance(private_key, rsa.RSAPrivateKey):
                raise ValueError("Not an RSA private key")
            return private_key
    except Exception as e:
        raise Exception(f"Error reading private key file: {str(e)}")

def sign_username(private_key: rsa.RSAPrivateKey, message: bytes) -> bytes:
    """Sign a message using the private key."""
    try:
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature
    except Exception as e:
        raise Exception(f"Error signing message: {str(e)}")

def send_image_data(image_hash, image_signature, image_data):
    url = f"{BASE_URL}/api/image"
    username = "pi"

    username_bytes = bytes("pi", encoding="ascii")
    private_key = load_private_key(PRIVATE_KEY_FILE_NAME)
    username_signature = sign_username(private_key, username_bytes)
    
    payload = {
        "encrypted_username": (None, hexlify(username_signature).decode()),
        "username": (None, username),
        "signed_hash": (None, image_hash.hex()),
        "hash_signature": (None, image_signature)
    }

    headers = {}

    # print(payload)
    # session = requests.Session()
    # session.mount('https://', SSLAdapter())
    # response = session.post(url, files=payload, headers=headers)

    response = requests.post(url, files=payload, headers=headers)

    print(response.status_code)
    print(response.text)

    # Upload image itself
    upload_image(image_data)

# Endpoint URL (adjust host/port as needed)

def upload_image(image_data):
    """
    Reads the file at file_path in binary mode and uploads it
    to the Flask endpoint as the request body.
    """
    url = f"{BASE_URL}/api/store_image"

    response = requests.post(url, data=image_data)
    
    if response.status_code == 200:
        print(f"Uploaded image successfully.")
        print("Response:", response.json())
    else:
        print(f"Failed to upload image.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
