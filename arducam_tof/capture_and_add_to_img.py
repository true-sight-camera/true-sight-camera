import cv2
import os
import numpy as np
import struct
import zlib
from PIL import Image
import ArducamDepthCamera as ac

image_path = "../test_images/tof_vision.png"
output_image = "../test_images/image_with_depth_2.png"

camera_index = 1;


def resize_with_padding(image, target_width, target_height):
    h, w = image.shape[:2]
    scale = min(target_width / w, target_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    pad_x = (target_width - new_w) // 2
    pad_y = (target_height - new_h) // 2
    
    padded = cv2.copyMakeBorder(resized, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    return padded

def normalize_depth(depth_buf):
    depth_min = np.min(depth_buf)
    depth_max = np.max(depth_buf)
    if depth_max > depth_min:  # Avoid division by zero
        normalized = (depth_buf - depth_min) / (depth_max - depth_min) * 255.0
    else:
        normalized = np.zeros_like(depth_buf)  # If all values are the same
    return normalized.astype(np.uint8)

def capture_picture():
    """
    Captures a picture from the specified camera and saves it to the specified path.

    Args:
        camera_index (int): The index of the camera to use (e.g., 0, 1, etc.).
        save_path (str): The file path where the captured image will be saved.
    """
    # Initialize the camera with the specified index
    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        print(f"Error: Could not access the camera at index {camera_index}.")
        return

    print(f"Capturing an image from camera {camera_index}. Please wait...")

    # Capture a single frame
    ret, frame = camera.read()

    if not ret:
        print(f"Error: Failed to capture frame from camera {camera_index}.")
    else:
        # Save the captured image
        cv2.imwrite(image_path, frame)
        print(f"Image saved to {os.path.abspath(image_path)}")

    # Release the camera
    camera.release()

def get_depth_map():
    print("Arducam Depth Camera Depth Map Capture.")
    print("  SDK version:", ac.__version__)

    cam = ac.ArducamCamera()
    ret = cam.open(ac.Connection.CSI, 0)
    if ret != 0:
        print("Failed to open camera. Error code:", ret)
        return

    ret = cam.start(ac.FrameType.DEPTH)
    if ret != 0:
        print("Failed to start camera. Error code:", ret)
        cam.close()
        return

    info = cam.getCameraInfo()
    print(f"Camera resolution: {info.width}x{info.height}")

    frame = cam.requestFrame(2000)
    depth_buf = frame.depth_data
    cam.releaseFrame(frame)
    cam.stop()
    cam.close()

    depth_map = normalize_depth(depth_buf)
    
    # Resize depth map while preserving aspect ratio with padding
    target_resolution = (1280, 800)
    padded_depth_map = resize_with_padding(depth_map, *target_resolution)

    return padded_depth_map

def add_depth_chunk_with_pixel_data(depth_array):
    """
    Adds a custom depth data chunk to a PNG file with pixel-specific depth information.

    Args:
        png_file (str): Path to the input PNG file.
        depth_array (numpy.ndarray): 2D array of depth values (0-255) matching the image dimensions.
        output_file (str): Path to the output PNG file.
    """
    # Read the original PNG file
    with open(image_path, "rb") as f:
        png_data = f.read()
    
    # Validate PNG file (must start with PNG signature)
    png_signature = b"\x89PNG\r\n\x1a\n"
    if not png_data.startswith(png_signature):
        raise ValueError("Not a valid PNG file")
    
    # Validate depth array dimensions
    img = Image.open(image_path)
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
    with open(output_image, "wb") as f:
        f.write(new_png_data)
    print(f"Depth data chunk added to {output_image}")



if __name__ == "__main__":
    # this is full process to add depth array to pic
    capture_picture()
    depth_map = get_depth_map()
    print("hello")
    add_depth_chunk_with_pixel_data(depth_array=depth_map)