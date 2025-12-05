from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import logging
import os
import random
import time
from typing import Optional, Tuple

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

from monitoring import emit_event

load_dotenv()

logger = logging.getLogger(__name__)

# KIE API Configuration
KIE_API_KEY = os.getenv("KIE_API_KEY")
KIE_API_BASE = os.getenv("KIE_API_BASE", "https://api.kie.ai/api/v1")


class KieNanoBananaTool(BaseTool):
    """
    Generate images using Nano Banana Pro through KIE API integration.
    This tool creates image generation tasks, polls for completion, and returns the final image URL.
    """
    
    prompt: str = Field(
        ..., 
        description="The detailed prompt for image generation. Should include theme, mood, composition, and style details."
    )
    
    aspect_ratio: str = Field(
        default="16:9",
        description="Aspect ratio for the image. Options: '1:1', '16:9', '9:16', '4:3', '3:4', '21:9', '9:21'"
    )
    
    negative_prompt: str = Field(
        default="messy textures, chaotic shapes, distorted Arabic text, low quality, blurry",
        description="Negative prompt to avoid unwanted elements in the image"
    )
    
    num_images: int = Field(
        default=1,
        description="Number of images to generate (1-4)"
    )
    
    max_poll_attempts: int = Field(
        default=60,
        description="Maximum number of polling attempts before timeout (legacy control, still honored)"
    )
    
    poll_interval: int = Field(
        default=5,
        description="Base seconds to wait between polling attempts (used in exponential backoff)"
    )

    max_wait_seconds: int = Field(
        default=600,
        description="Hard timeout in seconds before aborting poll loop"
    )

    max_backoff_seconds: int = Field(
        default=30,
        description="Maximum delay between poll attempts when backing off"
    )

    request_timeout_seconds: int = Field(
        default=30,
        description="Request timeout for all KIE HTTP calls"
    )

    backoff_growth: float = Field(
        default=1.8,
        description="Multiplier applied to poll interval after each attempt"
    )

    def run(self):
        """
        Execute the image generation workflow through KIE API.
        Returns the image URL, seed, and generation parameters.
        """
        
        if not KIE_API_KEY:
            emit_event("kie_missing_api_key", level="error")
            return self._format_result(None, error="KIE_API_KEY not found in environment variables. Please add it to your .env file.")
        
        session = self._build_session()
        
        # Step 1: Create the image generation task
        task_id = self._create_task(session)
        if not task_id:
            return self._format_result(None, error="Failed to create image generation task")
        
        logger.info("KIE task created successfully | task_id=%s", task_id)
        emit_event(
            "kie_task_created",
            task_id=task_id,
            aspect_ratio=self.aspect_ratio,
            num_images=self.num_images,
        )
        
        # Step 2: Poll for task completion
        task_data, poll_meta = self._poll_task(session, task_id)
        if not task_data:
            emit_event(
                "kie_task_failed",
                level="error",
                task_id=task_id,
                metadata=poll_meta,
            )
            return self._format_result(None, error=f"Task {task_id} failed or timed out", metadata=poll_meta)
        
        emit_event(
            "kie_task_completed",
            task_id=task_id,
            duration=poll_meta.get("poll_duration_seconds"),
            attempts=poll_meta.get("attempts"),
        )
        if (poll_meta.get("poll_duration_seconds") or 0) > 120 or (poll_meta.get("attempts") or 0) > 3:
            emit_event(
                "kie_slow_poll",
                level="warning",
                task_id=task_id,
                duration=poll_meta.get("poll_duration_seconds"),
                attempts=poll_meta.get("attempts"),
            )
        
        # Step 3: Extract and return image information
        return self._format_result(task_data, metadata=poll_meta)
    
    def _build_session(self) -> Session:
        """
        Configure a requests Session with retries for transient network issues.
        """
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _create_task(self, session: Session) -> Optional[str]:
        """
        Create an image generation task using KIE API.
        Returns the task ID if successful, None otherwise.
        """
        url = f"{KIE_API_BASE}/playground/createTask"
        
        headers = {
            "Authorization": f"Bearer {KIE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "nano-banana-pro",
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "aspect_ratio": self.aspect_ratio,
            "num_images": self.num_images,
            "quality": "premium",
            "style": "cinematic"
        }
        
        try:
            response = session.post(url, json=payload, headers=headers, timeout=self.request_timeout_seconds)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success") and data.get("data", {}).get("taskId"):
                return data["data"]["taskId"]
            else:
                logger.error("Task creation failed | response=%s", data)
                return None
                
        except requests.exceptions.Timeout:
            logger.error("KIE createTask timeout after %ss", self.request_timeout_seconds)
            return None
        except requests.exceptions.SSLError as exc:
            logger.error("KIE SSL handshake failure during createTask | error=%s", exc)
            return None
        except requests.exceptions.RequestException as exc:
            logger.error("Error creating task | error=%s", exc)
            return None
    
    def _poll_task(self, session: Session, task_id: str) -> Tuple[Optional[dict], dict]:
        """
        Poll the task status until completion or timeout.
        Returns the task result and metadata if successful, otherwise (None, meta).
        """
        url = f"{KIE_API_BASE}/playground/recordInfo"
        
        headers = {
            "Authorization": f"Bearer {KIE_API_KEY}"
        }
        
        params = {
            "taskId": task_id
        }
        
        start = time.monotonic()
        delay = self.poll_interval
        attempts = 0
        
        while attempts < self.max_poll_attempts and (time.monotonic() - start) < self.max_wait_seconds:
            attempts += 1
            try:
                response = session.get(url, params=params, headers=headers, timeout=self.request_timeout_seconds)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get("success"):
                    logger.warning("Error polling task | task_id=%s | message=%s", task_id, data.get("message"))
                return None, self._poll_meta(task_id, attempts, start)
                
                task_data = data.get("data", {})
                status = task_data.get("status", "")
                
                logger.info(
                    "KIE poll attempt %s | task_id=%s | status=%s",
                    attempts,
                    task_id,
                    status,
                )
                
                if status == "completed":
                    return task_data, self._poll_meta(task_id, attempts, start)
                if status in {"failed", "error"}:
                    logger.error("KIE task failed | task_id=%s | payload=%s", task_id, task_data)
                    emit_event(
                        "kie_generation_failed",
                        level="error",
                        task_id=task_id,
                        payload=task_data,
                    )
                    return None, self._poll_meta(task_id, attempts, start)
                
            except requests.exceptions.SSLError as exc:
                logger.error("KIE SSL error during poll | task_id=%s | attempt=%s | error=%s", task_id, attempts, exc)
            except requests.exceptions.Timeout:
                logger.warning("KIE poll timeout | task_id=%s | attempt=%s", task_id, attempts)
            except requests.exceptions.RequestException as exc:
                logger.warning("KIE network error during poll | task_id=%s | attempt=%s | error=%s", task_id, attempts, exc)
            
            # Respect max wait
            if (time.monotonic() - start) >= self.max_wait_seconds:
                break
            
            jitter = random.uniform(0, 0.5)
            time.sleep(min(delay + jitter, self.max_backoff_seconds))
            delay = min(delay * self.backoff_growth, self.max_backoff_seconds)
        
        duration = time.monotonic() - start
        logger.error(
            "KIE task timed out | task_id=%s | attempts=%s | duration=%.2fs",
            task_id,
            attempts,
            duration,
        )
        emit_event(
            "kie_task_timeout",
            level="error",
            task_id=task_id,
            attempts=attempts,
            duration=round(duration, 2),
        )
        return None, self._poll_meta(task_id, attempts, start)
    
    def _poll_meta(self, task_id: str, attempts: int, start_time: float) -> dict:
        """
        Helper to record monitoring metadata for poll behavior.
        """
        return {
            "task_id": task_id,
            "attempts": attempts,
            "poll_duration_seconds": round(time.monotonic() - start_time, 2),
        }
    
    def _format_result(self, task_data, error=None, metadata=None):
        """
        Format the task result as pure JSON for downstream agent consumption.
        CRITICAL: Returns ONLY JSON - no prose, no headers.
        """
        metadata = metadata or {}
        
        # Handle error cases
        if error:
            return json.dumps(
                {
                    "success": False,
                    "error": error,
                    "metadata": metadata,
                },
                indent=2,
            )
        
        # Handle missing task data
        if not task_data:
            return json.dumps(
                {"success": False, "error": "No task data available", "metadata": metadata},
                indent=2,
            )
        
        images = task_data.get("images", [])
        
        if not images:
            return json.dumps({"success": False, "error": "No images generated", "metadata": metadata}, indent=2)
        
        # Extract primary image information
        primary_image = images[0]
        
        result = {
            "success": True,
            "task_id": metadata.get("task_id"),
            "poll_duration_seconds": metadata.get("poll_duration_seconds"),
            "attempts": metadata.get("attempts"),
            "image_url": primary_image.get("url", ""),
            "seed": task_data.get("seed", "N/A"),
            "prompt_used": task_data.get("prompt", self.prompt),
            "aspect_ratio": self.aspect_ratio,
            "num_images": len(images),
            "all_image_urls": [img.get("url") for img in images if img.get("url")]
        }
        
        return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Test case
    tool = KieNanoBananaTool(
        prompt="A cinematic minimalistic artwork inspired by Athar. Theme: solitude and contemplation. Mood: calm, meditative. Palette: warm earth tones with soft golden light. Composition: A single figure silhouetted against a vast desert landscape at sunset, with soft depth of field. Background has atmospheric texture with paper grain and cinematic lighting. Tone: poetic, calm, meditative.",
        aspect_ratio="16:9",
        negative_prompt="messy textures, chaotic shapes, distorted Arabic text, low quality"
    )
    print(tool.run())
