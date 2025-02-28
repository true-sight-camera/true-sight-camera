import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from imaging.png import PngInteractor
import sys

BASE_URL = "https://3.133.137.72:5000"
PRIVATE_KEY_FILE_NAME = "../shadow/private_key.pem"

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

def send_image_hash_and_signature(image_hash, image_signature):
    # url = f"{BASE_URL}/api/image"
    url = "oof"
    username = "pi"

    username_bytes = bytes("pi", encoding="ascii")
    private_key = load_private_key(PRIVATE_KEY_FILE_NAME)
    username_signature = sign_username(private_key, username_bytes)

    payload = {
        "encrypted_username": username_signature,
        "username": username,
        "signed_hash": image_hash,
        "hash_signature": image_signature
    }

    print(username_signature)
    print(username)
    print(image_hash)
    print(image_signature)

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        while not filename:
            filename = input("Give a file name to upload")
    

    png_creation_interactor = PngInteractor(filename)
    image_hash = hash_image_sha256(png_creation_interactor.image_bytes)
    
    send_image_hash_and_signature(image_hash, image_signature)
