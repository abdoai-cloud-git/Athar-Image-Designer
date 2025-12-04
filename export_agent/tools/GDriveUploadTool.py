from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import json
import requests
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv

load_dotenv()

# Google Drive Configuration
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")


class GDriveUploadTool(BaseTool):
    """
    Upload images to Google Drive using a Service Account.
    Returns shareable view and download URLs for the uploaded file.
    """
    
    image_url: str = Field(
        ...,
        description="URL of the image to download and upload to Google Drive"
    )
    
    filename: str = Field(
        ...,
        description="Desired filename for the uploaded image (e.g., 'athar_image_001.png')"
    )
    
    folder_id: str = Field(
        default="",
        description="Google Drive folder ID to upload to. If not provided, uses GDRIVE_FOLDER_ID from environment"
    )

    def run(self):
        """
        Download image from URL and upload to Google Drive.
        Returns Google Drive URLs and file information.
        """
        
        # Step 1: Validate environment variables
        if not GOOGLE_SERVICE_ACCOUNT_JSON:
            return "Error: GOOGLE_SERVICE_ACCOUNT_JSON not found in environment variables. Please add the service account JSON to your .env file."
        
        target_folder_id = self.folder_id or GDRIVE_FOLDER_ID
        if not target_folder_id:
            return "Error: No folder_id provided and GDRIVE_FOLDER_ID not found in environment variables."
        
        # Step 2: Download the image
        image_bytes = self._download_image()
        if not image_bytes:
            return "Error: Failed to download image from URL"
        
        print(f"Image downloaded successfully. Size: {len(image_bytes)} bytes")
        
        # Step 3: Upload to Google Drive
        file_info = self._upload_to_gdrive(image_bytes, target_folder_id)
        if not file_info:
            return "Error: Failed to upload image to Google Drive"
        
        # Step 4: Make file publicly accessible
        if not self._make_public(file_info['id']):
            print("Warning: Failed to make file publicly accessible. Using default permissions.")
        
        # Step 5: Format and return results
        return self._format_result(file_info)
    
    def _download_image(self):
        """
        Download image from the provided URL.
        Returns image bytes if successful, None otherwise.
        """
        try:
            response = requests.get(self.image_url, timeout=60)
            response.raise_for_status()
            
            # Verify content is an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"Warning: Content-Type is {content_type}, expected image/*")
            
            return response.content
            
        except requests.exceptions.Timeout:
            print("Error: Request timed out while downloading image")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {str(e)}")
            return None
    
    def _upload_to_gdrive(self, image_bytes, folder_id):
        """
        Upload image bytes to Google Drive using service account.
        Returns file information if successful, None otherwise.
        """
        try:
            # Step 1: Parse service account credentials
            try:
                credentials_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
            except json.JSONDecodeError:
                # If it's a file path, try to read from file
                if os.path.exists(GOOGLE_SERVICE_ACCOUNT_JSON):
                    with open(GOOGLE_SERVICE_ACCOUNT_JSON, 'r') as f:
                        credentials_dict = json.load(f)
                else:
                    print("Error: Invalid GOOGLE_SERVICE_ACCOUNT_JSON format")
                    return None
            
            # Step 2: Create credentials
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict, scopes=SCOPES
            )
            
            # Step 3: Build Drive service
            service = build('drive', 'v3', credentials=credentials)
            
            # Step 4: Prepare file metadata
            file_metadata = {
                'name': self.filename,
                'parents': [folder_id]
            }
            
            # Step 5: Determine MIME type from filename
            mime_type = self._get_mime_type(self.filename)
            
            # Step 6: Upload file
            media = MediaIoBaseUpload(
                BytesIO(image_bytes),
                mimetype=mime_type,
                resumable=True
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            print(f"File uploaded successfully. File ID: {file.get('id')}")
            return file
            
        except Exception as e:
            print(f"Error uploading to Google Drive: {str(e)}")
            return None
    
    def _make_public(self, file_id):
        """
        Make the uploaded file publicly accessible.
        Returns True if successful, False otherwise.
        """
        try:
            credentials_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict, scopes=SCOPES
            )
            
            service = build('drive', 'v3', credentials=credentials)
            
            # Create public permission
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            print(f"File {file_id} is now publicly accessible")
            return True
            
        except Exception as e:
            print(f"Error making file public: {str(e)}")
            return False
    
    def _get_mime_type(self, filename):
        """
        Determine MIME type from file extension.
        """
        extension = filename.lower().split('.')[-1]
        
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'svg': 'image/svg+xml'
        }
        
        return mime_types.get(extension, 'image/png')
    
    def _format_result(self, file_info):
        """
        Format the upload result as pure JSON for downstream agent consumption.
        CRITICAL: Returns ONLY JSON - no prose, no headers.
        """
        result = {
            "success": True,
            "file_id": file_info.get('id', ''),
            "filename": file_info.get('name', self.filename),
            "gdrive_view_url": file_info.get('webViewLink', f"https://drive.google.com/file/d/{file_info.get('id')}/view"),
            "gdrive_download_url": file_info.get('webContentLink', f"https://drive.google.com/uc?id={file_info.get('id')}&export=download"),
            "gdrive_url": file_info.get('webViewLink', f"https://drive.google.com/file/d/{file_info.get('id')}/view")
        }
        
        return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Test case - Note: This requires actual credentials and a valid image URL
    print("GDriveUploadTool test")
    print("To test this tool, run:")
    print("tool = GDriveUploadTool(")
    print("    image_url='https://example.com/image.png',")
    print("    filename='test_image.png'")
    print(")")
    print("print(tool.run())")
    print("\nMake sure GOOGLE_SERVICE_ACCOUNT_JSON and GDRIVE_FOLDER_ID are set in .env")
