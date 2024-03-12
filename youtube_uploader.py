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
import googleapiclient


class YouTubeUploader:
    def __init__(self, video_path, aspect_ratio, title, description, tags, privacy_status, publish_at):
        self.video_path = video_path
        self.aspect_ratio = aspect_ratio
        self.title = title
        self.description = description
        self.tags = tags
        self.privacy_status = privacy_status
        self.publish_at = publish_at
        self.client_secrets = self.load_api_keys()
        self.youtube = self.get_authenticated_service()

    def load_api_keys(self):
        client_id, client_secret = load_api_keys()
        if not client_id or not client_secret:
            messagebox.showwarning(
                "Warning",
                "API keys not found. Please enter the API keys in the settings tab.",
            )
            return None

        client_secrets = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        return client_secrets

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
        # Parameter validation
        if not self.title or not self.description or not self.video_path:
            messagebox.showerror(
                "Error",
                "Please provide a title, description, and video file.",
            )
            return

        body = {
            "snippet": {
                "title": self.title,
                "description": self.description,
                "tags": self.tags,
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": self.privacy_status,
            },
        }

        if self.publish_at:
            body["status"]["publishAt"] = self.publish_at

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(self.video_path, chunksize=-1, resumable=True),
        )

        print("Starting video upload...")
        response = None
        error = None
        try:
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%.")
        except googleapiclient.errors.ResumableUploadError as e:
            error = e
            print(f"Error: {e}")

        if error:
            if "quotaExceeded" in str(error):
                messagebox.showerror(
                    "Error",
                    "Upload failed. You have exceeded your YouTube API quota. Please wait until your quota resets or request an increase in your API quota.",
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"Upload failed. Please check the scheduling format and try again.\n\nError details: {error}",
                )
        else:
            print(f"Video uploaded successfully. Video ID: {response['id']}")
            print(f"Video privacy status: {response['status']['privacyStatus']}")
            print(f"Video publish time: {response['status'].get('publishAt', 'Not scheduled')}")
            messagebox.showinfo("Success", "Video uploaded successfully!")