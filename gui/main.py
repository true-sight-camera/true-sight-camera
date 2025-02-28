import os
import cv2
import tkinter as tk
import numpy as np
import zlib
import struct
import threading
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import Label
import RPi.GPIO as GPIO

import gui.image_processing as img_proc
from gui.menu import OverlayMenu
from gui.gallery import Gallery
from imaging.encrypt import sign_png


# GLOBAL VARIABLES #
fullscreen = True  # Start in fullscreen mode
current_frame = None  # Store the current frame
gallery_active = False  # Track if the gallery is active
capturing_image = False
GALLERY_DIRECTORY = "./gallery"

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Full Screen Tkinter Window")
root.attributes("-fullscreen", fullscreen)

# Create a label to display the video feed
video_label = Label(root)
video_label.pack(fill=tk.BOTH, expand=True)

# FEATURES # 
# overlay_menu = OverlayMenu(root)


def toggle_fullscreen(event=None):
    """Toggle between fullscreen and windowed mode."""
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)


def exit_fullscreen(event=None):
    """Exit fullscreen mode and close the application."""
    global default_cam_capture
    default_cam_capture.release()  # Release the video capture
    root.destroy()

def capture_picture(filename, processing_path, local_path):
    camera_index = 2
    global capturing_image
    capturing_image = True

    global default_cam_capture
    if default_cam_capture.isOpened():
        default_cam_capture.release()

    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        print(f"Error: Could not access the camera at index {camera_index}.")
        return

    print(f"Capturing an image from camera {camera_index}. Please wait...")

    # Capture a single frame
    ret, frame = camera.read()

    image_path = f"{processing_path}/{filename}.png"

    if not ret:
        print(f"Error: Failed to capture frame from camera {camera_index}.")
    else:
        # Save the captured image
        cv2.imwrite(image_path, frame)
        print(f"Image saved to {os.path.abspath(image_path)}")

    # Release the camera
    camera.release()
    capturing_image = False
    default_cam_capture = cv2.VideoCapture(0)
    update_frame()

    image = Image.open(image_path)

    width, height = image.size
    split_point = width // 2

    left_image = image.crop((0, 0, split_point, height))
    right_image = image.crop((split_point, 0, width, height))

    left_image.save(f"{processing_path}/{filename}_left.png")
    right_image.save(f"{processing_path}/{filename}_right.png")
    os.remove(image_path)

    threading.Thread(target=create_depth_map, args=(filename, processing_path, local_path)).start()


def create_depth_map(filename, processing_path, local_path):
    left_img = cv2.imread(f"{processing_path}/{filename}_left.png", cv2.IMREAD_GRAYSCALE)
    right_img = cv2.imread(f"{processing_path}/{filename}_right.png", cv2.IMREAD_GRAYSCALE)

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

    normalized_depth = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
    normalized_depth = np.uint8(normalized_depth)

    threading.Thread(target=add_depth_chunk_with_pixel_data, args=(filename, processing_path, local_path, normalized_depth)).start()


def add_depth_chunk_with_pixel_data(filename, processing_path, local_path, depth_array):
    right_image_path = f"{processing_path}/{filename}_right.png"
    left_image_path = f"{processing_path}/{filename}_left.png"

    output_image = f"{local_path}/{filename}.png"

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

    # TEST SIGNING
    print("TESTING SIGNING")
    sign_png(output_image)
    print("DONE SIGNING")

    os.remove(left_image_path)
    os.remove(right_image_path)


def save_current_frame(event=None):
    """Save the current frame to a file."""
    local_path = "gallery/local"
    processing_path = "gallery/need_processing"

    print("Saving image")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"frame_{timestamp}"

    # 🚀 Start the capture process in a new thread
    threading.Thread(target=capture_picture, args=(filename, processing_path, local_path)).start()


def update_frame():
    """Update the video frame in the Tkinter window."""
    global current_frame
    global default_cam_capture
    if gallery_active or capturing_image:  # Stop updating if gallery is active
        return
    
    if not default_cam_capture.isOpened():
        default_cam_capture = cv2.VideoCapture(0)

    ret, frame = default_cam_capture.read()
    if ret:
        current_frame = frame

        # Resize the frame to fit the Tkinter window
        screen_width = int(root.winfo_screenwidth())
        screen_height = int(root.winfo_screenheight())
        resized_frame = cv2.resize(frame, (screen_width, screen_height))

        # Convert to a Tkinter-compatible format
        processed_frame = img_proc.process_image(resized_frame)
        img = tk.PhotoImage(master=root, width=screen_width, height=screen_height,
                            data=cv2.imencode('.ppm', processed_frame)[1].tobytes())

        # Update the label with the image
        video_label.config(image=img)
        video_label.imgtk = img  # Store reference to avoid garbage collection

    # Schedule the next frame update
    video_label.after(5, update_frame)


# BINDINGS #
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_fullscreen)
root.bind("s", save_current_frame)
# root.bind("m", overlay_menu.toggle_menu)
# root.bind("<Return>", overlay_menu.select)

# GALLERY INTEGRATION #
gallery = Gallery(root, video_label, update_frame)

def toggle_gallery(event=None):
    """Toggle between the video feed and the gallery."""
    if gallery_active:
        gallery.close()
    else:
        gallery.open()

root.bind("<Return>", toggle_gallery)  # Press "<Return>" to switch to the gallery


# GPIO SETUP #
GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT)
GPIO.output(21, GPIO.HIGH)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def click_picture(channel):
    print("PICTURE")
    root.event_generate("s")

def click_gallery(channel):
    print("TOGGLE GALLERY")
    root.event_generate("<Return>")

def click_19(channel):
    print("Pressed Right")
    root.event_generate("<Right>")

def click_16(channel):
    print("Pressed Down")
    root.event_generate("<Down>")

def click_26(channel):
    print("Pressed Up")
    root.event_generate("<Up>")

def click_20(channel):
    print("Pressed Center")
    root.event_generate("<Return>")

def click_13(channel):
    print("Pressed Left")
    root.event_generate("<Left>")

def click_12(channel):
    print("Pressed Capture")
    root.event_generate("s")


GPIO.add_event_detect(12, GPIO.FALLING, callback=click_12, bouncetime=200)
GPIO.add_event_detect(13, GPIO.FALLING, callback=click_13, bouncetime=200)
GPIO.add_event_detect(19, GPIO.FALLING, callback=click_19, bouncetime=200)
GPIO.add_event_detect(16, GPIO.FALLING, callback=click_16, bouncetime=200)
GPIO.add_event_detect(26, GPIO.FALLING, callback=click_26, bouncetime=200)
GPIO.add_event_detect(20, GPIO.FALLING, callback=click_20, bouncetime=200)


# Initialize OpenCV video capture
default_cam_capture = cv2.VideoCapture(0)

# Start video updates
update_frame()

# Start the Tkinter event loop
try:
    root.mainloop()
except:
    GPIO.cleanup()
