import cv2
from datetime import datetime
import tkinter as tk
from tkinter import Label
import RPi.GPIO as GPIO

import gui.image_processing as img_proc
from gui.menu import OverlayMenu


# GLOBAL VARIABLES #
fullscreen = True  # Start in fullscreen mode
current_frame = None  # Store the current frame

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
    ret, frame = default_cam_capture.read()
    if ret:
        current_frame = frame

        # Resize the frame to fit the Tkinter window
        screen_width = int(root.winfo_screenwidth())
        screen_height = int(root.winfo_screenheight())
        resized_frame = cv2.resize(frame, (screen_width, screen_height))

        # Preprocess the image in place
        processed_frame = img_proc.process_image(resized_frame)
        
        # Convert the frame to a Tkinter PhotoImage object
        img = tk.PhotoImage(master=root, width=screen_width, height=screen_height,
                            data=cv2.imencode('.ppm', processed_frame)[1].tobytes())
        
        # Update the label with the image
        video_label.config(image=img)
        video_label.imgtk = img  # Store a reference to avoid garbage collection
    
    # Schedule the next frame update
    video_label.after(5, update_frame)

# BINDINGS #

# Bind keys for toggling and exiting fullscreen mode
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_fullscreen)

# Bind the "s" key to save the current frame
root.bind("s", save_current_frame)

# Bind the "m" key to toggle the menu
root.bind("m", overlay_menu.toggle_menu)

# Bind the "Enter" key to select the current menu option
root.bind("<Return>", overlay_menu.select)


# The 5 volt pin
GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT)
GPIO.output(21, GPIO.HIGH)


GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def click_left():
    print("LEFT")
    root.event_generate("<Left>")

def click_right():
    print("RIGHT")
    root.event_generate("<Right>")

def click_up():
    print("UP")
    root.event_generate("<Up>")

def click_down():
    print("DOWN")
    root.event_generate("<Down>")

def click_ok():
    print("OK")
    root.event_generate("<Return>")

def click_picture():
    print("PICTURE")
    root.event_generate("s")

GPIO.add_event_detect(19, GPIO.FALLING, callback=click_left, bouncetime=200)
GPIO.add_event_detect(16, GPIO.FALLING, callback=click_right, bouncetime=200)
GPIO.add_event_detect(26, GPIO.FALLING, callback=click_up, bouncetime=200)
GPIO.add_event_detect(20, GPIO.FALLING, callback=click_down, bouncetime=200)
GPIO.add_event_detect(13, GPIO.FALLING, callback=click_ok, bouncetime=200)
GPIO.add_event_detect(12, GPIO.FALLING, callback=click_picture, bouncetime=200)

# Initialize the OpenCV video capture
default_cam_capture = cv2.VideoCapture(0)  # Use 0 for the default webcam

# Start updating the video feed
update_frame()

# Start the Tkinter event loop
try:
    root.mainloop()
except:
    GPIO.cleanup()
