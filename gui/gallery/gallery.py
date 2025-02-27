import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Expand the home directory properly
LOCAL_DIRECTORY = "./gallery/local"
UPLOADED_DIRECTORY = "./gallery/uploaded"

class Gallery:
    def __init__(self, root, video_label, update_frame):
        """Initialize the gallery with a root Tkinter window."""
        self.root = root
        self.video_label = video_label
        self.update_frame = update_frame

        self.gallery_view = None
        self.image_frame = None
        self.image_refs = []

        self.create_gallery()
    
    def create_gallery(self):
        """Create a fullscreen gallery view with 3 columns of images and an exit button."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Create a full-screen frame
        self.gallery_view = tk.Frame(self.root, bg="black", width=screen_width, height=screen_height)
        self.gallery_view.pack(fill="both", expand=True)

        # Exit button (X in the top right corner)
        exit_button = tk.Button(self.gallery_view, text="X", font=("Arial", 8, "bold"),
                                fg="white", bg="red", command=self.close,
                                padx=5, pady=3, bd=2)
        exit_button.place(relx=0.98, rely=0.02, anchor="ne")  # Ensures top-right positioning

        # Create a frame for the images with extra padding at the top
        self.image_frame = tk.Frame(self.gallery_view, bg="white")
        self.image_frame.pack(fill="both", expand=True, padx=0, pady=(40, 0))  # Increased pady

        # Ensure columns expand properly
        for i in range(3):
            self.image_frame.grid_columnconfigure(i, weight=1)

        # Create column titles
        titles = ["Uploaded", "Local"]
        for i, title in enumerate(titles):
            label = tk.Label(self.image_frame, text=title, font=("Arial", 14, "bold"), bg="white")
            label.grid(row=0, column=i, padx=20, pady=10, sticky="n")

        self.load_uploaded_image()
        self.load_local_image()
    
    def load_local_image(self):
        """Load and display images in a 3-column format."""
        row = 1  # Start from row 1 since row 0 has titles
        col = 1
        
        for name in os.listdir(LOCAL_DIRECTORY):
            file_path = os.path.join(LOCAL_DIRECTORY, name)
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                img = Image.open(file_path)
                img.thumbnail((200, 200))  # Resize images to fit nicely
                img = ImageTk.PhotoImage(img)

                self.image_refs.append(img)

                # Create a label for the image
                img_label = tk.Label(self.image_frame, image=img, bg="white")
                img_label.grid(row=row, column=col, padx=20, pady=10)

                break

    def load_uploaded_image(self):
        """Load and display images in a 3-column format."""
        row = 1  # Start from row 1 since row 0 has titles
        col = 0
        
        for name in os.listdir(UPLOADED_DIRECTORY):
            file_path = os.path.join(UPLOADED_DIRECTORY, name)
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                img = Image.open(file_path)
                img.thumbnail((200, 200))  # Resize images to fit nicely
                img = ImageTk.PhotoImage(img)

                self.image_refs.append(img)

                # Create a label for the image
                img_label = tk.Label(self.image_frame, image=img, bg="white")
                img_label.grid(row=row, column=col, padx=20, pady=10)

                break


    def open(self):
        """Switch to the gallery view."""
        global gallery_active
        gallery_active = True
        self.video_label.pack_forget()  # Hide the video feed
        self.gallery_view.pack(fill="both", expand=True)

    def close(self, event=None):
        """Close the gallery and return to the video feed."""
        global gallery_active
        gallery_active = False
        self.gallery_view.pack_forget()  # Hide gallery
        self.image_frame.pack_forget()
        self.video_label.pack(fill="both", expand=True)  # Show video feed
        self.update_frame()  # Restart video updates