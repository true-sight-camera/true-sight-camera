import tkinter as tk
from PIL import Image, ImageTk
import os

class Image_Viewer:
    """A class to handle full-screen image viewing with navigation and togglable UI."""
    
    def __init__(self, root, image_paths, start_index, category, gallery):
        self.root = root
        self.image_paths = image_paths
        self.current_index = start_index
        self.category = category  # "local" or "uploaded"
        self.ui_visible = True  # UI is visible by default
        self.bottom_buttons = []  # Track buttons for navigation
        self.top_buttons = []
        self.focus_index = [0, 0]  # Track the currently focused button
        self.gallery = gallery

        # Hide previous view (gallery)
        for widget in self.root.winfo_children():
            widget.pack_forget()

        # Create a full-screen frame
        self.viewer_frame = tk.Frame(self.root, bg="black")
        self.viewer_frame.pack(fill="both", expand=True)

        # Set fullscreen mode
        self.root.attributes('-fullscreen', True)

        # Top bar (title with buttons)
        self.top_bar = tk.Frame(self.viewer_frame, bg="black")
        self.top_bar.pack(side="top", fill="x")

        # Back button to return to the gallery
        self.back_button = tk.Button(self.top_bar, text="⬅", font=("Arial", 16), fg="white", bg="gray",
                                    command=self.return_to_gallery)
        self.back_button.pack(side="left", padx=10, pady=5)

        # Title in the center
        title_text = "Uploaded Images" if category == "Uploaded" else "Local Images"
        self.title_label = tk.Label(self.top_bar, text=title_text, font=("Arial", 16, "bold"), fg="white", bg="black")
        self.title_label.pack(side="left", expand=True)

        # X button to return to the main view
        self.close_view_button = tk.Button(self.top_bar, text="✖", font=("Arial", 16, "bold"), fg="white", bg="red",
                                        command=self.return_to_main_view)
        self.close_view_button.pack(side="right", padx=10, pady=5)

        self.top_buttons.extend([self.back_button, self.close_view_button])


        # Bottom bar (navigation buttons)
        self.bottom_bar = tk.Frame(self.viewer_frame, bg="black")
        self.bottom_bar.pack(side="bottom", fill="x", pady=10)

        # ✅ Left side container (for Hide UI, Delete, Upload)
        self.left_controls = tk.Frame(self.bottom_bar, bg="black")
        self.left_controls.pack(side="left", padx=20)  # ✅ Now correctly positioned on the left

        self.hide_ui_button = tk.Button(self.left_controls, text="Hide UI", command=self.toggle_ui_mode, font=("Arial", 12))
        self.hide_ui_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(self.left_controls, text="Delete", command=self.delete_image, font=("Arial", 12))
        self.delete_button.pack(side="left", padx=5)

        if category == "Local":
            self.upload_button = tk.Button(self.left_controls, text="Upload", command=self.delete_image, font=("Arial", 12))
            self.upload_button.pack(side="left", padx=5)

        # ✅ Right side container (for navigation buttons)
        self.right_controls = tk.Frame(self.bottom_bar, bg="black")
        self.right_controls.pack(side="right", padx=20)  # ✅ Now correctly positioned on the right

        self.prev_button = tk.Button(self.right_controls, text="⬅", command=self.show_prev, font=("Arial", 14, "bold"))
        self.prev_button.pack(side="left", padx=5)

        self.next_button = tk.Button(self.right_controls, text="➡", command=self.show_next, font=("Arial", 14, "bold"))
        self.next_button.pack(side="left", padx=5)

        # Add buttons to navigation list
        if category == "Local":
            self.bottom_buttons.extend([self.hide_ui_button, self.delete_button, self.upload_button, self.prev_button, self.next_button])
        else:
            self.bottom_buttons.extend([self.hide_ui_button, self.delete_button, self.prev_button, self.next_button])

        # Image display area
        self.image_label = tk.Label(self.viewer_frame, bg="black")
        self.image_label.pack(expand=True)

        # Load the first image
        self.display_image()

        # Bind keyboard events
        self.root.bind("<Right>", lambda event: self.show_next() if not self.ui_visible else self.navigate_buttons("right"))
        self.root.bind("<Left>", lambda event: self.show_prev() if not self.ui_visible else self.navigate_buttons("left"))
        self.root.bind("<Escape>", lambda event: self.close_viewer())
        self.root.bind("<Return>", lambda event: self.press_enter())
        self.root.bind("<Up>", lambda event: self.navigate_buttons("up"))
        self.root.bind("<Down>", lambda event: self.navigate_buttons("down"))

        # Focus on first button
        self.focus_index = [0, 0]
        self.set_focus(self.focus_index)

    def display_image(self):
        """Display the current image while preserving aspect ratio."""
        img_path = self.image_paths[self.current_index]
        img = Image.open(img_path)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Compute the max image size while keeping aspect ratio
        img_aspect = img.width / img.height
        screen_aspect = screen_width / screen_height

        if img_aspect > screen_aspect:
            # Image is wider than the screen aspect ratio
            new_width = screen_width
            new_height = int(screen_width / img_aspect)
        else:
            # Image is taller than the screen aspect ratio
            new_height = screen_height
            new_width = int(screen_height * img_aspect)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)

        self.image_label.config(image=self.tk_img)

    def show_next(self):
        """Show the next image in the folder."""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.display_image()

    def show_prev(self):
        """Show the previous image in the folder."""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()

    def press_enter(self):
        """Presses the currently focused button or toggles UI if hidden."""
        if self.ui_visible:
            x = self.focus_index[0]
            y = self.focus_index[1]

            if y == 0:
                focused_widget = self.bottom_buttons[x]
            else:
                focused_widget = self.top_buttons[x]

            focused_widget.invoke()  # Click the button
        else:
            self.toggle_ui_mode()  # Hide or show UI when Enter is pressed

    def navigate_buttons(self, direction):
        """Move focus between buttons using Up/Down/Left/Right arrows."""
        if not self.ui_visible:
            return  # Ignore navigation if UI is hidden
        
        if direction == "up":
            self.focus_index[1] = (self.focus_index[1] + 1) % 2
            if self.focus_index[1] == 1 and self.focus_index[0] >= len(self.top_buttons):
                self.focus_index[0] = 0
        elif direction == "down":
            self.focus_index[1] = (self.focus_index[1] - 1) % 2
            if self.focus_index[1] == 1 and self.focus_index[0] >= len(self.top_buttons):
                self.focus_index[0] = 0
        elif direction == "right":
            if self.focus_index[1] == 1:
                self.focus_index[0] = (self.focus_index[0] + 1) % len(self.top_buttons)
            else:
                self.focus_index[0] = (self.focus_index[0] + 1) % len(self.bottom_buttons)
        elif direction == "left":
            if self.focus_index[1] == 1:
                self.focus_index[0] = (self.focus_index[0] - 1) % len(self.top_buttons)
            else:
                self.focus_index[0] = (self.focus_index[0] - 1) % len(self.bottom_buttons)

        self.set_focus(self.focus_index)

    def set_focus(self, index):
        """Sets focus on the specified button and highlights it."""
        for button in self.bottom_buttons:
            button.config(bg="white", fg="black")  # Reset all buttons
        
        self.top_buttons[0].config(fg="white", bg="gray")
        self.top_buttons[1].config(fg="white", bg="red")

        x = index[0]
        y = index[1]

        if y == 0:
            self.bottom_buttons[x].config(bg="royalblue", fg="white")
            self.bottom_buttons[x].focus_set()
        elif y == 1:
            self.top_buttons[x].config(bg="royalblue", fg="white")
            self.top_buttons[x].focus_set()

    def toggle_ui_mode(self):
        """Toggles between UI-visible mode and UI-hidden mode."""
        if self.ui_visible:
            # Hide UI
            self.top_bar.pack_forget()
            self.bottom_bar.pack_forget()
        else:
            # Show UI
            self.top_bar.pack(side="top", fill="x", before=self.image_label)
            self.bottom_bar.pack(side="bottom", fill="x", pady=10, before=self.image_label)
            self.focus_index = [0, 0]
            self.set_focus(self.focus_index)  # Focus on the first button

        self.ui_visible = not self.ui_visible

    def close_viewer(self):
        """Close the image viewer and return to the gallery."""
        self.viewer_frame.pack_forget()
        self.root.attributes('-fullscreen', False)  # Exit fullscreen
        self.root.quit()  # Quit app (replace with code to return to gallery if needed)
    
    def show_no_images_message(self):
        """Displays 'No Images Left' message in the center."""
        self.image_label.config(image="")  # Clear any previous image
        self.image_label.config(text="No Images Left", font=("Arial", 20, "bold"), fg="white", bg="black")

    def delete_image(self):
        """Deletes the current image and moves to the next one or shows a message if none remain."""
        if not self.image_paths:
            return  # No images left

        img_path = self.image_paths[self.current_index]

        try:
            os.remove(img_path)  # Delete the file
            print(f"Deleted: {img_path}")

            # Remove from the list
            del self.image_paths[self.current_index]

            if self.image_paths:
                # If images remain, show the next or previous one
                if self.current_index >= len(self.image_paths):  # If last image was deleted
                    self.current_index -= 1  # Move to previous
                self.display_image()
            else:
                # No images left → Show "No Images Left" message
                self.show_no_images_message()

        except Exception as e:
            print(f"Error deleting {img_path}: {e}")
    
    def return_to_gallery(self):
        """Closes the viewer and returns to the gallery."""
        self.viewer_frame.pack_forget()
        if self.gallery:  # ✅ Ensure gallery is available
            self.gallery.open()
        else:
            print("Error: No gallery instance available!")  # ✅ Debugging message


    def return_to_main_view(self):
        """Closes the viewer and returns to the main video feed."""
        self.viewer_frame.pack_forget()

        if self.gallery.video_label:
            self.gallery.video_label.pack(fill="both", expand=True)

        self.root.unbind("<Right>")
        self.root.unbind("<Left>")
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")

        self.gallery.toggle_gallery()

