import os.path
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_gdrive_service():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # The user needs to provide their own credentials.json file
            # from Google Cloud Platform.
            if not os.path.exists(CREDENTIALS_FILE):
                print("Error: credentials.json not found.")
                print(f"Please download your credentials from the Google Cloud Console and place it at {CREDENTIALS_FILE}")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def list_videos(service, folder_id):
    """
    List video files in a specific Google Drive folder.
    """
    if not service:
        return []

    try:
        # Query for video files in the specified folder
        query = f"'{folder_id}' in parents and mimeType contains 'video/' and trashed=false"
        results = service.files().list(
            q=query,
            pageSize=100, # Adjust as needed
            fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        return items
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def download_file(service, file_id, file_path):
    """
    Download a file from Google Drive.
    """
    if not service:
        return False

    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        print(f"File {file_path} downloaded successfully.")
        return True
    except HttpError as error:
        print(f'An error occurred: {error}')
        return False
