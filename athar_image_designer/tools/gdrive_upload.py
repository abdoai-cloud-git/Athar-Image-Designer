"""Google Drive upload helper and Agency Swarm tool."""

from __future__ import annotations

import io
import json
import logging
import mimetypes
import os
import re
import time
from typing import Any, Dict, Optional

import requests
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from pydantic import Field

load_dotenv()

LOGGER = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/drive"]


def _load_credentials():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT_JSON is not set")
    raw = raw.strip()
    if raw.startswith("{"):
        info = json.loads(raw)
    else:
        if not os.path.exists(raw):
            raise FileNotFoundError(f"Service account file not found: {raw}")
        with open(raw, "r", encoding="utf-8") as handle:
            info = json.load(handle)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def _slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9-_]+", "-", value.strip().lower())
    return re.sub(r"-+", "-", value).strip("-") or f"athar-{int(time.time())}"


def upload_to_gdrive(image_bytes: bytes, filename: str, mime_type: Optional[str] = None, folder_id: Optional[str] = None) -> Dict[str, Any]:
    folder_id = folder_id or os.getenv("GDRIVE_FOLDER_ID")
    if not folder_id:
        raise EnvironmentError("GDRIVE_FOLDER_ID is not configured")

    creds = _load_credentials()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    mime_type = mime_type or "image/png"

    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype=mime_type, resumable=True)
    metadata = {"name": filename, "parents": [folder_id]}

    try:
        file_obj = (
            service.files()
            .create(body=metadata, media_body=media, fields="id,webViewLink,webContentLink")
            .execute()
        )
        service.permissions().create(
            fileId=file_obj["id"], body={"role": "reader", "type": "anyone"}, fields="id"
        ).execute()
    except HttpError as exc:
        raise RuntimeError(f"Google Drive upload failed: {exc}") from exc

    return {
        "file_id": file_obj["id"],
        "gdrive_view_url": file_obj["webViewLink"],
        "gdrive_download_url": file_obj["webContentLink"],
        "filename": filename,
    }


class GoogleDriveUploadTool(BaseTool):
    """Downloads an image and uploads it to a Google Drive folder."""

    image_url: str = Field(..., description="Publicly accessible image URL to download and upload.")
    filename: Optional[str] = Field(None, description="Desired filename; auto-generated when omitted.")
    mime_type: Optional[str] = Field(None, description="Mime type for Drive upload (defaults to response Content-Type).")
    folder_id: Optional[str] = Field(None, description="Override folder id; defaults to env GDRIVE_FOLDER_ID.")

    def run(self) -> Dict[str, Any]:
        response = requests.get(self.image_url, timeout=60)
        response.raise_for_status()
        mime_type = self.mime_type or response.headers.get("Content-Type") or "image/png"
        filename = self.filename or self._infer_filename()
        LOGGER.info("Uploading image to Drive", extra={"filename": filename})
        result = upload_to_gdrive(response.content, filename, mime_type, self.folder_id)
        result["source_url"] = self.image_url
        result["mime_type"] = mime_type
        return result

    def _infer_filename(self) -> str:
        path_segment = self.image_url.rstrip("/").split("/")[-1]
        guess = path_segment.split("?")[0]
        guess = guess if guess and "." in guess else f"athar-image-{int(time.time())}.png"
        name, ext = os.path.splitext(guess)
        slug = _slugify(name)
        if not ext:
            ext = mimetypes.guess_extension(self.mime_type or "image/png") or ".png"
        return f"{slug}{ext}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload an image URL to Google Drive")
    parser.add_argument("image_url")
    parser.add_argument("--filename")
    args = parser.parse_args()

    tool = GoogleDriveUploadTool(image_url=args.image_url, filename=args.filename)
    try:
        upload_info = tool.run()
        print(json.dumps(upload_info, indent=2))
    except Exception as exc:  # pragma: no cover - manual testing helper
        LOGGER.error("Upload failed: %s", exc)
        raise
