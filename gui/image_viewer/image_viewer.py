import tkinter as tk
from PIL import Image, ImageTk

class Image_Viewer:
    """A class to handle full-screen image viewing with navigation and togglable UI."""
    
    def __init__(self, root, image_paths, start_index, category):
        self.root = root
        self.image_paths = image_paths
        self.current_index = start_index
        self.category = category  # "local" or "uploaded"
        self.ui_visible = True  # UI is visible by default
        self.buttons = []  # Track buttons for navigation
        self.focus_index = 0  # Track the currently focused button

        # Hide previous view (gallery)
        for widget in self.root.winfo_children():
            widget.pack_forget()

        # Create a full-screen frame
        self.viewer_frame = tk.Frame(self.root, bg="black")
        self.viewer_frame.pack(fill="both", expand=True)

        # Set fullscreen mode
        self.root.attributes('-fullscreen', True)

        # Top bar (title)
        self.top_bar = tk.Frame(self.viewer_frame, bg="black")
        self.top_bar.pack(side="top", fill="x")

        title_text = "Viewing Uploaded Images" if category == "uploaded" else "Viewing Local Images"
        self.title_label = tk.Label(self.top_bar, text=title_text, font=("Arial", 16, "bold"), fg="white", bg="black")
        self.title_label.pack(pady=10)

        # Bottom bar (navigation buttons)
        self.bottom_bar = tk.Frame(self.viewer_frame, bg="black")
        self.bottom_bar.pack(side="bottom", fill="x", pady=10)

        # Right side container for both sets of buttons
        self.right_controls = tk.Frame(self.bottom_bar, bg="black")
        self.right_controls.pack(side="right", padx=20)

        # Left Controls (Hide UI & Close) - Placed together
        self.left_controls = tk.Frame(self.right_controls, bg="black")  # Inside right_controls
        self.left_controls.pack(side="left", padx=10)  # Positioned first (closer to center)

        self.hide_ui_button = tk.Button(self.left_controls, text="Hide UI", command=self.toggle_ui_mode, font=("Arial", 12))
        self.hide_ui_button.pack(side="left", padx=5)  # Place Hide UI button on the left

        self.close_button = tk.Button(self.left_controls, text="Close (Esc)", command=self.close_viewer, font=("Arial", 12))
        self.close_button.pack(side="left", padx=5)  # Place Close button next to Hide UI

        # Right Controls (← & →) - Placed beside each other
        self.nav_controls = tk.Frame(self.right_controls, bg="black")  # Inside right_controls
        self.nav_controls.pack(side="left", padx=10)  # Positioned next to left_controls

        self.prev_button = tk.Button(self.nav_controls, text="←", command=self.show_prev, font=("Arial", 20))
        self.prev_button.pack(side="left", padx=5)  # Place Left button on the left

        self.next_button = tk.Button(self.nav_controls, text="→", command=self.show_next, font=("Arial", 20))
        self.next_button.pack(side="left", padx=5)  # Place Right button next to Left button

        # Add buttons to navigation list
        self.buttons.extend([self.hide_ui_button, self.close_button, self.prev_button, self.next_button])

        # Image display area
        self.image_label = tk.Label(self.viewer_frame, bg="black")
        self.image_label.pack(expand=True)

        # Load the first image
        self.display_image()

        # Bind keyboard events
        self.root.bind("<Right>", lambda event: self.show_next() if not self.ui_visible else self.navigate_buttons(1))
        self.root.bind("<Left>", lambda event: self.show_prev() if not self.ui_visible else self.navigate_buttons(-1))
        self.root.bind("<Escape>", lambda event: self.close_viewer())
        self.root.bind("<Return>", lambda event: self.press_enter())
        self.root.bind("<Up>", lambda event: self.navigate_buttons(-1))
        self.root.bind("<Down>", lambda event: self.navigate_buttons(1))

        # Focus on first button
        self.set_focus(0)

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
            focused_widget = self.buttons[self.focus_index]
            focused_widget.invoke()  # Click the button
        else:
            self.toggle_ui_mode()  # Hide or show UI when Enter is pressed

    def navigate_buttons(self, direction):
        """Move focus between buttons using Up/Down/Left/Right arrows."""
        if not self.ui_visible:
            return  # Ignore navigation if UI is hidden

        # Move focus to the next button
        self.focus_index = (self.focus_index + direction) % len(self.buttons)
        self.set_focus(self.focus_index)

    def set_focus(self, index):
        """Sets focus on the specified button and highlights it."""
        for button in self.buttons:
            button.config(bg="white", fg="black")  # Reset all buttons
        self.buttons[index].config(bg="red", fg="white")  # Highlight focused button
        self.buttons[index].focus_set()  # Set keyboard focus

    def toggle_ui_mode(self):
        """Toggles between UI-visible mode and UI-hidden mode."""
        if self.ui_visible:
            # Hide UI
            self.top_bar.pack_forget()
            self.bottom_bar.pack_forget()
        else:
            # Show UI
            self.top_bar.pack(side="top", fill="x", before=self.image_label)
            self.bottom_bar.pack(side="bottom", fill="x", before=self.image_label)
            self.set_focus(0)  # Focus on the first button

        self.ui_visible = not self.ui_visible

    def close_viewer(self):
        """Close the image viewer and return to the gallery."""
        self.viewer_frame.pack_forget()
        self.root.attributes('-fullscreen', False)  # Exit fullscreen
        self.root.quit()  # Quit app (replace with code to return to gallery if needed)
