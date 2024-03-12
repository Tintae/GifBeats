import os
import pickle
import requests
from tkinter import messagebox

class InstagramUploader:
    def __init__(self, video_path, aspect_ratio, caption):
        self.video_path = video_path
        self.aspect_ratio = aspect_ratio
        self.caption = caption
        self.api_url = "https://graph.facebook.com/v10.0/"
        self.access_token = self.load_access_token()

    def load_access_token(self):
        if os.path.exists("instagram_token.pickle"):
            with open("instagram_token.pickle", "rb") as token_file:
                access_token = pickle.load(token_file)
        else:
            access_token = self.get_access_token()
            with open("instagram_token.pickle", "wb") as token_file:
                pickle.dump(access_token, token_file)
        return access_token

    def get_access_token(self):
        # Implement the logic to obtain the Instagram access token
        # This may involve redirecting the user to the Instagram authorization page
        # and retrieving the access token from the redirected URL
        # You can use the `requests` library to make HTTP requests
        # and the `webbrowser` module to open the authorization page in a web browser
        # Once you have obtained the access token, return it
        access_token = "YOUR_INSTAGRAM_ACCESS_TOKEN"
        return access_token

    def upload_video(self):
        if not self.access_token:
            messagebox.showerror("Error", "Instagram access token not found.")
            return

        try:
            # Prepare the video file for upload
            video_file = open(self.video_path, "rb")

            # Make a POST request to the Instagram Graph API to upload the video
            url = f"{self.api_url}me/media?access_token={self.access_token}"
            response = requests.post(
                url,
                files={"video": video_file},
                data={"caption": self.caption},
            )

            if response.status_code == 200:
                media_id = response.json()["id"]
                # Publish the uploaded video
                url = f"{self.api_url}{media_id}/media_publish?access_token={self.access_token}"
                response = requests.post(url)

                if response.status_code == 200:
                    messagebox.showinfo("Success", "Video uploaded successfully to Instagram!")
                else:
                    messagebox.showerror("Error", f"Failed to publish the video on Instagram. Status code: {response.status_code}")
            else:
                messagebox.showerror("Error", f"Failed to upload the video to Instagram. Status code: {response.status_code}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during Instagram upload: {str(e)}")

        finally:
            video_file.close()