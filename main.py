import os
import sys
import database  # This should be your Supabase-based database module now
import google_drive
import instagram
import time
from dotenv import load_dotenv
load_dotenv()

# Load configuration from environment variables
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

def safe_delete(path, retries=3, delay=1):
    for _ in range(retries):
        try:
            os.remove(path)
            return True
        except PermissionError:
            time.sleep(delay)

    print(f"Could not delete {path}. Still in use.")
    return False

def main():
    """
    The main function to run the Instagram uploader bot.
    """
    # Validate configuration
    if not all([GOOGLE_DRIVE_FOLDER_ID, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        print("Error: Missing required environment variables.")
        print("Please set GOOGLE_DRIVE_FOLDER_ID, INSTAGRAM_USERNAME, and INSTAGRAM_PASSWORD.")
        sys.exit(1)

    print("--- Starting Instagram Uploader Bot ---")

    # 1. No need to initialize local DB anymore (Supabase is remote)
    # If you want, you can add a function to check Supabase connection here.

    # 2. Get Google Drive service
    print("Authenticating with Google Drive...")
    gdrive_service = google_drive.get_gdrive_service()
    if not gdrive_service:
        print("Could not authenticate with Google Drive. Exiting.")
        sys.exit(1)

    # 3. Get list of videos from Google Drive
    print(f"Fetching videos from Google Drive folder: {GOOGLE_DRIVE_FOLDER_ID}")
    videos = google_drive.list_videos(gdrive_service, GOOGLE_DRIVE_FOLDER_ID)
    if not videos:
        print("No videos found in the specified folder.")
        sys.exit(0)
    else:
        print(f"Found {len(videos)} videos.")

    # 4. Process each video
    for video in videos:
        database.wait_if_needed()  # No connection param now

        file_id = video.get("id")
        file_name = video.get("name")
        print(f"\nProcessing video: {file_name} (ID: {file_id})")

        # Check if video has already been uploaded
        if database.is_video_uploaded(file_id):
            print(f"Video '{file_name}' has already been uploaded. Skipping.")
            continue

        # Download the video
        local_video_path = os.path.join("uploads", file_name)
        os.makedirs(os.path.dirname(local_video_path), exist_ok=True)
        print(f"Downloading '{file_name}' to '{local_video_path}'...")
        if not google_drive.download_file(gdrive_service, file_id, local_video_path):
            print(f"Failed to download '{file_name}'. Skipping.")
            continue

        # Upload to Instagram
        insta_client = instagram.login_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

        if insta_client:
            caption = f"From Google Drive: {file_name}"  # Simple caption
            instagram.upload_video_to_instagram(insta_client, local_video_path, caption)
            # Record the upload in the database
            database.add_uploaded_video(file_id)
            print(f"Recorded '{file_name}' as uploaded.")
        else:
            print("Failed to log into Instagram.")

        # Clean up the downloaded file
        if os.path.exists(local_video_path):
            safe_delete(local_video_path, retries=3, delay=1)

    print("\n--- Instagram Uploader Bot finished ---")

if __name__ == "__main__":
    main()
