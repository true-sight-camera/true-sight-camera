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
import ArducamDepthCamera as ac


import gui.image_processing as img_proc
from gui.menu import OverlayMenu
from gui.gallery import Gallery
from imaging.encrypt import sign_png


# GLOBAL VARIABLES #
fullscreen = True  # Start in fullscreen mode
current_frame = None  # Store the current frame
gallery_active = False  # Track if the gallery is active
capturing_image = False
overlay = None
GALLERY_DIRECTORY = "./gallery"
DEFAULT_CAM_IDX = 1

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

def show_loading_overlay():
    """Show a semi-transparent overlay with a loading icon."""
    global loading_label, overlay

    # Create a full-screen overlay
    overlay = tk.Canvas(root, bg="black", width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Set transparency by using a dark background
    overlay.configure(bg="#000000", highlightthickness=0)  # Solid black background

    # Add loading text
    loading_label = tk.Label(overlay, text="Capturing...", font=("Arial", 40), fg="white", bg="black")
    loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Force UI update
    root.update_idletasks()


import cv2
import numpy as np

def old_resize_with_padding(image, target_width, target_height):
    h, w = image.shape[:2]
    scale = min(target_width / w, target_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    pad_x = (target_width - new_w) // 2
    pad_y = (target_height - new_h) // 2
    
    padded = cv2.copyMakeBorder(resized, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    return padded

def resize_with_padding(image, target_width, target_height):
    h, w = image.shape[:2]

    # Resize while maintaining aspect ratio
    scale = target_width / w
    new_w = target_width
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Crop from the top and bottom if necessary
    if new_h > target_height:
        crop_y = (new_h - target_height) // 2
        cropped = resized[crop_y:crop_y + target_height, :]
    else:
        cropped = resized

    return cropped

def normalize_depth(depth_buf):
    depth_min = np.min(depth_buf)
    depth_max = np.max(depth_buf)
    if depth_max > depth_min:  # Avoid division by zero
        normalized = (depth_buf - depth_min) / (depth_max - depth_min) * 255.0
    else:
        normalized = np.zeros_like(depth_buf)  # If all values are the same
    return normalized.astype(np.uint8)

def capture_tof_data(filename, processing_path, local_path):
    print("Arducam Depth Camera Depth Map Capture.")
    print("  SDK version:", ac.__version__)
    
    camera_index = 1
    global capturing_image
    capturing_image = True
    global default_cam_capture

    show_loading_overlay()

    if default_cam_capture.isOpened():
        default_cam_capture.release()
    
    # Start Arducam TOF data capture
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

    ### ADDITION START
    r = cam.getControl(ac.Control.RANGE)
    print("R VALUE", r)
    frame = cam.requestFrame(2000)
    while frame is None:
        frame = cam.requestFrame(2000)

    depth_buf = frame.depth_data
    confidence_buf = frame.confidence_data
    result_image = (depth_buf * (255.0 / r)).astype(np.uint8)
    result_image = cv2.applyColorMap(result_image, cv2.COLORMAP_RAINBOW)
    result_image = np.nan_to_num(result_image)
    result_image[confidence_buf < 30] = (0, 0, 0)
    cv2.normalize(confidence_buf, confidence_buf, 1, 0, cv2.NORM_MINMAX)

    cv2.imshow("preview_confidence", confidence_buf)
    cv2.imshow("preview", result_image)

    # cv2.rectangle(result_image, followRect.rect, white_color, 1)
    # if not selectRect.empty:
    #     cv2.rectangle(result_image, selectRect.rect, black_color, 2)
    #     print("select Rect distance:", np.mean(depth_buf[selectRect.slice]))

    cam.releaseFrame(frame)
    ### ADDITION END

    cam.releaseFrame(frame)
    cam.stop()
    cam.close()

    capturing_image = False
    default_cam_capture = cv2.VideoCapture(DEFAULT_CAM_IDX)
    update_frame()

    if overlay:
        overlay.destroy()

    # depth buf contains the depth map data to be normalized and converted to a method which can be saved
    depth_map = normalize_depth(depth_buf)

    # Rotate depth map 180 degrees
    depth_map = np.rot90(depth_map, 2)
    
    # Resize depth map while preserving aspect ratio with padding
    target_resolution = (1280, 800)
    depth_array = resize_with_padding(depth_map, *target_resolution)

    add_depth_chunk_with_pixel_data(filename, processing_path, local_path, depth_array)


def add_depth_chunk_with_pixel_data(filename, processing_path, local_path, depth_array):
    processing_image_path = f"{processing_path}/{filename}"
    output_image = f"{local_path}/{filename}"

    # Read the original PNG file
    with open(processing_image_path, "rb") as f:
        png_data = f.read()
    
    # Validate PNG file (must start with PNG signature)
    png_signature = b"\x89PNG\r\n\x1a\n"
    if not png_data.startswith(png_signature):
        raise ValueError("Not a valid PNG file")
    
    # Validate depth array dimensions
    img = Image.open(processing_image_path)
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
    # print("TESTING SIGNING")
    # sign_png(output_image)
    # print("DONE SIGNING")

    os.remove(processing_image_path)


def save_current_frame(event=None):
    """Save the current frame to a file."""
    local_path = "gallery/local"
    processing_path = "gallery/need_processing"

    print("Saving image")
    global current_frame
    if current_frame is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"frame_{timestamp}.png"
        cv2.imwrite(f"{processing_path}/{filename}", current_frame)
        print(f"Saved current frame as {filename}")
        # 🚀 Start the capture process in a new thread
        threading.Thread(target=capture_tof_data, args=(filename, processing_path, local_path)).start()
    else:
        print("No frame to save.")


def update_frame():
    """Update the video frame in the Tkinter window."""
    global current_frame
    global default_cam_capture
    if gallery_active or capturing_image:  # Stop updating if gallery is active
        return
    
    if not default_cam_capture.isOpened():
        default_cam_capture = cv2.VideoCapture(DEFAULT_CAM_IDX)

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

def toggle_gallery(event=None):
    """Toggle between the video feed and the gallery."""
    global gallery_active

    if gallery_active:
        # ✅ Closing Gallery - Return to Video Feed
        gallery_active = False
        
        # ✅ Rebind video feed controls
        root.bind("<Return>", toggle_gallery)  # Open gallery
        root.bind("s", save_current_frame)  # Capture image
        
        # ✅ Restart video feed (fixes white screen issue)
        root.after(5, update_frame)
    else:
        # ✅ Opening Gallery - Hide Video Feed
        gallery_active = True
        gallery.open()

gallery = Gallery(root, video_label, update_frame, toggle_gallery)

root.bind("g", toggle_gallery)  # Press "<Return>" to switch to the gallery


# GPIO SETUP #
GPIO.setmode(GPIO.BCM)
#Pin Layout
#No. - Color - Use Case
#21 - Red - Power
#20 - Brown - Power
#16 - Black - Capture
#12 - Orange - Gallery
#26 - Green - Down
#19 - Blue - Enter
#13 - Purple - Right
#6 - Grey - Left
#5 - White - Up

PIN_POWER1 = 21
PIN_POWER2 = 20
PIN_CAPTURE = 16
PIN_GALLERY = 12
PIN_ENTER = 19
PIN_UP = 5
PIN_RIGHT = 6
PIN_LEFT = 13
PIN_DOWN = 26

# Set Power Pin for Buttons
GPIO.setup(PIN_POWER1, GPIO.OUT)
GPIO.output(PIN_POWER1, GPIO.HIGH)
GPIO.setup(PIN_POWER2, GPIO.OUT)
GPIO.output(PIN_POWER2, GPIO.HIGH)
# Set input for all buttons
GPIO.setup(PIN_CAPTURE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_GALLERY, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_ENTER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_UP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def click_capture(channel):
    print("clicked capture")
    root.event_generate("s")

def click_gallery(channel):
    print("clicked gallery")
    root.event_generate("g")

def click_enter(channel):
    print("clicked enter")
    root.event_generate("<Return>")

def click_up(channel):
    print("clicked up")
    root.event_generate("<Up>")

def click_right(channel):
    print("clicked right")
    root.event_generate("<Right>")

def click_left(channel):
    print("clicked left")
    root.event_generate("<Left>")

def click_down(channel):
    print("clicked down")
    root.event_generate("<Down>")

GPIO.add_event_detect(PIN_CAPTURE, GPIO.FALLING, callback=click_capture, bouncetime=200)
GPIO.add_event_detect(PIN_GALLERY, GPIO.FALLING, callback=click_gallery, bouncetime=200)
GPIO.add_event_detect(PIN_ENTER, GPIO.FALLING, callback=click_enter, bouncetime=200)
GPIO.add_event_detect(PIN_UP, GPIO.FALLING, callback=click_up, bouncetime=200)
GPIO.add_event_detect(PIN_LEFT, GPIO.FALLING, callback=click_left, bouncetime=200)
GPIO.add_event_detect(PIN_RIGHT, GPIO.FALLING, callback=click_right, bouncetime=200)
GPIO.add_event_detect(PIN_DOWN, GPIO.FALLING, callback=click_down, bouncetime=200)


# Initialize OpenCV video capture
default_cam_capture = cv2.VideoCapture(DEFAULT_CAM_IDX)

# Start video updates
update_frame()

# Start the Tkinter event loop
try:
    root.mainloop()
except:
    GPIO.cleanup()
