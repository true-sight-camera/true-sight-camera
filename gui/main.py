import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import Label
import RPi.GPIO as GPIO

import gui.image_processing as img_proc
from gui.menu import OverlayMenu
from gui.gallery import Gallery


# GLOBAL VARIABLES #
fullscreen = True  # Start in fullscreen mode
current_frame = None  # Store the current frame
gallery_active = False  # Track if the gallery is active
GALLERY_DIRECTORY = "./gallery"

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Full Screen Tkinter Window")
root.attributes("-fullscreen", fullscreen)

# Create a label to display the video feed
video_label = Label(root)
video_label.pack(fill=tk.BOTH, expand=True)

# FEATURES # 
overlay_menu = OverlayMenu(root)


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


def save_current_frame(event=None):
    """Save the current frame to a file."""
    print("Saving image")
    global current_frame
    if current_frame is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gallery/frame_{timestamp}.png"
        cv2.imwrite(filename, current_frame)
        print(f"Saved current frame as {filename}")
    else:
        print("No frame to save.")


def update_frame():
    """Update the video frame in the Tkinter window."""
    global current_frame
    if gallery_active:  # Stop updating if gallery is active
        return
    ret, frame = default_cam_capture.read()
    if ret:
        current_frame = frame

        # Resize the frame to fit the Tkinter window
        screen_width = int(root.winfo_screenwidth())
        screen_height = int(root.winfo_screenheight())
        resized_frame = cv2.resize(frame, (screen_width, screen_height))

        # Preprocess the image
        processed_frame = img_proc.process_image(resized_frame)
        
        # Convert to a Tkinter-compatible format
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
root.bind("m", overlay_menu.toggle_menu)
root.bind("<Return>", overlay_menu.select)

# GALLERY INTEGRATION #
gallery = Gallery(root, video_label, update_frame)

def toggle_gallery(event=None):
    """Toggle between the video feed and the gallery."""
    if gallery_active:
        gallery.close()
    else:
        gallery.open()

root.bind("g", toggle_gallery)  # Press "g" to switch to the gallery


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
    root.event_generate("g")

GPIO.add_event_detect(12, GPIO.FALLING, callback=click_picture, bouncetime=200)
GPIO.add_event_detect(13, GPIO.FALLING, callback=click_gallery, bouncetime=200)

# Initialize OpenCV video capture
default_cam_capture = cv2.VideoCapture(0)

# Start video updates
update_frame()

# Start the Tkinter event loop
try:
    root.mainloop()
except:
    GPIO.cleanup()
