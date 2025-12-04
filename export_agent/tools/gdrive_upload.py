"""
Google Drive upload tool using Service Account authentication.
Uploads images to a specified Google Drive folder and returns sharing URLs.
"""
from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import json
import base64
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class GdriveUpload(BaseTool):
    """
    Tool for uploading images to Google Drive using Service Account credentials.
    Returns both view and download URLs for the uploaded file.
    """
    
    image_url: str = Field(
        ...,
        description="URL of the image to download and upload to Google Drive."
    )
    
    filename: str = Field(
        ...,
        description="Filename for the uploaded image (e.g., 'athar_image_001.jpg')."
    )
    
    folder_id: Optional[str] = Field(
        default=None,
        description="Google Drive folder ID where the image should be uploaded. If not provided, uses GDRIVE_FOLDER_ID from environment."
    )

    def run(self):
        """
        Downloads image from URL and uploads to Google Drive.
        Returns view URL, download URL, and filename.
        """
        # Step 1: Get configuration from environment
        service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        folder_id = self.folder_id or os.getenv("GDRIVE_FOLDER_ID")
        
        if not service_account_json:
            return "Error: GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not set."
        
        if not folder_id:
            return "Error: GDRIVE_FOLDER_ID environment variable is not set and folder_id parameter not provided."
        
        # Step 2: Parse service account JSON
        try:
            if service_account_json.startswith('{'):
                # Already a JSON string
                service_account = json.loads(service_account_json)
            else:
                # Base64 encoded JSON
                decoded = base64.b64decode(service_account_json)
                service_account = json.loads(decoded)
        except Exception as e:
            return f"Error: Failed to parse GOOGLE_SERVICE_ACCOUNT_JSON: {str(e)}"
        
        # Step 3: Get access token using service account
        access_token = self._get_access_token(service_account)
        if not access_token:
            return "Error: Failed to obtain Google Drive access token."
        
        # Step 4: Download image from URL
        try:
            image_response = requests.get(self.image_url, timeout=30)
            image_response.raise_for_status()
            image_bytes = image_response.content
        except Exception as e:
            return f"Error: Failed to download image from {self.image_url}: {str(e)}"
        
        # Step 5: Upload to Google Drive
        try:
            # Create file metadata
            metadata = {
                "name": self.filename,
                "parents": [folder_id]
            }
            
            # Upload file using multipart upload
            files = {
                "metadata": (None, json.dumps(metadata), "application/json"),
                "file": (self.filename, image_bytes, "image/jpeg")
            }
            
            upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.post(upload_url, headers=headers, files=files, timeout=60)
            response.raise_for_status()
            file_data = response.json()
            file_id = file_data.get("id")
            
            if not file_id:
                return "Error: File uploaded but no file ID returned."
            
            # Step 6: Make file publicly viewable and get sharing URLs
            share_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
            share_payload = {
                "role": "reader",
                "type": "anyone"
            }
            
            requests.post(
                share_url,
                headers=headers,
                json=share_payload,
                timeout=30
            )
            
            # Generate URLs
            view_url = f"https://drive.google.com/file/d/{file_id}/view"
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            return {
                "status": "success",
                "file_id": file_id,
                "filename": self.filename,
                "gdrive_view_url": view_url,
                "gdrive_download_url": download_url,
                "folder_id": folder_id
            }
            
        except Exception as e:
            return f"Error: Failed to upload to Google Drive: {str(e)}"
    
    def _get_access_token(self, service_account: dict) -> Optional[str]:
        """
        Obtains an access token using Google Service Account credentials.
        Uses OAuth 2.0 JWT flow.
        """
        import jwt
        import time
        from datetime import datetime, timedelta
        
        try:
            # Extract credentials
            client_email = service_account.get("client_email")
            private_key = service_account.get("private_key")
            
            if not client_email or not private_key:
                return None
            
            # Create JWT token
            now = datetime.utcnow()
            claims = {
                "iss": client_email,
                "sub": client_email,
                "aud": "https://oauth2.googleapis.com/token",
                "iat": int(time.mktime(now.timetuple())),
                "exp": int(time.mktime((now + timedelta(hours=1)).timetuple())),
                "scope": "https://www.googleapis.com/auth/drive.file"
            }
            
            token = jwt.encode(claims, private_key, algorithm="RS256")
            
            # Exchange JWT for access token
            token_url = "https://oauth2.googleapis.com/token"
            payload = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": token
            }
            
            response = requests.post(token_url, data=payload, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            
            return token_data.get("access_token")
            
        except Exception as e:
            print(f"Error obtaining access token: {str(e)}")
            return None


if __name__ == "__main__":
    # Test the tool (requires proper environment variables)
    tool = GdriveUpload(
        image_url="https://example.com/test.jpg",
        filename="test_image.jpg"
    )
    result = tool.run()
    print(result)
