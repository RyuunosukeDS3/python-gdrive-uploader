import os
import zipfile
import datetime
from dotenv import load_dotenv
import re

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

load_dotenv()

SOURCE_FOLDER = os.getenv("SOURCE_FOLDER")
BACKUP_NAME = os.getenv("BACKUP_NAME")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 7))

def get_drive_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def zip_folder():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{BACKUP_NAME}_{timestamp}.zip"

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_FOLDER):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, SOURCE_FOLDER)
                zipf.write(full_path, relative_path)

    return zip_filename, timestamp

def upload_file(service, filename):
    file_metadata = {
        'name': filename,
        'parents': [GDRIVE_FOLDER_ID]
    }

    media = MediaFileUpload(filename, resumable=True)

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"Uploaded: {filename}")

def cleanup_old_backups(service):
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)

    query = (
        f"'{GDRIVE_FOLDER_ID}' in parents and "
        f"name contains '{BACKUP_NAME}_' and "
        f"mimeType = 'application/zip'"
    )

    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    files = results.get('files', [])

    for file in files:
        filename = file["name"]

        match = re.search(rf"{re.escape(BACKUP_NAME)}_(\d{{8}}_\d{{6}})\.zip$", filename)

        if not match:
            print(f"Skipping invalid filename format: {filename}")
            continue

        timestamp_str = match.group(1)

        try:
            file_datetime = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except ValueError:
            print(f"Invalid timestamp format in: {filename}")
            continue

        if file_datetime < cutoff_date:
            service.files().delete(fileId=file['id']).execute()
            print(f"Deleted old backup: {filename}")
def main():
    service = get_drive_service()

    zip_filename, _ = zip_folder()
    upload_file(service, zip_filename)
    cleanup_old_backups(service)

    os.remove(zip_filename)
    print("Local zip removed.")

if __name__ == "__main__":
    main()
