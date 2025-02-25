import tkinter as tk

class Buttons:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(self.root, width=400, height=200, bg="white")
        self.canvas.pack()
        
        # Boolean states for each shape
        self.states = [False, False, False, False]
        
        # Coordinates for shapes (rectangles for now)
        self.shapes = [
            self.canvas.create_rectangle(50, 50, 100, 100, fill="red"),
            self.canvas.create_rectangle(120, 50, 170, 100, fill="red"),
            self.canvas.create_rectangle(190, 50, 240, 100, fill="red"),
            self.canvas.create_rectangle(260, 50, 310, 100, fill="red"),
        ]
        
        # Toggle button for testing
        self.toggle_button = tk.Button(self.root, text="Toggle", command=self.toggle_states)
        self.toggle_button.pack()
    
    def toggle_states(self):
        """Toggle the boolean values and update colors."""
        for i in range(len(self.states)):
            self.states[i] = not self.states[i]
            new_color = "green" if self.states[i] else "red"
            self.canvas.itemconfig(self.shapes[i], fill=new_color)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = Buttons(root)
    root.mainloop()