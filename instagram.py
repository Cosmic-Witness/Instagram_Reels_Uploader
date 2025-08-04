import subprocess
import sys
import os
from instagrapi import Client
from time import sleep
import random
from rich.console import Console
from rich.progress import track
from instagrapi.exceptions import LoginRequired
import database

console = Console()
path = "sessions.json" #session file

def save_session(client: Client, path: str):
    client.dump_settings(path)

def login_instagram(username,password):
    client = Client()
    if os.path.exists(path):
        try:
            client.load_settings(path)
            client.login(username, password)
            print("✅ Logged in using saved session.")
            return client
        except Exception as e:
            print(f"⚠️ Couldn’t reuse session ({e}), logging in fresh…")
    print("🔑 Logging in fresh…")
    client.login(username, password)
    save_session(client, path)
    return client


def upload_video_to_instagram(cl:Client, video_path, caption):
    """
    Uploads a video to Instagram.
    """
    if not cl:
        print("Not logged in. Cannot upload video.")
        return False

    try:
        print(f"Uploading video {video_path} to Instagram...")
        media = cl.clip_upload(video_path, caption)
        print("Video uploaded successfully.")
        return True
    except Exception as e:
        print(f"An error occurred during video upload: {e}")
        return False
