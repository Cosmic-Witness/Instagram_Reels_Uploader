# Instagram Uploader Bot

This Python script automates the process of uploading videos from a specified Google Drive folder to an Instagram account. It keeps track of uploaded videos to prevent duplicates. The application is designed to be run in a Docker container, making it easy to deploy in the cloud.

## Features

- Connects to Google Drive and fetches video files from a specific folder.
- Uploads new videos to Instagram with a caption.
- Maintains a local SQLite database to keep track of uploaded videos, preventing re-uploads.
- Packaged with a `Dockerfile` for easy containerization and cloud deployment.

## Prerequisites

Before you begin, ensure you have the following:
- Python 3.7+
- Docker (for containerized deployment)
- A Google Cloud Platform project
- An Instagram account

## Setup and Configuration

Follow these steps to set up and configure the application.

### 1. Google Drive API Credentials

You need to enable the Google Drive API and get credentials for your application.

1.  **Go to the Google Cloud Console:** [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Create a new project** or select an existing one.
3.  **Enable the Google Drive API:**
    - Go to "APIs & Services" > "Library".
    - Search for "Google Drive API" and enable it.
4.  **Create OAuth 2.0 Credentials:**
    - Go to "APIs & Services" > "Credentials".
    - Click "Create Credentials" > "OAuth client ID".
    - If prompted, configure the OAuth consent screen. Choose "External" and provide an app name, user support email, and developer contact information. You don't need to fill out everything for a simple script.
    - For the application type, select **"Desktop app"**.
    - Give it a name (e.g., "Instagram Uploader").
    - After creation, a dialog will appear with your client ID and secret. Click the "Download JSON" button to download your credentials.
5.  **Place the credentials file:**
    - Rename the downloaded file to `credentials.json`.
    - Place this file inside the `instagram_uploader` directory.

    **Important:** The `credentials.json` file is sensitive. It's included in the `.gitignore` file to prevent it from being committed to version control.

### 2. Get Your Google Drive Folder ID

1.  Open Google Drive in your browser.
2.  Navigate to the folder containing the videos you want to upload.
3.  The Folder ID is the last part of the URL in the address bar. For example, if the URL is `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j`, your Folder ID is `1a2b3c4d5e6f7g8h9i0j`.

### 3. Set Environment Variables

The script requires the following environment variables to be set:

-   `GOOGLE_DRIVE_FOLDER_ID`: The ID of your Google Drive folder.
-   `INSTAGRAM_USERNAME`: Your Instagram username.
-   `INSTAGRAM_PASSWORD`: Your Instagram password.

You can set these directly in your shell, or if you are not using Docker, you can create a `.env` file and use a library like `python-dotenv` to load them (this is not included in the current `requirements.txt`).

## Running the Application

### Running Locally (for testing)

1.  **Navigate to the project directory:**
    ```bash
    cd instagram_uploader
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set environment variables:**
    ```bash
    export GOOGLE_DRIVE_FOLDER_ID="your_folder_id"
    export INSTAGRAM_USERNAME="your_instagram_username"
    export INSTAGRAM_PASSWORD="your_instagram_password"
    ```

4.  **Run the script:**
    ```bash
    python main.py
    ```

5.  **First-time Google Authentication:**
    - The first time you run the script, it will open a new tab in your browser asking you to authorize access to your Google account.
    - After you grant permission, it will create a `token.json` file in the `instagram_uploader` directory. This file will be used for subsequent runs to avoid the authentication flow.

### Running with Docker

Using Docker is the recommended way to run this application, especially for deployment.

1.  **Build the Docker image:**
    - Make sure your `credentials.json` file is inside the `instagram_uploader` directory.
    - From the root directory of the repository, run:
    ```bash
    docker build -t instagram-uploader instagram_uploader
    ```

2.  **Run the Docker container:**
    ```bash
    docker run --rm -it \
      -e GOOGLE_DRIVE_FOLDER_ID="your_folder_id" \
      -e INSTAGRAM_USERNAME="your_instagram_username" \
      -e INSTAGRAM_PASSWORD="your_instagram_password" \
      --name instagram-uploader-instance \
      instagram-uploader
    ```
    - The first time you run this, you will need to complete the Google authentication flow in your terminal. Copy the URL from the terminal, open it in a browser, grant access, and then paste the authorization code back into the terminal.
    - To persist the `token.json` and the `uploads.db` database between container runs, you can use a volume mount:
    ```bash
    docker run --rm -it \
      -e GOOGLE_DRIVE_FOLDER_ID="your_folder_id" \
      -e INSTAGRAM_USERNAME="your_instagram_username" \
      -e INSTAGRAM_PASSWORD="your_instagram_password" \
      -v $(pwd)/instagram_uploader:/app \
      --name instagram-uploader-instance \
      instagram-uploader
    ```
    This command mounts the `instagram_uploader` directory on your host to the `/app` directory in the container. This way, `token.json` and `uploads.db` are stored on your host machine.

## How It Works

1.  **Initialization:** The script starts by initializing the SQLite database (`uploads.db`) to ensure the table for tracking uploads exists.
2.  **Google Drive Authentication:** It authenticates with the Google Drive API using your `credentials.json` and `token.json`.
3.  **Fetch Videos:** It lists all video files in the specified Google Drive folder.
4.  **Process Videos:** For each video, it checks the database to see if the video's file ID has been recorded.
    - If it has been recorded, the video is skipped.
    - If it's a new video, it's downloaded locally.
5.  **Instagram Upload:** The script logs into Instagram and uploads the downloaded video with a caption generated from the filename.
6.  **Record Upload:** If the upload is successful, the video's Google Drive file ID is saved to the database.
7.  **Cleanup:** The local video file is deleted to save space.

## Disclaimer

- This script uses a third-party library (`instagrapi`) to interact with Instagram's private API. This is not an official API, and its use may be against Instagram's terms of service. Use it at your own risk.
- Storing your Instagram password in an environment variable is convenient for automation but be mindful of the security implications in your deployment environment.
