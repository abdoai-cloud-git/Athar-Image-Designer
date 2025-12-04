"""KIE Nano Banana integration utilities and Agency Swarm tool."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field, field_validator

load_dotenv()

LOGGER = logging.getLogger(__name__)

KIE_API_BASE = os.getenv("KIE_API_BASE", "https://api.kie.ai/api/v1")
CREATE_TASK_PATH = "/playground/createTask"
RECORD_INFO_PATH = "/playground/recordInfo"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
BACKOFF_START = 2
POLL_INTERVAL = 5
POLL_TIMEOUT = 300


class KIEApiError(RuntimeError):
    """Raised when the KIE API returns an unrecoverable error."""


@dataclass
class TaskSubmission:
    task_id: str
    submitted_at: Optional[str]
    payload: Dict[str, Any]


@dataclass
class TaskPollResult:
    task_id: str
    status: str
    response: Dict[str, Any]
    attempts: int
    completed_at: Optional[str]


def _headers() -> Dict[str, str]:
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        raise EnvironmentError("KIE_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {api_key}",
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _build_url(path: str) -> str:
    return f"{KIE_API_BASE.rstrip('/')}{path}"


def create_task(prompt: str, aspect_ratio: str, options: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT) -> TaskSubmission:
    """Create a Nano Banana task via KIE playground."""
    payload: Dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "options": options or {},
    }

    attempt = 0
    backoff = BACKOFF_START
    while True:
        try:
            response = requests.post(
                _build_url(CREATE_TASK_PATH),
                headers=_headers(),
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()
            task_id = data.get("data", {}).get("taskId") or data.get("taskId")
            if not task_id:
                raise KIEApiError(f"Missing taskId in response: {data}")
            LOGGER.info("KIE task created", extra={"task_id": task_id})
            submitted_at = data.get("data", {}).get("createdAt") or data.get("createdAt")
            return TaskSubmission(task_id=task_id, submitted_at=submitted_at, payload=payload)
        except (requests.RequestException, ValueError) as exc:
            attempt += 1
            LOGGER.warning("KIE createTask failed", extra={"attempt": attempt, "error": str(exc)})
            if attempt > MAX_RETRIES:
                raise KIEApiError("Exceeded retries when creating KIE task") from exc
            time.sleep(backoff)
            backoff *= 2


def poll_task(task_id: str, poll_interval: int = POLL_INTERVAL, timeout: int = POLL_TIMEOUT) -> TaskPollResult:
    """Poll the KIE API until the task completes or fails."""
    deadline = time.monotonic() + timeout
    attempts = 0
    last_response: Dict[str, Any] | None = None

    while time.monotonic() < deadline:
        attempts += 1
        try:
            response = requests.get(
                _build_url(RECORD_INFO_PATH),
                headers=_headers(),
                params={"taskId": task_id},
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            last_response = data
            status = data.get("data", {}).get("status") or data.get("status")
            if status in {"completed", "failed", "error"}:
                completed_at = data.get("data", {}).get("completedAt") or data.get("completedAt")
                return TaskPollResult(
                    task_id=task_id,
                    status=status,
                    response=data,
                    attempts=attempts,
                    completed_at=completed_at,
                )
        except (requests.RequestException, ValueError) as exc:
            LOGGER.warning("KIE recordInfo failed", extra={"task_id": task_id, "attempt": attempts, "error": str(exc)})
        time.sleep(poll_interval)

    raise TimeoutError(f"KIE task {task_id} did not complete within {timeout}s. Last response: {last_response}")


def get_image_url(task_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract image URLs and seed metadata from the KIE record info response."""
    data_section = task_result.get("data") or {}
    records: List[Dict[str, Any]] = data_section.get("records") or data_section.get("images") or []
    if not records:
        raise KIEApiError(f"No image records found in response: {json.dumps(task_result)[:400]}")

    image_urls = []
    seeds = []
    for record in records:
        url = record.get("imageUrl") or record.get("url") or record.get("cdnUrl")
        if url:
            image_urls.append(url)
        seed = record.get("seed") or record.get("meta", {}).get("seed")
        if seed is not None:
            seeds.append(str(seed))

    if not image_urls:
        raise KIEApiError("Record info payload does not include any image URLs")

    return {
        "image_urls": image_urls,
        "seed": seeds[0] if seeds else None,
    }


class NanoBananaTaskTool(BaseTool):
    """Agency Swarm tool that runs the full KIE Nano Banana task lifecycle."""

    prompt: str = Field(..., description="Fully formatted Nano Banana prompt to send through KIE.")
    aspect_ratio: str = Field("3:2", description="Aspect ratio in W:H format (e.g., 3:2, 4:5).")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt string to suppress artifacts.")
    style: Optional[str] = Field(None, description="Optional style tag sent inside options.style")
    palette: Optional[str] = Field(None, description="Palette description for metadata logging")
    keywords: Optional[List[str]] = Field(None, description="Keyword list for traceability")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata to persist with the task")

    _record: Optional[TaskPollResult] = None

    @field_validator("aspect_ratio")
    def _validate_ratio(cls, value: str) -> str:
        parts = value.split(":")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise ValueError("aspect_ratio must look like '3:2'")
        return value

    def run(self) -> Dict[str, Any]:
        options: Dict[str, Any] = {
            "negative_prompt": self.negative_prompt or "",
            "style": self.style or "athar-cinematic",
            "palette": self.palette,
            "keywords": self.keywords,
            "metadata": self.metadata or {},
        }
        submission = create_task(self.prompt, self.aspect_ratio, options)
        poll_result = poll_task(submission.task_id)
        if poll_result.status != "completed":
            raise KIEApiError(f"KIE task {submission.task_id} failed with status {poll_result.status}")
        image_payload = get_image_url(poll_result.response)
        self._record = poll_result
        LOGGER.info(
            "KIE task completed",
            extra={
                "task_id": submission.task_id,
                "attempts": poll_result.attempts,
                "image_count": len(image_payload["image_urls"]),
            },
        )
        return {
            "task_id": submission.task_id,
            "prompt_used": self.prompt,
            "negative_prompt_used": self.negative_prompt,
            "aspect_ratio": self.aspect_ratio,
            "image_url": image_payload["image_urls"][0],
            "all_image_urls": image_payload["image_urls"],
            "seed": image_payload.get("seed"),
            "retrieval_log": {
                "submitted_at": submission.submitted_at,
                "completed_at": poll_result.completed_at,
                "poll_attempts": poll_result.attempts,
            },
        }


if __name__ == "__main__":
    import argparse
    import pprint

    parser = argparse.ArgumentParser(description="Manually test the KIE Nano Banana tool.")
    parser.add_argument("prompt", help="Prompt to send to Nano Banana")
    parser.add_argument("--aspect-ratio", default="3:2")
    parser.add_argument("--negative", default="")
    args = parser.parse_args()

    tool = NanoBananaTaskTool(
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        negative_prompt=args.negative,
    )
    pprint.pp(tool.run())
