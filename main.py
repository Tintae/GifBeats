import tkinter as tk
from tkinter import ttk
from video_converter import Application


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()