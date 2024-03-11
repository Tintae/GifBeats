import queue
import threading
from moviepy.editor import *
from tkinter import filedialog, messagebox
from utils import CreateToolTip, load_api_keys, save_api_keys
import tkinter as tk
from tkinter import ttk
from youtube_uploader import YouTubeUploaderFrame
from settings_window import SettingsWindow
import tkinter as tk
from tkinter import ttk
from utils import CreateToolTip


def create_video(audio_path, gif_path, output_path, progress_queue, settings):
    try:
        audio_clip = AudioFileClip(audio_path)
        progress_queue.put(10)

        gif_clip = VideoFileClip(gif_path)
        gif_width, gif_height = gif_clip.size
        aspect_ratio = gif_width / gif_height
        new_height = settings["height"] if settings["custom_resolution"] else 1080
        new_width = int(new_height * aspect_ratio)
        gif_clip = gif_clip.resize((new_width, new_height))
        progress_queue.put(40)

        video_width = settings["width"] if settings["custom_resolution"] else 1920
        video_height = settings["height"] if settings["custom_resolution"] else 1080
        position = ((video_width - new_width) // 2, (video_height - new_height) // 2)
        background_clip = ColorClip(size=(video_width, video_height), color=(0, 0, 0))
        background_clip = background_clip.set_duration(audio_clip.duration)
        gif_clip = gif_clip.loop(duration=audio_clip.duration)
        final_clip = CompositeVideoClip(
            [background_clip, gif_clip.set_position(position)]
        )
        final_clip = final_clip.set_audio(audio_clip)
        progress_queue.put(70)

        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24,
        )
        progress_queue.put(100)

        messagebox.showinfo("Success", "Video created successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create video: {e}")
        progress_queue.put(-1)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("GifBeats")
        self.master.geometry("600x600")
        self.master.configure(bg="#1f1f1f")
        self.configure(bg="#1f1f1f")
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.settings = {
            "custom_resolution": False,
            "width": 1920,
            "height": 1080,
        }
        self.create_widgets()
        self.youtube_frame = None

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
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
            padding=10,
            relief="flat",
            borderwidth=0,
            borderradius=20,
        )
        style.configure("TProgressbar", background="#ff5500", troughcolor="#4d4d4d")

        self.audio_frame = ttk.Frame(self, style="Card.TFrame")
        self.audio_frame.pack(side="top", pady=10, fill="x")

        self.audio_label = ttk.Label(self.audio_frame, text="Audio File:")
        self.audio_label.pack(side="left", padx=10)
        CreateToolTip(self.audio_label, "Select the audio file for your video")

        self.audio_entry = ttk.Entry(self.audio_frame, width=40)
        self.audio_entry.pack(side="left", padx=10, expand=True, fill="x")

        self.browse_audio_button = ttk.Button(
            self.audio_frame, text="Browse", command=self.browse_audio, style="Round.TButton"
        )
        self.browse_audio_button.pack(side="left", padx=10)

        self.gif_frame = ttk.Frame(self, style="Card.TFrame")
        self.gif_frame.pack(side="top", pady=10, fill="x")

        self.gif_label = ttk.Label(self.gif_frame, text="GIF File:")
        self.gif_label.pack(side="left", padx=10)
        CreateToolTip(self.gif_label, "Select the GIF file for your video")

        self.gif_entry = ttk.Entry(self.gif_frame, width=40)
        self.gif_entry.pack(side="left", padx=10, expand=True, fill="x")

        self.browse_gif_button = ttk.Button(
            self.gif_frame, text="Browse", command=self.browse_gif, style="Round.TButton"
        )
        self.browse_gif_button.pack(side="left", padx=10)

        self.output_frame = ttk.Frame(self, style="Card.TFrame")
        self.output_frame.pack(side="top", pady=10, fill="x")

        self.output_label = ttk.Label(self.output_frame, text="Output File:")
        self.output_label.pack(side="left", padx=10)
        CreateToolTip(self.output_label, "Specify the output video file path")

        self.output_entry = ttk.Entry(self.output_frame, width=40)
        self.output_entry.pack(side="left", padx=10, expand=True, fill="x")

        self.browse_output_button = ttk.Button(
            self.output_frame, text="Browse", command=self.browse_output, style="Round.TButton"
        )
        self.browse_output_button.pack(side="left", padx=10)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side="top", pady=20)

        self.start_button = ttk.Button(
            self.button_frame, text="Convert", command=self.start_conversion, style="Round.TButton"
        )
        self.start_button.pack(side="left", padx=10)
        CreateToolTip(self.start_button, "Start the video conversion process")

        self.preview_button = ttk.Button(
            self.button_frame, text="Preview", command=self.preview_video, style="Round.TButton"
        )
        self.preview_button.pack(side="left", padx=10)
        self.preview_button.state(["disabled"])
        CreateToolTip(self.preview_button, "Preview the converted video")

        self.settings_button = ttk.Button(
            self.button_frame, text="Settings", command=self.open_settings, style="Round.TButton"
        )
        self.settings_button.pack(side="left", padx=10)
        CreateToolTip(self.settings_button, "Open the settings window")

        self.youtube_button = ttk.Button(
            self.button_frame,
            text="Post",
            command=self.open_youtube_uploader,
            style="Round.TButton"
        )
        self.youtube_button.pack(side="left", padx=10)
        self.youtube_button.state(["disabled"])
        CreateToolTip(self.youtube_button, "Open the YouTube upload window")

        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=500, mode="determinate"
        )
        self.progress_bar.pack(side="top", pady=10)

        self.status_label = ttk.Label(self, text="", font=("Helvetica", 12), foreground="#ffffff")
        self.status_label.pack(side="top", pady=10)


    def browse_audio(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3;*.wav;*.m4a")]
        )
        self.audio_entry.delete(0, tk.END)
        self.audio_entry.insert(0, file_path)

    def browse_gif(self):
        file_path = filedialog.askopenfilename(filetypes=[("GIF Files", "*.gif")])
        self.gif_entry.delete(0, tk.END)
        self.gif_entry.insert(0, file_path)

    def browse_output(self):
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4", filetypes=[("Video Files", "*.mp4")]
        )
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, output_path)

    def start_conversion(self):
        if self.audio_entry.get() and self.gif_entry.get() and self.output_entry.get():
            self.status_label.config(text="Converting...")
            self.start_button.state(["disabled"])
            self.progress_bar["value"] = 0
            self.convert_video(
                self.audio_entry.get(), self.gif_entry.get(), self.output_entry.get()
            )
        else:
            messagebox.showwarning("Warning", "Please select all required files.")

    def convert_video(self, audio_path, gif_path, output_path):
        progress_queue = queue.Queue()

        def update_progress():
            try:
                progress = progress_queue.get(block=False)
                if progress == -1:
                    self.status_label.config(text="Failed to create video.")
                    self.start_button.state(["!disabled"])
                    self.preview_button.state(["disabled"])
                    self.youtube_button.state(["disabled"])
                elif progress == 100:
                    self.progress_bar["value"] = progress
                    self.status_label.config(text="Conversion completed.")
                    self.start_button.state(["!disabled"])
                    self.preview_button.state(["!disabled"])
                    self.youtube_button.state(["!disabled"])
                else:
                    self.progress_bar["value"] = progress
                    self.master.after(100, update_progress)
            except queue.Empty:
                self.master.after(100, update_progress)

        threading.Thread(
            target=create_video,
            args=(audio_path, gif_path, output_path, progress_queue, self.settings),
        ).start()
        update_progress()

    def preview_video(self):
        output_path = self.output_entry.get()
        if os.path.isfile(output_path):
            os.startfile(output_path)
        else:
            messagebox.showerror("Error", "Output video file not found.")

    def open_settings(self):
        settings_window = SettingsWindow(self.master, self.settings)
        self.master.wait_window(settings_window)

    def open_youtube_uploader(self):
        self.youtube_frame = YouTubeUploaderFrame(self.master, self.output_entry.get())