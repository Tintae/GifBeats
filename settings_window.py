import tkinter as tk
from tkinter import ttk
from utils import CreateToolTip, load_api_keys, save_api_keys
from tkinter import ttk
import webbrowser

class SettingsWindow(tk.Toplevel):
    def __init__(self, master=None, settings=None):
        super().__init__(master)
        self.settings = settings
        self.title("Settings")
        self.geometry("800x400")
        self.configure(bg="#1f1f1f")
        self.create_widgets()
        self.load_api_keys()

    def create_widgets(self):
        style = ttk.Style()
        style.configure(
            "TLabel",
            background="#1f1f1f",
            foreground="#ffffff",
            font=("Helvetica", 12),
            padding=5,
        )
        style.configure(
            "TButton",
            background="#ff5500",
            foreground="#ffffff",
            font=("Helvetica", 12, "bold"),
            padding=10,
            relief="flat",
            borderwidth=0,
            borderradius=20,
            width=10,
            height=10,
        )
        style.map("TButton", background=[("active", "#ff8c00"), ("disabled", "#4d4d4d")])
        style.configure(
            "TCheckbutton",
            background="#1f1f1f",
            foreground="#ffffff",
            font=("Helvetica", 12),
            padding=5,
        )
        style.configure(
            "TEntry",
            fieldbackground="#4d4d4d",
            foreground="#ffffff",
            insertcolor="#ffffff",
            font=("Helvetica", 12),
            padding=5,
        )

        self.custom_resolution_var = tk.BooleanVar(
            value=self.settings["custom_resolution"]
        )
        self.custom_resolution_checkbox = ttk.Checkbutton(
            self,
            text="Custom Resolution",
            variable=self.custom_resolution_var,
            command=self.toggle_resolution_fields,
        )
        self.custom_resolution_checkbox.pack(side="top", pady=10)
        CreateToolTip(
            self.custom_resolution_checkbox, "Set custom output video resolution"
        )

        self.resolution_frame = ttk.Frame(self)
        self.resolution_frame.pack(side="top", pady=10)

        self.width_label = ttk.Label(self.resolution_frame, text="Width:")
        self.width_label.pack(side="left", padx=5)

        self.width_entry = ttk.Entry(self.resolution_frame, width=10)
        self.width_entry.pack(side="left", padx=5)
        self.width_entry.insert(0, str(self.settings["width"]))

        self.height_label = ttk.Label(self.resolution_frame, text="Height:")
        self.height_label.pack(side="left", padx=5)

        self.height_entry = ttk.Entry(self.resolution_frame, width=10)
        self.height_entry.pack(side="left", padx=5)
        self.height_entry.insert(0, str(self.settings["height"]))

        self.api_frame = ttk.Frame(self)
        self.api_frame.pack(side="top", pady=10)

        self.client_id_label = ttk.Label(self.api_frame, text="Client ID:")
        self.client_id_label.pack(side="left", padx=5)

        self.client_id_entry = ttk.Entry(self.api_frame, width=30)
        self.client_id_entry.pack(side="left", padx=5)

        self.client_secret_label = ttk.Label(self.api_frame, text="Client Secret:")
        self.client_secret_label.pack(side="left", padx=5)

        self.client_secret_entry = ttk.Entry(self.api_frame, width=30, show="*")
        self.client_secret_entry.pack(side="left", padx=5)

        self.api_button_frame = ttk.Frame(self)
        self.api_button_frame.pack(side="top", pady=5)

        self.api_button = ttk.Button(
            self.api_button_frame,
            text="Google API Console",
            command=self.open_api_console,
        )
        self.api_button.pack(side="left", padx=5)
        CreateToolTip(
            self.api_button,
            "Open the Google API Console to create or manage your API credentials",
        )

        self.toggle_resolution_fields()

        self.save_button = ttk.Button(self, text="Save", command=self.save_settings)
        self.save_button.pack(side="top", pady=20)
        CreateToolTip(self.save_button, "Save the settings")

    def toggle_resolution_fields(self):
        if self.custom_resolution_var.get():
            self.width_entry.state(["!disabled"])
            self.height_entry.state(["!disabled"])
        else:
            self.width_entry.state(["disabled"])
            self.height_entry.state(["disabled"])

    def load_api_keys(self):
        client_id, client_secret = load_api_keys()
        self.client_id_entry.delete(0, tk.END)
        self.client_id_entry.insert(0, client_id)
        self.client_secret_entry.delete(0, tk.END)
        self.client_secret_entry.insert(0, client_secret)

    def open_api_console(self):
        webbrowser.open("https://console.developers.google.com/apis/dashboard")

    def save_settings(self):
        self.settings["custom_resolution"] = self.custom_resolution_var.get()
        self.settings["width"] = int(self.width_entry.get())
        self.settings["height"] = int(self.height_entry.get())
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        save_api_keys(client_id, client_secret)
        self.destroy()