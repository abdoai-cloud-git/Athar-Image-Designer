"""KIE Playground wrapper for Nano Banana Pro submissions."""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional

import requests
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_DEFAULT_BASE = os.getenv("KIE_API_BASE", "https://api.kie.ai/api/v1").rstrip("/")
CREATE_TASK_URL = f"{_DEFAULT_BASE}/playground/createTask"
RECORD_INFO_URL = f"{_DEFAULT_BASE}/playground/recordInfo"
_MAX_RETRIES = 4
_DEFAULT_TIMEOUT = 180
_INITIAL_INTERVAL = 3.0
_SESSION = requests.Session()


class KieApiError(RuntimeError):
    """Raised when the KIE Playground API reports an error."""


def _headers() -> Dict[str, str]:
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        raise KieApiError("KIE_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _request_with_retry(method: str, url: str, *, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    last_error: Optional[Exception] = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = _SESSION.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=_headers(),
                timeout=30,
            )
            if response.status_code >= 500:
                raise KieApiError(f"KIE server error {response.status_code}: {response.text}")
            response.raise_for_status()
            payload = response.json()
            logger.debug("KIE %s attempt %s succeeded", method, attempt)
            return payload
        except (requests.RequestException, KieApiError) as exc:
            last_error = exc
            logger.warning("KIE request error (attempt %s/%s): %s", attempt, _MAX_RETRIES, exc)
            if attempt == _MAX_RETRIES:
                break
            sleep_time = min(_INITIAL_INTERVAL * (2 ** (attempt - 1)), 12)
            time.sleep(sleep_time)
    raise KieApiError(f"KIE request failed after {_MAX_RETRIES} attempts: {last_error}")


def create_task(prompt: str, aspect_ratio: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Submit a Nano Banana render task via KIE."""
    body: Dict[str, Any] = {
        "prompt": prompt.strip(),
        "aspectRatio": aspect_ratio.strip(),
        "options": {"model": "nano-banana-pro"},
    }
    if options:
        merged_options = {"model": "nano-banana-pro"}
        merged_options.update({k: v for k, v in options.items() if v is not None})
        body["options"] = merged_options
    return _request_with_retry("POST", CREATE_TASK_URL, json_body=body)


def poll_task(task_id: str, timeout_seconds: int = _DEFAULT_TIMEOUT, interval_seconds: float = _INITIAL_INTERVAL) -> Dict[str, Any]:
    """Poll task status until completion or timeout."""
    start = time.monotonic()
    attempt = 0
    interval = interval_seconds
    while time.monotonic() - start <= timeout_seconds:
        attempt += 1
        payload = _request_with_retry("GET", RECORD_INFO_URL, params={"taskId": task_id})
        status = payload.get("status") or payload.get("data", {}).get("status")
        if status in {"completed", "failed"}:
            payload["_attempts"] = attempt
            payload["_elapsed"] = round(time.monotonic() - start, 2)
            return payload
        time.sleep(interval)
        interval = min(interval * 1.5, 12.0)
    raise TimeoutError(f"KIE task {task_id} did not complete within {timeout_seconds} seconds")


def get_image_url(task_result: Dict[str, Any]) -> str:
    """Extract the final image URL from a completed task response."""
    result = task_result.get("result") or task_result.get("data", {}).get("result") or {}
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {"raw": result}
    if isinstance(result, dict):
        if result.get("imageUrl"):
            return result["imageUrl"]
        images = result.get("images") or result.get("outputs")
        if isinstance(images, list) and images:
            if isinstance(images[0], dict) and images[0].get("url"):
                return images[0]["url"]
            if isinstance(images[0], str):
                return images[0]
    raise KieApiError("KIE response did not include an image URL")


class KieNanoBananaTool(BaseTool):
    """Agency Swarm tool that drives KIE to render Nano Banana Pro images."""

    prompt: Optional[str] = Field(None, description="Fully composed Nano Banana prompt")
    aspect_ratio: Optional[str] = Field("3:4", description="Aspect ratio string such as '3:4' or '16:9'")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt to suppress undesired features")
    style: Optional[str] = Field("cinematic-premium", description="Nano Banana style preset")
    palette: Optional[str] = Field(None, description="Comma-separated palette keywords")
    seed: Optional[int] = Field(None, description="Seed override for deterministic renders")
    timeout_seconds: int = Field(_DEFAULT_TIMEOUT, ge=30, le=600, description="Max seconds to wait for KIE task completion")
    poll_interval: float = Field(_INITIAL_INTERVAL, gt=0.5, le=10, description="Initial polling interval in seconds")
    extra_options: Optional[Dict[str, Any]] = Field(None, description="Additional KIE options to merge into the payload")

    def run(self) -> Dict[str, Any]:
        if not self.prompt:
            raise ValueError("KieNanoBananaTool requires 'prompt'")
        aspect_ratio = (self.aspect_ratio or "3:4").strip()
        options = self.extra_options.copy() if self.extra_options else {}
        options.setdefault("style", self.style)
        options.setdefault("palette", self.palette)
        options.setdefault("negativePrompt", self.negative_prompt)
        options.setdefault("seed", self.seed)
        response = create_task(self.prompt, aspect_ratio, options=options)
        task_id = response.get("taskId") or response.get("data", {}).get("taskId")
        if not task_id:
            raise KieApiError(f"KIE createTask response missing taskId: {response}")
        task_result = poll_task(task_id, timeout_seconds=self.timeout_seconds, interval_seconds=self.poll_interval)
        image_url = get_image_url(task_result)
        result_block = task_result.get("result") or task_result.get("data", {}).get("result") or {}
        if isinstance(result_block, str):
            try:
                result_block = json.loads(result_block)
            except json.JSONDecodeError:
                result_block = {"raw": result_block}
        seed = result_block.get("seed") or response.get("seed") or options.get("seed")
        metadata = {
            "task_id": task_id,
            "attempts": task_result.get("_attempts"),
            "elapsed_seconds": task_result.get("_elapsed"),
            "status": task_result.get("status") or task_result.get("data", {}).get("status"),
        }
        return {
            "image_url": image_url,
            "seed": str(seed) if seed is not None else "",
            "prompt_used": self.prompt,
            "aspect_ratio": aspect_ratio,
            "metadata": metadata,
        }


__all__ = [
    "KieNanoBananaTool",
    "create_task",
    "poll_task",
    "get_image_url",
    "KieApiError",
]


if __name__ == "__main__":
    try:
        if not os.getenv("KIE_API_KEY"):
            raise SystemExit("Set KIE_API_KEY to run the live KIE test.")
        tool = KieNanoBananaTool(
            prompt="Test cinematic Athar texture study",
            aspect_ratio="3:4",
            negative_prompt="chaotic shapes, distorted Arabic",
            palette="copper, moonlit lavender",
            timeout_seconds=60,
        )
        print(tool.run())
    except SystemExit as exc:
        print(exc)
    except Exception as exc:  # pragma: no cover - manual smoke test only
        logger.error("KIE self-test failed: %s", exc, exc_info=True)
