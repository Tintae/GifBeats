import configparser
import tkinter as tk

def load_api_keys():
    """Load the API keys from the configuration file."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    client_id = config.get("API", "client_id", fallback="")
    client_secret = config.get("API", "client_secret", fallback="")
    return client_id, client_secret


def save_api_keys(client_id, client_secret):
    """Save the API keys to the configuration file."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("API"):
        config.add_section("API")
    config.set("API", "client_id", client_id)
    config.set("API", "client_secret", client_secret)
    with open("config.ini", "w") as config_file:
        config.write(config_file)

        
class CreateToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw,
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()