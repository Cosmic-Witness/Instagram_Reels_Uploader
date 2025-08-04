from supabase import create_client, Client
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_uploaded_video(file_id):
    now_utc = datetime.utcnow().isoformat()
    response = supabase.table("uploaded_videos").insert({
        "file_id": file_id,
        "timestamp_utc": now_utc
    }).execute()
    return response

def is_video_uploaded(file_id):
    response = supabase.table("uploaded_videos").select("file_id").eq("file_id", file_id).execute()
    return len(response.data) > 0

def get_last_upload_time():
    response = supabase.table("uploaded_videos").select("timestamp_utc").order("timestamp_utc", desc=True).limit(1).execute()
    if response.data:
        return datetime.fromisoformat(response.data[0]["timestamp_utc"])
    return None

def wait_if_needed():
    last_upload_time = get_last_upload_time()
    if last_upload_time:
        now = datetime.utcnow()
        elapsed = (now - last_upload_time).total_seconds()
        if elapsed < 60:
            wait_time = 60 - elapsed
            print(f"Last upload was at {last_upload_time.isoformat()} UTC")
            print(f"Waiting {int(wait_time/60)} minutes before next upload...")
            time.sleep(wait_time)
