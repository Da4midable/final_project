import tkinter as tk

root = tk.Tk()

def on_click():
    print("Button clicked!")

# Create a button
button = tk.Button(root, text="Click Me", command=on_click)

# Place the button on the window
button.pack()

root.mainloop()
