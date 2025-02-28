from datetime import datetime
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from binascii import hexlify, unhexlify
from imaging.png import PngInteractor
from imaging.encrypt import sign_png

PRIVATE_KEY_FILE_NAME = "shadow/private_key.pem"
PUBLIC_KEY_FILE_NAME = "shadow/public_key.pem"
    
if __name__ == "__main__":
    filename = "gallery/local/frame_20250227_190856.png"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"gallery/uploaded/done_{timestamp}.png"
    
    # Create PNG interactor for the input image
    png_creation_interactor = PngInteractor(filename)
    sign_png(filename)

