import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

def create_test_window():
    root = ThemedTk(theme="arc")
    root.title("GUI Test")
    root.geometry("400x300")
    
    # Create a label
    label = ttk.Label(root, text="GUI Test Window")
    label.pack(pady=20)
    
    # Create a button
    button = ttk.Button(root, text="Test Button")
    button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    create_test_window()
