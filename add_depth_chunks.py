import struct
import zlib
import numpy as np
from PIL import Image

def add_depth_chunk_with_pixel_data(png_file, depth_array, output_file):
    """
    Adds a custom depth data chunk to a PNG file with pixel-specific depth information.

    Args:
        png_file (str): Path to the input PNG file.
        depth_array (numpy.ndarray): 2D array of depth values (0-255) matching the image dimensions.
        output_file (str): Path to the output PNG file.
    """
    # Read the original PNG file
    with open(png_file, "rb") as f:
        png_data = f.read()
    
    # Validate PNG file (must start with PNG signature)
    png_signature = b"\x89PNG\r\n\x1a\n"
    if not png_data.startswith(png_signature):
        raise ValueError("Not a valid PNG file")
    
    # Validate depth array dimensions
    img = Image.open(png_file)
    if depth_array.shape != (img.height, img.width):
        raise ValueError("Depth array dimensions must match the image dimensions")
    
    # Flatten the depth array and compress it
    depth_bytes = depth_array.astype(np.uint8).tobytes()  # Convert to bytes
    compressed_depth = zlib.compress(depth_bytes)         # Compress the depth data
    
    # Create a custom PNG chunk for depth data
    chunk_type = b"dEPh"                                  # Custom chunk identifier
    chunk_data = compressed_depth
    chunk_length = struct.pack(">I", len(chunk_data))     # Length of the chunk data
    chunk_crc = struct.pack(">I", zlib.crc32(chunk_type + chunk_data))  # CRC for validation
    
    custom_chunk = chunk_length + chunk_type + chunk_data + chunk_crc
    
    # Find the position of the IEND chunk
    iend_index = png_data.rfind(b"IEND")
    if iend_index == -1:
        raise ValueError("PNG file is missing the IEND chunk")
    
    # Insert the custom chunk before the IEND chunk
    new_png_data = png_data[:iend_index - 4] + custom_chunk + png_data[iend_index - 4:]
    
    # Write the modified PNG to a new file
    with open(output_file, "wb") as f:
        f.write(new_png_data)
    print(f"Depth data chunk added to {output_file}")



def extract_depth_chunk(file_path, chunk_type=b"dEPh"):
    """
    Extracts the custom depth data chunk from a PNG file.
    
    Args:
        file_path (str): Path to the PNG file.
        chunk_type (bytes): Type of the chunk to extract (default is b"dEPh").
    
    Returns:
        bytes: The decompressed depth data if the chunk is found.
    """
    with open(file_path, "rb") as f:
        # Validate PNG signature
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")
        
        while True:
            # Read the chunk length (4 bytes, big-endian)
            length_bytes = f.read(4)
            if len(length_bytes) < 4:
                break  # End of file
            length = int.from_bytes(length_bytes, "big")
            
            # Read the chunk type (4 bytes)
            chunk = f.read(4)
            
            # Read the chunk data and CRC (length + 4 bytes CRC)
            chunk_data = f.read(length)
            crc = f.read(4)
            
            # Check if this is the desired chunk type
            if chunk == chunk_type:
                # Decompress the depth data
                decompressed_data = zlib.decompress(chunk_data)
                depth_array_flat = list(decompressed_data)
                width, height = get_png_dimensions(file_path)
                depth_array = [depth_array_flat[i * width : (i+1) * width] for i in range(height)]
                return depth_array

    raise ValueError(f"Chunk type {chunk_type.decode('utf-8')} not found in the PNG file.")


def get_png_dimensions(file_path):
    with Image.open(file_path) as img:
        width, height = img.size
    return width, height


if __name__ == "__main__":
    # randomizing depth arr
    png_file = "mario.png"
    dest_file = "example_with_depth.png"
    width, height = get_png_dimensions(png_file)
    depth_array = np.random.randint(0, 256, (height, width), dtype=np.uint8)

    # Add depth data as a custom chunk
    add_depth_chunk_with_pixel_data(png_file, depth_array, dest_file)

    depth_from_chunk = extract_depth_chunk(dest_file)
    assert np.array_equal(np.array(depth_array), np.array(depth_from_chunk))