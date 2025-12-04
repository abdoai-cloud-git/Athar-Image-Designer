"""Google Drive uploader using a service account."""
from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
from datetime import datetime, timezone
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
_SERVICE_CACHE = None


def _sanitize_filename(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", name.strip())
    return safe or f"athar-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"


def _load_service_account_info() -> Dict[str, Any]:  # type: ignore[name-defined]
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not configured")
    raw = raw.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    if os.path.isfile(raw):
        with open(raw, "r", encoding="utf-8") as handle:
            return json.load(handle)
    try:
        decoded = base64.b64decode(raw).decode("utf-8")
        return json.loads(decoded)
    except Exception as exc:  # pragma: no cover - defensive branch
        raise RuntimeError("Invalid GOOGLE_SERVICE_ACCOUNT_JSON payload") from exc


def _drive_service():
    global _SERVICE_CACHE
    if _SERVICE_CACHE is None:
        info = _load_service_account_info()
        credentials = service_account.Credentials.from_service_account_info(info, scopes=_DRIVE_SCOPES)
        _SERVICE_CACHE = build("drive", "v3", credentials=credentials, cache_discovery=False)
    return _SERVICE_CACHE


def download_image_bytes(image_url: str) -> bytes:
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()
    return response.content


def upload_to_gdrive(image_bytes: bytes, filename: str, mime_type: str = "image/png") -> Dict[str, str]:
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    if not folder_id:
        raise RuntimeError("GDRIVE_FOLDER_ID is not configured")
    sanitized_name = _sanitize_filename(filename)
    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype=mime_type, resumable=False)
    service = _drive_service()
    metadata = {"name": sanitized_name, "parents": [folder_id]}
    try:
        file_record = (
            service.files()
            .create(body=metadata, media_body=media, fields="id, webViewLink, webContentLink")
            .execute()
        )
        service.permissions().create(
            fileId=file_record["id"],
            body={"role": "reader", "type": "anyone"},
        ).execute()
        return {
            "file_id": file_record["id"],
            "gdrive_view_url": file_record.get("webViewLink"),
            "gdrive_download_url": file_record.get("webContentLink"),
            "filename": sanitized_name,
        }
    except HttpError as exc:
        logger.error("Google Drive upload failed: %s", exc)
        raise


class GDriveUploadTool(BaseTool):
    """Tool wrapper that downloads an image and uploads it to Google Drive."""

    image_url: Optional[str] = Field(None, description="HTTP URL to download the image from")
    image_bytes_b64: Optional[str] = Field(None, description="Base64 encoded image payload")
    filename: Optional[str] = Field(None, description="Destination filename in Google Drive (auto-generated when omitted)")
    mime_type: str = Field("image/png", description="MIME type for the upload")

    def run(self) -> Dict[str, str]:
        if not self.image_url and not self.image_bytes_b64:
            raise ValueError("Provide either image_url or image_bytes_b64")
        if self.image_bytes_b64:
            image_bytes = base64.b64decode(self.image_bytes_b64)
        else:
            image_bytes = download_image_bytes(self.image_url)  # type: ignore[arg-type]
        filename = self.filename or f"athar-frame-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.png"
        record = upload_to_gdrive(image_bytes, filename, mime_type=self.mime_type)
        return record


__all__ = ["GDriveUploadTool", "upload_to_gdrive", "download_image_bytes"]


if __name__ == "__main__":
    if not os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"):
        print("Set GOOGLE_SERVICE_ACCOUNT_JSON and GDRIVE_FOLDER_ID to run the Drive uploader test.")
    else:
        dummy_bytes = b"test"
        try:
            upload_to_gdrive(dummy_bytes, "athar-uploader-smoketest.txt", mime_type="text/plain")
        except Exception as exc:  # pragma: no cover - manual smoke test
            logger.error("Drive self-test failed: %s", exc)
