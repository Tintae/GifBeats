import os
import pickle
import threading
import webbrowser
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
from utils import CreateToolTip, load_api_keys, save_api_keys
from tkcalendar import DateEntry
import datetime
import webbrowser
import tkinter as tk
from youtube_uploader import YouTubeUploader
#from instagram_uploader import InstagramUploader
#from tiktok_uploader import TikTokUploader

class UploaderFrame(tk.Toplevel):
    def __init__(self, master=None, video_path=None, aspect_ratio=None):
        super().__init__(master)
        self.video_path = video_path
        self.aspect_ratio = aspect_ratio
        self.title("Upload Video")
        self.geometry("400x800")
        self.configure(bg="#1f1f1f")
        self.create_widgets()

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
            "TEntry",
            fieldbackground="#4d4d4d",
            foreground="#ffffff",
            insertcolor="#ffffff",
            font=("Helvetica", 12),
            padding=5,
        )
        style.configure(
            "TCombobox",
            background="#4d4d4d",
            foreground="#ffffff",
            fieldbackground="#4d4d4d",
            selectbackground="#ff5500",
            selectforeground="#ffffff",
            font=("Helvetica", 12),
            padding=5,
        )

        self.platform_label = ttk.Label(self, text="Platform:")
        self.platform_label.pack(side="top", pady=10)
        CreateToolTip(self.platform_label, "Select the platform to upload your video")

        self.platform_var = tk.StringVar(value="YouTube")
        self.platform_combobox = ttk.Combobox(
            self, textvariable=self.platform_var, values=["YouTube", "Instagram", "TikTok"], style="TCombobox"
        )
        self.platform_combobox.pack(side="top", pady=5)
        self.platform_combobox.bind("<<ComboboxSelected>>", self.on_platform_selected)

        self.fields_frame = ttk.Frame(self)
        self.fields_frame.pack(side="top", pady=10, fill="x")

        self.youtube_fields()

        self.upload_button = ttk.Button(self, text="Upload", command=self.start_upload, style="TButton")
        self.upload_button.pack(side="top", pady=20)
        CreateToolTip(self.upload_button, "Start the video upload")

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy, style="TButton")
        self.cancel_button.pack(side="top", pady=10)
        CreateToolTip(self.cancel_button, "Cancel the upload and close the window")

    def on_platform_selected(self, event):
        selected_platform = self.platform_var.get()
        if selected_platform == "YouTube":
            self.youtube_fields()
        elif selected_platform == "Instagram":
            self.instagram_fields()
        elif selected_platform == "TikTok":
            self.tiktok_fields()

    def youtube_fields(self):
        self.clear_fields()

        self.title_label = ttk.Label(self.fields_frame, text="Title:")
        self.title_label.pack(side="top", pady=10)
        self.title_entry = ttk.Entry(self.fields_frame, width=40)
        self.title_entry.pack(side="top", pady=5)

        self.description_label = ttk.Label(self.fields_frame, text="Description:")
        self.description_label.pack(side="top", pady=10)
        self.description_entry = ttk.Entry(self.fields_frame, width=40)
        self.description_entry.pack(side="top", pady=5)

        self.tags_label = ttk.Label(self.fields_frame, text="Tags (comma-separated):")
        self.tags_label.pack(side="top", pady=10)
        self.tags_entry = ttk.Entry(self.fields_frame, width=40)
        self.tags_entry.pack(side="top", pady=5)

        self.privacy_label = ttk.Label(self.fields_frame, text="Privacy:")
        self.privacy_label.pack(side="top", pady=10)
        self.privacy_var = tk.StringVar(value="private")
        self.privacy_combobox = ttk.Combobox(
            self.fields_frame, textvariable=self.privacy_var, values=["private", "unlisted", "public"], style="TCombobox"
        )
        self.privacy_combobox.pack(side="top", pady=5)

        self.schedule_label = ttk.Label(self.fields_frame, text="Schedule:")
        self.schedule_label.pack(side="top", pady=10)

        self.schedule_frame = ttk.Frame(self.fields_frame, style="TFrame")
        self.schedule_frame.pack(side="top", pady=5)

        self.date_label = ttk.Label(self.schedule_frame, text="Date:")
        self.date_label.pack(side="left", padx=5)
        self.date_entry = DateEntry(
            self.schedule_frame,
            width=12,
            background="#4d4d4d",
            foreground="#ffffff",
            borderwidth=0,
            font=("Helvetica", 12),
        )
        self.date_entry.pack(side="left", padx=5)

        self.time_label = ttk.Label(self.schedule_frame, text="Time:")
        self.time_label.pack(side="left", padx=5)

        current_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        time_options = []
        for _ in range(48):
            time_options.append(current_time.strftime("%I:%M %p"))
            current_time += datetime.timedelta(minutes=30)

        self.time_combobox = ttk.Combobox(
            self.schedule_frame, width=8, values=time_options, style="TCombobox"
        )
        self.time_combobox.pack(side="left", padx=5)
        
        self.timezone_label = ttk.Label(self.schedule_frame, text="Time Zone:")
        self.timezone_label.pack(side="left", padx=5)

        timezone_options = ["Eastern", "Central", "Western"]
        self.timezone_var = tk.StringVar(value="Eastern")
        self.timezone_combobox = ttk.Combobox(
            self.schedule_frame, width=8, textvariable=self.timezone_var, values=timezone_options, style="TCombobox"
        )
        self.timezone_combobox.pack(side="left", padx=5)

    def instagram_fields(self):
        self.clear_fields()

        self.caption_label = ttk.Label(self.fields_frame, text="Caption:")
        self.caption_label.pack(side="top", pady=10)
        self.caption_entry = ttk.Entry(self.fields_frame, width=40)
        self.caption_entry.pack(side="top", pady=5)

    def tiktok_fields(self):
        self.clear_fields()

        self.description_label = ttk.Label(self.fields_frame, text="Description:")
        self.description_label.pack(side="top", pady=10)
        self.description_entry = ttk.Entry(self.fields_frame, width=40)
        self.description_entry.pack(side="top", pady=5)

    def clear_fields(self):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

    def start_upload(self):
        selected_platform = self.platform_var.get()
        if selected_platform == "YouTube":
            self.upload_to_youtube()
        elif selected_platform == "Instagram":
            self.upload_to_instagram()
        elif selected_platform == "TikTok":
            self.upload_to_tiktok()

    def upload_to_youtube(self):
        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = [tag.strip() for tag in self.tags_entry.get().split(",")]
        privacy_status = self.privacy_var.get()

        schedule_date = self.date_entry.get_date()
        schedule_time = self.time_combobox.get()
        selected_timezone = self.timezone_var.get()

        if selected_timezone == "Eastern":
            local_timezone = datetime.timezone(datetime.timedelta(hours=-4))
        elif selected_timezone == "Central":
            local_timezone = datetime.timezone(datetime.timedelta(hours=-5))
        elif selected_timezone == "Western":
            local_timezone = datetime.timezone(datetime.timedelta(hours=-7))

        if schedule_date and schedule_time:
            schedule_datetime = datetime.datetime.combine(
                schedule_date,
                datetime.datetime.strptime(schedule_time, "%I:%M %p").time()
            )
            schedule_datetime = schedule_datetime.replace(tzinfo=local_timezone)
            publish_at = schedule_datetime.astimezone(datetime.timezone.utc).isoformat()
        else:
            publish_at = None

        youtube_uploader = YouTubeUploader(self.video_path, self.aspect_ratio, title, description, tags, privacy_status, publish_at)
        threading.Thread(target=youtube_uploader.upload_video).start()

        youtube_uploader = YouTubeUploader(self.video_path, self.aspect_ratio, title, description, tags, privacy_status, publish_at)
        threading.Thread(target=youtube_uploader.upload_video).start()

    def upload_to_instagram(self):
        caption = self.caption_entry.get()
        instagram_uploader = InstagramUploader(self.video_path, self.aspect_ratio, caption)
        threading.Thread(target=instagram_uploader.upload_video).start()

    def upload_to_tiktok(self):
        description = self.description_entry.get()
        tiktok_uploader = TikTokUploader(self.video_path, self.aspect_ratio, description)
        threading.Thread(target=tiktok_uploader.upload_video).start()