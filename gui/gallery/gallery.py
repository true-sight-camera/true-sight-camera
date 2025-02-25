import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Expand the home directory properly
GALLERY_DIRECTORY = "./gallery"

class Gallery:
    def __init__(self, root):
        """Initialize the gallery with a root Tkinter window."""
        self.root = root
        self.gallery_view = None
        self.image_frame = None
        self.image_paths = []  # List to store image file paths
        self.images = []       # List to store PhotoImage references

        self.create_gallery()
    
    def create_gallery(self):
        """Create a fullscreen gallery view."""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Create a full-screen frame
        self.gallery_view = tk.Frame(self.root, bg="black", width=screen_width, height=screen_height)
        self.gallery_view.pack(fill="both", expand=True)

        # Create a frame for the images
        self.image_frame = tk.Frame(self.gallery_view, bg="white")
        self.image_frame.pack(fill="both", expand=True, padx=20, pady=20)

        print("Current Directory:", os.getcwd())
        print("Files in current directory:", os.listdir('.'))

        # Iterate over files in the gallery directory and store valid image paths
        for name in os.listdir(GALLERY_DIRECTORY):
            file_path = os.path.join(GALLERY_DIRECTORY, name)
            # Optionally filter by extension
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self.image_paths.append(file_path)
        
        self.load_images()
    
    def load_images(self):
        """Load images from the gallery directory using OpenCV and display them."""
        for i, img_path in enumerate(self.image_paths):
            try:
                # Load image using OpenCV
                img = cv2.imread(img_path)
                if img is None:
                    print(f"Failed to load {img_path}")
                    continue
                # Convert from BGR to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Resize the image (e.g., 100x100 pixels)
                img = cv2.resize(img, (100, 100))
                # Convert the image to a PIL Image then to a Tkinter PhotoImage
                img_pil = Image.fromarray(img)
                photo = ImageTk.PhotoImage(img_pil)
                self.images.append(photo)  # Prevent garbage collection

                # Create a label for the image and add it to a grid layout
                label = tk.Label(self.image_frame, image=photo, bg="white")
                label.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            except Exception as e:
                print(f"Error loading {img_path}: {e}")

    def open(self, event):
        """Toggle visibility of the gallery."""
        if self.gallery_view.winfo_ismapped():
            self.gallery_view.place_forget()  # Hide the gallery
        else:
            self.gallery_view.place(relx=0.5, rely=0.5, anchor="center")  # Show in center

