import os
import cv2
import tkinter as tk
from PIL import Image, ImageTk

from gui.image_viewer.image_viewer import Image_Viewer

# Expand the home directory properly
LOCAL_DIRECTORY = "./gallery/local"
UPLOADED_DIRECTORY = "./gallery/uploaded"

class Gallery:
    def __init__(self, root, video_label, update_frame, toggle_gallery):
        """Initialize the gallery with a root Tkinter window."""
        self.root = root
        self.video_label = video_label
        self.update_frame = update_frame
        self.toggle_gallery = toggle_gallery

        self.gallery_view = None
        self.image_frame = None
        self.image_refs = []
        
        self.buttons = []  # Store buttons for navigation

        self.create_gallery()
        self.focus_index = 0
        self.set_focus(0)  # Start focus on the first button

        # Bind keys for navigation
        self.root.bind("<Right>", lambda event: self.navigate_buttons(1))  # Move right
        self.root.bind("<Left>", lambda event: self.navigate_buttons(-1))  # Move left
        self.root.bind("<Up>", lambda event: self.navigate_buttons(-2))  # Move up (Exit button)
        self.root.bind("<Down>", lambda event: self.navigate_buttons(2))  # Move down (Image buttons)
        self.root.bind("<Return>", lambda event: self.press_enter())  # Activate button

    def create_gallery(self):
        """Create a fullscreen gallery view with 2 images and an exit button."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Create a full-screen frame
        self.gallery_view = tk.Frame(self.root, bg="black", width=screen_width, height=screen_height)
        self.gallery_view.pack(fill="both", expand=True)

        # ✅ Create a Compact Top Bar
        self.top_bar = tk.Frame(self.gallery_view, bg="black")  # Match Image Viewer height
        self.top_bar.pack(side="top", fill="x")
        

        # ✅ Exit button (properly aligned inside top bar)
        exit_button = tk.Button(self.top_bar, text="✖", font=("Arial", 16, "bold"), fg="white", bg="red", command=self.close)
        exit_button.pack(side="right", padx=10)  # ✅ Same spacing as Image Viewer
        self.buttons.append(exit_button)  # ✅ Add Exit button to navigable buttons

        # ✅ Create a frame for images (centered layout)
        self.image_frame = tk.Frame(self.gallery_view, bg="white")
        self.image_frame.pack(expand=True)  # Centering the image frame

        # Ensure columns expand properly (for proper centering)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(1, weight=1)

        # ✅ Create column titles (centered)
        titles = ["Uploaded", "Local"]
        for i, title in enumerate(titles):
            label = tk.Label(self.image_frame, text=title, font=("Arial", 14, "bold"), bg="white")
            label.grid(row=0, column=i, padx=20, pady=10, sticky="n")

        self.load_uploaded_image()
        self.load_local_image()

    def load_local_image(self):
        """Load and display a local image as a button."""
        row, col = 1, 1  # Position for the local image

        img_paths = sorted(
            [os.path.join(LOCAL_DIRECTORY, name) for name in os.listdir(LOCAL_DIRECTORY)
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))],
            reverse=True
        )

        if img_paths:
            img_path = img_paths[0]  # Load only one image
            img = Image.open(img_path)
            img.thumbnail((200, 200))
            img = ImageTk.PhotoImage(img)

            self.image_refs.append(img)
            img_button = tk.Button(self.image_frame, image=img, bg="white",
                                command=lambda: self.open_image_viewer(img_paths, 0, "Local"))
            img_button.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")  # ✅ Ensures centering
            self.buttons.append(img_button)  # ✅ Add local image button to navigation

    def load_uploaded_image(self):
        """Load and display an uploaded image as a button."""
        row, col = 1, 0  # Position for the uploaded image

        img_paths = sorted(
            [os.path.join(UPLOADED_DIRECTORY, name) for name in os.listdir(UPLOADED_DIRECTORY)
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))],
            reverse=True
        )

        if img_paths:
            img_path = img_paths[0]  # Load only one image
            img = Image.open(img_path)
            img.thumbnail((200, 200))
            img = ImageTk.PhotoImage(img)

            self.image_refs.append(img)
            img_button = tk.Button(self.image_frame, image=img, bg="white",
                                command=lambda: self.open_image_viewer(img_paths, 0, "Uploaded"))
            img_button.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")  # ✅ Ensures centering
            self.buttons.append(img_button)  # ✅ Add uploaded image button to navigation

    def open_image_viewer(self, image_paths, start_index, category):
        """Open Image_Viewer for selected category."""
        Image_Viewer(self.root, image_paths, start_index, category, self)

    def navigate_buttons(self, direction):
        """Move focus between Exit and Image Buttons using Up/Down/Left/Right arrows."""
        if not self.buttons:
            return

        if direction == -2:  # Move Up (to Exit button)
            self.focus_index = 0
        elif direction == 2:  # Move Down (to image buttons)
            self.focus_index = 1  # First image button
        else:  # Move Left/Right within buttons
            self.focus_index = (self.focus_index + direction) % len(self.buttons)

        self.set_focus(self.focus_index)

    def set_focus(self, index):
        """Sets focus on the specified button and highlights it."""
        for idx, button in enumerate(self.buttons):
            if idx == 0:
                button.config(bg="red", fg="white") # X button
                continue

            button.config(bg="white", fg="black")  # Reset all buttons

        self.buttons[index].config(bg="royalblue", fg="white")  # Highlight focused button
        self.buttons[index].focus_set()  # Set keyboard focus

        self.focus_index = index

    def press_enter(self):
        """Presses the currently focused button."""
        self.buttons[self.focus_index].invoke()  # Click the focused button

    def open(self):
        """Switch to the gallery view."""
        global gallery_active
        gallery_active = True

        self.buttons.pop()
        self.buttons.pop()

        # Reload the images
        self.load_uploaded_image()
        self.load_local_image()

        self.video_label.pack_forget()  # Hide the video feed
        self.gallery_view.pack(fill="both", expand=True)
        self.root.bind("<Right>", lambda event: self.navigate_buttons(1))  # Move right
        self.root.bind("<Left>", lambda event: self.navigate_buttons(-1))  # Move left
        self.root.bind("<Up>", lambda event: self.navigate_buttons(-2))  # Move up (Exit button)
        self.root.bind("<Down>", lambda event: self.navigate_buttons(2))  # Move down (Image buttons)
        self.root.unbind("<Return")
        self.root.bind("<Return>", lambda event: self.press_enter())  # Activate button
        self.focus_index = 0
        self.set_focus(0)  # Start focus on Exit button

    def close(self, event=None):
        """Close the gallery and return to the video feed."""
        # ✅ Hide the gallery properly
        if self.gallery_view:
            self.gallery_view.pack_forget()

        # ✅ Show video feed again
        if self.video_label:
            self.video_label.pack(fill="both", expand=True)

        # ✅ Unbind navigation keys to avoid interference
        self.root.unbind("<Right>")
        self.root.unbind("<Left>")
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")
        # self.root.unbind("<Return>")

        self.toggle_gallery()
        
        # # ✅ Restart video feed (fixes white screen issue)
        # self.root.after(5, self.update_frame)

