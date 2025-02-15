from enum import Enum
import tkinter as tk

from gui.gallery import Gallery

class Dummy:
    def __init__(self):
        pass
    def open(self):
        print("opened dummy")

# Each one is triggered by <class>.open()
class Menu(Enum):
    GALLERY = Gallery
    OPTION = Dummy

class OverlayMenu:
    def __init__(self, root):
        """Initialize the menu with a root Tkinter window."""
        self.root = root
        self.menu_frame = None

        # Menu
        self.current_index = 0
        self.max_menu_items = 4
        gallery = Gallery(root)

        self.menu_items = [gallery, Dummy(), Dummy(), Dummy()]

        # Initialization function
        self.create_menu()


    def create_menu(self):
        """Create the overlay menu in the tkinter window."""
        self.menu_frame = tk.Frame(self.root, bg="black")
        
        # Position the menu at the bottom of the screen
        self.menu_frame.place(relx=0.5, rely=1.0, relwidth=1.0, relheight=0.2, anchor="s")
        
        option1 = tk.Button(self.menu_frame, text="Gallery")
        option1.pack(side=tk.LEFT, padx=20)
        
        option2 = tk.Button(self.menu_frame, text="Option 2")
        option2.pack(side=tk.LEFT, padx=20)

        option3 = tk.Button(self.menu_frame, text="Option 3")
        option3.pack(side=tk.LEFT, padx=20)

        option4 = tk.Button(self.menu_frame, text="Option 4")
        option4.pack(side=tk.LEFT, padx=20)
        

    def toggle_menu(self, event):
        """Toggle the visibility of the menu on pressing 'M'."""
        if self.menu_frame.winfo_ismapped():
            self.menu_frame.place_forget()  # Hide the menu
        else:
            # Show the menu at the bottom of the screen
            self.menu_frame.place(relx=0.5, rely=1.0, relwidth=1.0, relheight=0.2, anchor="s")


    def select(self, event):
        self.menu_items[self.current_index].open(event)

    
    def move_selector_left(self, event):
        """Shift the selected menu item left."""
        self.current_index = max(0, self.current_index-1)


    def move_selector_right(self, event):
        """Shift the selected menu item right."""
        self.current_index = min(self.max_menu_items-1, self.current_index+1)


