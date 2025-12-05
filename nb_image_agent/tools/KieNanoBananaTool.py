from agency_swarm.tools import BaseTool
from pydantic import Field, ValidationError
import logging
import os
import time
import json
import requests
from dotenv import load_dotenv

from shared.schemas import ImageGenerationResultSchema

load_dotenv()

# KIE API Configuration
KIE_API_KEY = os.getenv("KIE_API_KEY")
KIE_API_BASE = os.getenv("KIE_API_BASE", "https://api.kie.ai/api/v1")
logger = logging.getLogger(__name__)


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
        description="Maximum number of polling attempts before timeout"
    )
    
    poll_interval: int = Field(
        default=5,
        description="Seconds to wait between polling attempts"
    )

    max_wait_seconds: int = Field(
        default=600,
        description="Maximum overall wait (in seconds) before aborting"
    )

    def run(self):
        """
        Execute the image generation workflow through KIE API.
        Returns the image URL, seed, and generation parameters.
        """
        
        if not KIE_API_KEY:
            return self._format_result(None, error="KIE_API_KEY not found in environment variables. Please add it to your .env file.")

        run_start = time.time()

        with requests.Session() as session:

            # Step 1: Create the image generation task
            create_started = time.time()
            task_id = self._create_task(session)
            if not task_id:
                return self._format_result(None, error="Failed to create image generation task")
            
            create_duration = time.time() - create_started
            logger.info("Task %s created successfully in %.2fs", task_id, create_duration)
            
            # Step 2: Poll for task completion
            result = self._poll_task(session, task_id)
            poll_stats = getattr(self, "_last_poll_stats", {"attempts": 0, "duration": 0.0})
            total_duration = time.time() - run_start
            logger.info(
                "Task %s polled in %.2fs over %s attempts (total runtime %.2fs)",
                task_id,
                poll_stats.get("duration", 0.0),
                poll_stats.get("attempts", 0),
                total_duration,
            )
            if poll_stats.get("duration", 0) > 120 or poll_stats.get("attempts", 0) > 3:
                logger.warning(
                    "Task %s experienced slow polling (attempts=%s duration=%.2fs)",
                    task_id,
                    poll_stats.get("attempts", 0),
                    poll_stats.get("duration", 0.0),
                )

            if not result:
                return self._format_result(None, error=f"Task {task_id} failed or timed out")
            
            # Step 3: Extract and return image information
            return self._format_result(result)
    
    def _create_task(self, session: requests.Session):
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
            response = session.post(url, json=payload, headers=headers, timeout=30, verify=True)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success") and data.get("data", {}).get("taskId"):
                return data["data"]["taskId"]
            else:
                logger.error("Task creation failed with response: %s", data)
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Error: Request timed out while creating task")
            return None
        except requests.exceptions.JSONDecodeError as e:
            logger.error("Failed to parse task creation response: %s", e)
            return None
        except requests.exceptions.RequestException as e:
            logger.error("Error creating task: %s", e, exc_info=True)
            return None

    def _poll_task(self, session: requests.Session, task_id):
        """
        Poll the task status until completion or timeout.
        Returns the task result if successful, None otherwise.
        """
        url = f"{KIE_API_BASE}/playground/recordInfo"
        
        headers = {
            "Authorization": f"Bearer {KIE_API_KEY}"
        }

        params = {
            "taskId": task_id
        }

        attempt = 0
        backoff = float(self.poll_interval)
        start = time.time()
        self._last_poll_stats = {"attempts": 0, "duration": 0.0}

        while attempt < self.max_poll_attempts:
            attempt += 1
            self._last_poll_stats["attempts"] = attempt
            try:
                response = session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30,
                    verify=True,
                )
                response.raise_for_status()

                data = response.json()

                if not data.get("success"):
                    logger.error("Error polling task %s: %s", task_id, data.get("message", "Unknown error"))
                    self._last_poll_stats["duration"] = time.time() - start
                    return None

                task_data = data.get("data", {})
                status = task_data.get("status", "")

                logger.info("Task %s poll attempt %s status=%s", task_id, attempt, status)

                if status == "completed":
                    self._last_poll_stats["duration"] = time.time() - start
                    return task_data
                if status in ("failed", "error"):
                    logger.error("Task %s failed with payload: %s", task_id, task_data)
                    self._last_poll_stats["duration"] = time.time() - start
                    return None
                if status not in ("pending", "processing", "queued"):
                    logger.warning("Task %s returned unknown status '%s'", task_id, status)

            except requests.exceptions.SSLError as e:
                logger.error("KIE SSL error on task %s: %s", task_id, e, exc_info=True)
            except requests.exceptions.Timeout:
                logger.warning("Timeout polling task %s on attempt %s", task_id, attempt)
            except requests.exceptions.JSONDecodeError as e:
                logger.error("Invalid JSON while polling task %s: %s", task_id, e, exc_info=True)
            except requests.exceptions.RequestException as e:
                logger.warning("Network error polling task %s: %s", task_id, e, exc_info=True)

            elapsed = time.time() - start
            if elapsed > self.max_wait_seconds:
                logger.error("Task %s timed out after %.1fs", task_id, elapsed)
                self._last_poll_stats["duration"] = elapsed
                break

            time.sleep(backoff)
            backoff = min(backoff * 1.6, 30.0)

        logger.error(
            "Task %s timed out after %s attempts and %.1fs",
            task_id,
            self.max_poll_attempts,
            time.time() - start,
        )
        self._last_poll_stats["duration"] = time.time() - start
        return None
    
    def _format_result(self, task_data, error=None):
        """
        Format the task result as pure JSON for downstream agent consumption.
        CRITICAL: Returns ONLY JSON - no prose, no headers.
        """
        retryable = False
        if error:
            lowered = error.lower()
            retryable = any(keyword in lowered for keyword in ["timeout", "network", "ssl", "retry"])
            payload = {
                "success": False,
                "error": error,
                "image_url": "",
                "seed": task_data.get("seed", "N/A") if task_data else "N/A",
                "prompt_used": task_data.get("prompt", self.prompt) if task_data else self.prompt,
                "aspect_ratio": self.aspect_ratio,
                "num_images": len(task_data.get("images", [])) if task_data else 0,
                "all_image_urls": [],
                "retryable": retryable,
            }
        else:
            if not task_data:
                payload = {
                    "success": False,
                    "error": "No task data available",
                    "image_url": "",
                    "seed": "N/A",
                    "prompt_used": self.prompt,
                    "aspect_ratio": self.aspect_ratio,
                    "num_images": 0,
                    "all_image_urls": [],
                    "retryable": False,
                }
            else:
                images = task_data.get("images", [])
                if not images:
                    payload = {
                        "success": False,
                        "error": "No images generated",
                        "image_url": "",
                        "seed": task_data.get("seed", "N/A"),
                        "prompt_used": task_data.get("prompt", self.prompt),
                        "aspect_ratio": self.aspect_ratio,
                        "num_images": 0,
                        "all_image_urls": [],
                        "retryable": False,
                    }
                else:
                    payload = {
                        "success": True,
                        "error": None,
                        "image_url": images[0].get("url", ""),
                        "seed": task_data.get("seed", "N/A"),
                        "prompt_used": task_data.get("prompt", self.prompt),
                        "aspect_ratio": self.aspect_ratio,
                        "num_images": len(images),
                        "all_image_urls": [img.get("url") for img in images if img.get("url")],
                        "retryable": False,
                    }

        try:
            normalized = ImageGenerationResultSchema(**payload).normalized()
            return json.dumps(normalized, indent=2)
        except ValidationError as exc:
            logger.error("Image result schema validation failed: %s", exc)
            fallback = {
                "success": False,
                "error": "image_result_validation_failed",
                "details": exc.errors(),
                "raw": payload,
            }
            return json.dumps(fallback, indent=2)


if __name__ == "__main__":
    # Test case
    tool = KieNanoBananaTool(
        prompt="A cinematic minimalistic artwork inspired by Athar. Theme: solitude and contemplation. Mood: calm, meditative. Palette: warm earth tones with soft golden light. Composition: A single figure silhouetted against a vast desert landscape at sunset, with soft depth of field. Background has atmospheric texture with paper grain and cinematic lighting. Tone: poetic, calm, meditative.",
        aspect_ratio="16:9",
        negative_prompt="messy textures, chaotic shapes, distorted Arabic text, low quality"
    )
    print(tool.run())
