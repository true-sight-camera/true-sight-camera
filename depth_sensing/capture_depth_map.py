import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import struct
import zlib
from PIL import Image

image_path = "../test_images/stereo_vision.png"
left_image_path = "../test_images/left_image_3.png"
right_image_path = "../test_images/right_image_3.png"
output_image = "../test_images/image_with_depth_2.png"

camera_index = 0;

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

    image = Image.open(image_path)

    width, height = image.size
    split_point = width // 2

    left_image = image.crop((0, 0, split_point, height))
    right_image = image.crop((split_point, 0, width, height))

    left_image.save(left_image_path)
    right_image.save(right_image_path)
    os.remove(image_path)

def create_depth_map_SGBM():
    left_img = cv2.imread(left_image_path, cv2.IMREAD_GRAYSCALE)
    right_img = cv2.imread(right_image_path, cv2.IMREAD_GRAYSCALE)

    left_img = cv2.equalizeHist(left_img)
    right_img = cv2.equalizeHist(right_img)
    
    window_size = 6
    n_disp_factor = 6 # adjust
    num_disp = 16*n_disp_factor

    focal_length = 1000
    baseline = 0.6

    stereo = cv2.StereoSGBM_create(
        minDisparity=0,
        numDisparities=num_disp,
        blockSize=window_size,
        P1=8*1*window_size**2,
        P2=32*1*window_size**2,
        disp12MaxDiff=1,
        uniquenessRatio=7,
        speckleWindowSize=0,
        speckleRange=2,
        preFilterCap=63,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )

    disparity = stereo.compute(left_img, right_img).astype(np.float32) / 16.0

    depth_map = np.zeros_like(disparity, dtype=np.float32)
    disparity[disparity == 0] = 1
    depth_map = (focal_length * baseline) / disparity

    plt.imshow(depth_map, 'gray')
    plt.colorbar()
    plt.show()

def create_depth_map():
    left_img = cv2.imread(left_image_path, cv2.IMREAD_GRAYSCALE)
    right_img = cv2.imread(right_image_path, cv2.IMREAD_GRAYSCALE)

    left_img = cv2.equalizeHist(left_img)
    right_img = cv2.equalizeHist(right_img)
    
    window_size = 6
    n_disp_factor = 6 # adjust
    num_disp = 16*n_disp_factor

    focal_length = 1000
    baseline = 0.6

    stereo = cv2.StereoSGBM_create(
        minDisparity=0,
        numDisparities=num_disp,
        blockSize=window_size,
        P1=8*1*window_size**2,
        P2=32*1*window_size**2,
        disp12MaxDiff=1,
        uniquenessRatio=7,
        speckleWindowSize=0,
        speckleRange=2,
        preFilterCap=63,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )

    disparity = stereo.compute(left_img, right_img).astype(np.float32) / 16.0

    depth_map = np.zeros_like(disparity, dtype=np.float32)
    disparity[disparity == 0] = 1
    depth_map = (focal_length * baseline) / disparity

    plt.imshow(depth_map, 'gray')
    plt.colorbar()
    plt.show()
    
    normalized_depth = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
    normalized_depth = np.uint8(normalized_depth)

    # Apply colormap
    colored_depth = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)

    # Show Depth Map
    plt.figure(figsize=(10, 5))
    plt.imshow(colored_depth)
    plt.title("Depth Map with Colormap")
    plt.axis("off")
    plt.show()

    return normalized_depth

def add_depth_chunk_with_pixel_data(depth_array):
    """
    Adds a custom depth data chunk to a PNG file with pixel-specific depth information.

    Args:
        png_file (str): Path to the input PNG file.
        depth_array (numpy.ndarray): 2D array of depth values (0-255) matching the image dimensions.
        output_file (str): Path to the output PNG file.
    """
    # Read the original PNG file
    with open(right_image_path, "rb") as f:
        png_data = f.read()
    
    # Validate PNG file (must start with PNG signature)
    png_signature = b"\x89PNG\r\n\x1a\n"
    if not png_data.startswith(png_signature):
        raise ValueError("Not a valid PNG file")
    
    # Validate depth array dimensions
    img = Image.open(right_image_path)
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
    # capture_picture()
    depth_map = create_depth_map()
    add_depth_chunk_with_pixel_data(depth_array=depth_map)