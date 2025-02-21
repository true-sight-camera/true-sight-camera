import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

image_path = "test_images/stereo_vision.png"

left_image_path = "test_images/left_image.png"
right_image_path = "test_images/right_image.png"

def capture_picture():
    """
    Captures a picture from the specified camera and saves it to the specified path.

    Args:
        camera_index (int): The index of the camera to use (e.g., 0, 1, etc.).
        save_path (str): The file path where the captured image will be saved.
    """
    # Initialize the camera with the specified index
    camera = cv2.VideoCapture(0)

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
        print(f"Image saved to {os.path.abspath(save_path)}")

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


def create_depth_map():
    # Load stereo images
    left_img = cv2.imread("left_image.jpg", cv2.IMREAD_GRAYSCALE)
    right_img = cv2.imread("right_image.jpg", cv2.IMREAD_GRAYSCALE)

    # TUNABLE StereoSGBM Parameters
    numDisparities = 64   # Multiple of 16 (increase for better accuracy)
    blockSize = 9         # Odd number (increase to reduce noise, decrease for detail)
    minDisparity = 0
    disp12MaxDiff = 1
    uniquenessRatio = 15
    speckleWindowSize = 50
    speckleRange = 2
    P1 = 8 * 3 * blockSize ** 2
    P2 = 32 * 3 * blockSize ** 2

    # Initialize StereoSGBM matcher
    stereo = cv2.StereoSGBM_create(
        minDisparity=minDisparity,
        numDisparities=numDisparities,
        blockSize=blockSize,
        P1=P1,
        P2=P2,
        disp12MaxDiff=disp12MaxDiff,
        uniquenessRatio=uniquenessRatio,
        speckleWindowSize=speckleWindowSize,
        speckleRange=speckleRange
    )

    # Compute disparity map
    disparity = stereo.compute(left_img, right_img).astype(np.float32) / 16.0

    # TUNABLE Camera Parameters
    focal_length = 700  # Adjust per camera specs
    baseline = 0.06      # Stereo camera baseline distance in meters

    # Avoid division by zero
    disparity[disparity <= 0] = 0.1

    # Compute depth map using Depth = (f * B) / disparity
    depth_map = (focal_length * baseline) / disparity

    # Normalize Depth Map (for visualization)
    normalize_min = np.min(depth_map)
    normalize_max = np.max(depth_map)

    normalized_depth = 255 * (depth_map - normalize_min) / (normalize_max - normalize_min)
    normalized_depth = np.uint8(normalized_depth)

    # Apply Colormap for Visualization
    colormap = cv2.COLORMAP_PLASMA  # Options: JET, MAGMA, VIRIDIS, etc.
    colored_depth = cv2.applyColorMap(normalized_depth, colormap)

    # Save and Show Depth Map
    cv2.imwrite("normalized_depth_map.png", colored_depth)
    plt.figure(figsize=(10, 5))
    plt.imshow(colored_depth)
    plt.title("Depth Map with Colormap")
    plt.axis("off")
    plt.show()



if __name__ == "__main__":
    capture_picture()
    create_depth_map()