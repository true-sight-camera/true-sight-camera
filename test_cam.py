import cv2
import os
from PIL import Image


def capture_picture(camera_index=0, save_path="captured_image.jpg"):
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
        cv2.imwrite(save_path, frame)
        print(f"Image saved to {os.path.abspath(save_path)}")

    # Release the camera
    camera.release()


def list_camera_indexes():
    """
    Lists all available camera indexes by attempting to access each index.
    """
    print("Checking available camera indexes...")
    available_indexes = []
    for index in range(10):  # Check the first 10 indexes
        camera = cv2.VideoCapture(index)
        if camera.isOpened():
            print(f"Camera found at index {index}")
            available_indexes.append(index)
            camera.release()
    if not available_indexes:
        print("No cameras found.")
    return available_indexes


if __name__ == "__main__":
    # Attempt to capture images from two cameras
    # available_indexes = list_camera_indexes()
    # available_indexes = [0, 2]
    # for index in available_indexes:
    #     file_name = f"camera_{index}.png"
    #     capture_picture(camera_index=index, save_path=file_name)
    image_path = "test_images/stereo_vision.png"
    capture_picture(camera_index=0, save_path=image_path)
    image = Image.open(image_path)

    width, height = image.size
    split_point = width // 2

    left_image = image.crop((0, 0, split_point, height))
    right_image = image.crop((split_point, 0, width, height))

    left_image_path = "test_images/left_image.png"
    right_image_path = "test_images/right_image.png"
    left_image.save(left_image_path)
    right_image.save(right_image_path)
    os.remove(image_path)
