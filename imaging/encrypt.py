from datetime import datetime
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from binascii import hexlify, unhexlify
from imaging.send_to_db import send_image_data
from imaging.png import PngInteractor

import sys

# Constants
PRIVATE_KEY_FILE_NAME = "shadow/private_key.pem"
PUBLIC_KEY_FILE_NAME = "shadow/public_key.pem"

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

def load_public_key(file_path: str) -> rsa.RSAPublicKey:
    """Load an RSA public key from a PEM file."""
    try:
        with open(file_path, 'rb') as key_file:
            pem_data = key_file.read()
            public_key = load_pem_public_key(pem_data)
            if not isinstance(public_key, rsa.RSAPublicKey):
                raise ValueError("Not an RSA public key")
            return public_key
    except Exception as e:
        raise Exception(f"Error reading public key file: {str(e)}")

def sign_message(private_key: rsa.RSAPrivateKey, message: bytes) -> bytes:
    """Sign a message using the private key."""
    try:
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            Prehashed(hashes.SHA256())
        )
        return signature
    except Exception as e:
        raise Exception(f"Error signing message: {str(e)}")

def verify_signature(public_key: rsa.RSAPublicKey, message: bytes, signature: bytes) -> bool:
    """Verify a signature using the public key."""
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            Prehashed(hashes.SHA256())
        )
        return True
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False

def hash_image_sha256(data: bytes) -> bytes:
    """Create SHA256 hash of image data."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.digest()

def sign_png(filename: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"gallery/uploaded/done_{timestamp}.png"
    
    try:
        # Create PNG interactor for the input image
        png_creation_interactor = PngInteractor(filename)

        # Hash the image
        print("BYTES")
        print(hexlify(png_creation_interactor.image_bytes[:30]))
        image_hash = hash_image_sha256(png_creation_interactor.image_bytes)
        # print(f"Image hash (bytes): {image_hash}")
        # print(f"Image hash (hex): {hexlify(image_hash).decode()}")
        # print(f"Image hash (bytes array): {list(image_hash)}")

        # Load private key and sign the hash
        private_key = load_private_key(PRIVATE_KEY_FILE_NAME)
        signed_bytes = sign_message(private_key, image_hash)  # Pass bytes directly
        # print(f"SIGNED MESSAGE: {hexlify(signed_bytes).decode()}\n")


        # Add signature to image metadata
        png_creation_interactor.add_text_chunk_to_data(
            "Signature", 
            hexlify(signed_bytes).decode(), 
            output_filename
        )
        print("Signature added to file metadata")
        print("\n-----------READING METADATA-----------\n")

        
        # Read and verify the signature
        png_reader_interactor = PngInteractor(output_filename)
        png_reader_interactor.read_all_metadata()

        signature = png_reader_interactor.find_signature_metadata()
        if not signature:
            raise Exception("Could not find signature in metadata")

        signature_bytes = unhexlify(signature)

        # Load public key and verify signature
        public_key = load_public_key(PUBLIC_KEY_FILE_NAME)
        
        # Print verification data for debugging
        print(f"\nVerifying signature using the following data:")
        # print(f"Original hash: {hexlify(image_hash).decode()}")
        # print(f"Signature: {hexlify(signature_bytes).decode()}")
        
        if verify_signature(public_key, image_hash, signature_bytes):
            print("\nSignature Verified ✓")
        else:
            print("\nSignature Verification Failed ✗")
        
        send_image_data(image_hash, signature, png_creation_interactor.image_bytes)

    except Exception as e:
        print(f"Error: {str(e)}")
        return
    
if __name__ == "__main__":
    filename = "gallery/local/frame_20250227_190856.png"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"gallery/uploaded/done_{timestamp}.png"
    
    # Create PNG interactor for the input image
    png_creation_interactor = PngInteractor(filename)

    # Hash the image
    # print("BYTES")
    print(hexlify(png_creation_interactor.image_bytes).decode())
    image_hash = hash_image_sha256(png_creation_interactor.image_bytes)
    # print(f"Image hash (bytes): {image_hash}")
    # print(f"Image hash (hex): {hexlify(image_hash).decode()}")

    # print(f"Python version: {sys.version}")
    # print(f"Hashlib module location: {hashlib.__file__}")
    # print(hashlib.algorithms_available)


