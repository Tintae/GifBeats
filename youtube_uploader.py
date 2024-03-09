import os
import pickle
import threading
import webbrowser
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tkinter import filedialog, messagebox, ttk
from tkcalendar import DateEntry
from utils import CreateToolTip, load_api_keys, save_api_keys
from tkcalendar import DateEntry
import datetime
import webbrowser
import tkinter as tk

class YouTubeUploaderFrame(tk.Toplevel):
    def __init__(self, master=None, video_path=None):
        super().__init__(master)
        self.video_path = video_path
        self.title("Upload to YouTube")
        self.geometry("400x750")
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
            "TEntry",
            fieldbackground="#4d4d4d",
            foreground="#ffffff",
            insertcolor="#ffffff",
            font=("Helvetica", 12),
            padding=5,
        )
        style.configure(
            "TRadiobutton",
            background="#1f1f1f",
            foreground="#ffffff",
            font=("Helvetica", 12),
            padding=5,
        )
        style.configure(
            "Treeview",
            background="#4d4d4d",
            foreground="#ffffff",
            fieldbackground="#4d4d4d",
            font=("Helvetica", 12),
            rowheight=25,
        )
        style.configure(
            "Treeview.Heading",
            background="#ff5500",
            foreground="#ffffff",
            font=("Helvetica", 12, "bold"),
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#ff8c00")],
        )

        self.title_label = ttk.Label(self, text="Title:")
        self.title_label.pack(side="top", pady=10)
        CreateToolTip(self.title_label, "Enter the title for your YouTube video")

        self.title_entry = ttk.Entry(self, width=40)
        self.title_entry.pack(side="top", pady=5)

        self.description_label = ttk.Label(self, text="Description:")
        self.description_label.pack(side="top", pady=10)
        CreateToolTip(
            self.description_label, "Enter the description for your YouTube video"
        )

        self.description_entry = ttk.Entry(self, width=40)
        self.description_entry.pack(side="top", pady=5)

        self.tags_label = ttk.Label(self, text="Tags (comma-separated):")
        self.tags_label.pack(side="top", pady=10)
        CreateToolTip(
            self.tags_label, "Enter tags for your YouTube video, separated by commas"
        )

        self.tags_entry = ttk.Entry(self, width=40)
        self.tags_entry.pack(side="top", pady=5)

        self.privacy_label = ttk.Label(self, text="Privacy:")
        self.privacy_label.pack(side="top", pady=10)
        CreateToolTip(self.privacy_label, "Select the privacy setting for your video")

        self.privacy_var = tk.StringVar(value="private")
        self.privacy_frame = ttk.Frame(self)
        self.privacy_frame.pack(side="top", pady=5)

        self.private_radio = ttk.Radiobutton(
            self.privacy_frame,
            text="Private",
            variable=self.privacy_var,
            value="private",
        )
        self.private_radio.pack(side="left", padx=5)

        self.unlisted_radio = ttk.Radiobutton(
            self.privacy_frame,
            text="Unlisted",
            variable=self.privacy_var,
            value="unlisted",
        )
        self.unlisted_radio.pack(side="left", padx=5)

        self.public_radio = ttk.Radiobutton(
            self.privacy_frame, text="Public", variable=self.privacy_var, value="public"
        )
        self.public_radio.pack(side="left", padx=5)

        self.schedule_label = ttk.Label(self, text="Schedule:")
        self.schedule_label.pack(side="top", pady=10)
        CreateToolTip(
            self.schedule_label,
            "Select the date and time to schedule your video (optional)",
        )

        self.schedule_frame = ttk.Frame(self)
        self.schedule_frame.pack(side="top", pady=5)

        self.date_label = ttk.Label(self.schedule_frame, text="Date:")
        self.date_label.pack(side="left", padx=5)
        self.date_entry = DateEntry(
            self.schedule_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
        )
        self.date_entry.pack(side="left", padx=5)

        self.time_label = ttk.Label(self.schedule_frame, text="Time:")
        self.time_label.pack(side="left", padx=5)

        # Generate time options in 30-minute intervals
        current_time = datetime.datetime.now().replace(
            minute=0, second=0, microsecond=0
        )
        time_options = []
        for _ in range(48):
            time_options.append(current_time.strftime("%H:%M"))
            current_time += datetime.timedelta(minutes=30)

        self.time_combobox = ttk.Combobox(
            self.schedule_frame, width=8, values=time_options
        )
        self.time_combobox.pack(side="left", padx=5)

        self.upload_button = ttk.Button(self, text="Upload", command=self.start_upload)
        self.upload_button.pack(side="top", pady=20)
        CreateToolTip(self.upload_button, "Start the video upload to YouTube")

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side="top", pady=10)
        CreateToolTip(self.cancel_button, "Cancel the upload and close the window")

    def load_api_keys(self):
        client_id, client_secret = load_api_keys()
        if not client_id or not client_secret:
            messagebox.showwarning(
                "Warning",
                "API keys not found. Please enter the API keys in the settings tab.",
            )

    def start_upload(self):
        client_id, client_secret = load_api_keys()
        if not client_id or not client_secret:
            messagebox.showerror(
                "Error",
                "API keys not found. Please enter the API keys in the settings tab.",
            )
            return

        title = self.title_entry.get()
        description = self.description_entry.get()
        tags = [tag.strip() for tag in self.tags_entry.get().split(",")]
        privacy_status = self.privacy_var.get()

        schedule_date = self.date_entry.get_date()
        schedule_time = self.time_combobox.get()

        if schedule_date and schedule_time:
            publish_at = f"{schedule_date.isoformat()}T{schedule_time}:00.000Z"
        else:
            publish_at = None

        client_secrets = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        uploader = YouTubeUploader(
            self.video_path,
            title,
            description,
            tags,
            privacy_status,
            publish_at,
            client_secrets,
        )
        threading.Thread(target=uploader.upload_video).start()

        # Clear the entry fields for the next upload
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)


class YouTubeUploader:
    def __init__(
        self,
        video_path,
        title,
        description,
        tags,
        privacy_status,
        publish_at,
        client_secrets,
    ):
        self.video_path = video_path
        self.title = title
        self.description = description
        self.tags = tags
        self.privacy_status = privacy_status
        self.publish_at = publish_at
        self.client_secrets = client_secrets
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
        credentials = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    self.client_secrets,
                    ["https://www.googleapis.com/auth/youtube.upload"],
                )
                credentials = flow.run_local_server(port=0)
            with open("token.pickle", "wb") as token:
                pickle.dump(credentials, token)
        return build("youtube", "v3", credentials=credentials)

    def upload_video(self):
        body = {
            "snippet": {
                "title": self.title,
                "description": self.description,
                "tags": self.tags,
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": self.privacy_status,
                "publishAt": self.publish_at,
            },
        }

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(self.video_path, chunksize=-1, resumable=True),
        )

        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")

        print(f"Video uploaded successfully. Video ID: {response['id']}")