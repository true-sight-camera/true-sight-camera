import cv2
from datetime import datetime
import tkinter as tk
from tkinter import Label

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
    global cap
    cap.release()  # Release the video capture
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
    ret, frame = cap.read()
    if ret:
        current_frame = frame

        # Resize the frame to fit the Tkinter window
        screen_width = int(root.winfo_screenwidth())
        screen_height = int(root.winfo_screenheight())
        resized_frame = cv2.resize(frame, (screen_width, screen_height), interpolation=cv2.INTER_AREA)

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

# Initialize the OpenCV video capture
cap = cv2.VideoCapture(0)  # Use 0 for the default webcam

# Start updating the video feed
update_frame()

# Start the Tkinter event loop
root.mainloop()
