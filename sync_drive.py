import os
import io
import shutil
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
# We need both drive scope and drive.readonly to ensure export works properly
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file"
]

def setup_local_folder(folder_name):
    """Create or clear the local folder"""
    if os.path.exists(folder_name):
        # Remove existing folder and its contents
        shutil.rmtree(folder_name)
    # Create fresh folder
    os.makedirs(folder_name)
    print(f"Local folder '{folder_name}' prepared.")

def find_folder_id(service, folder_name):
    """Find the folder ID for the specified folder name"""
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query, spaces='drive').execute()
    items = results.get('files', [])
    
    if not items:
        print(f"No folder named '{folder_name}' found in Google Drive.")
        return None
        
    return items[0]['id']

def download_folder_contents(service, folder_id, local_folder):
    """Download all files from the specified folder to local folder"""
    # Query for files in the specified folder
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query).execute()
    items = results.get('files', [])
    
    if not items:
        print(f"No files found in the folder.")
        return

    # Define mime type mappings for exports
    export_types = {
        'application/vnd.google-apps.document': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),
        'application/vnd.google-apps.spreadsheet': ('text/csv', '.csv'),  # Changed to CSV
        'application/vnd.google-apps.presentation': ('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),
    }

    # Download each file
    for item in items:
        file_id = item['id']
        file_name = item['name']
        mime_type = item.get('mimeType', '')
        
        # Handle Google Workspace files differently (export them)
        if mime_type.startswith('application/vnd.google-apps'):
            if mime_type in export_types:
                export_mime, extension = export_types[mime_type]
                
                # Add appropriate extension if not present
                if not file_name.endswith(extension):
                    file_name += extension
                
                file_path = os.path.join(local_folder, file_name)
                
                try:
                    # Export the file
                    request = service.files().export_media(fileId=file_id, mimeType=export_mime)
                    
                    with io.FileIO(file_path, 'wb') as fh:
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            print(f"Exporting {file_name}: {int(status.progress() * 100)}%")
                    
                    print(f"Exported {mime_type} to {file_name}")
                except HttpError as error:
                    print(f"Error exporting {file_name}: {error}")
                    print("Skipping this file due to permission issues.")
                    continue
            else:
                print(f"Skipping unsupported Google Workspace file: {file_name} (type: {mime_type})")
                continue
        else:
            # Regular file download
            try:
                request = service.files().get_media(fileId=file_id)
                file_path = os.path.join(local_folder, file_name)
                
                with io.FileIO(file_path, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(f"Downloading {file_name}: {int(status.progress() * 100)}%")
            except HttpError as error:
                print(f"Error downloading {file_name}: {error}")
                print("Skipping this file due to permission issues.")
                continue
    
    print(f"All files downloaded to {local_folder}")

def main():
    """Downloads all files from '_Workouts' folder in Google Drive to a local folder."""
    FOLDER_NAME = "_Workouts"
    
    # Remove existing token to force re-authorization
    if os.path.exists("token.json"):
        print("Removing old token to ensure proper permissions...")
        os.remove("token.json")
        
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        
        # Set up local folder
        setup_local_folder(FOLDER_NAME)
        
        # Find the folder ID for "_Workouts"
        folder_id = find_folder_id(service, FOLDER_NAME)
        if folder_id:
            # Download all files from the folder
            download_folder_contents(service, folder_id, FOLDER_NAME)
    
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()