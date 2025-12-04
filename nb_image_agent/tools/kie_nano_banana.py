"""
KIE API wrapper for Nano Banana Pro image generation.
All image generation requests MUST go through KIE's API endpoints.
"""
from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import time
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class KienanoBanana(BaseTool):
    """
    Tool for generating images using Nano Banana Pro via KIE API.
    Submits tasks to KIE's playground API and polls for completion.
    """
    
    prompt: str = Field(
        ...,
        description="The complete Nano Banana prompt for image generation, including style and aspect ratio parameters."
    )
    
    aspect_ratio: str = Field(
        default="16:9",
        description="Aspect ratio for the image (e.g., '16:9', '1:1', '9:16')."
    )
    
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Negative prompt to avoid unwanted elements in the image."
    )
    
    style: Optional[str] = Field(
        default="cinematic-premium",
        description="Style preset for the image generation."
    )
    
    max_poll_attempts: int = Field(
        default=60,
        description="Maximum number of polling attempts (default 60, ~5 minutes at 5s intervals)."
    )
    
    poll_interval: int = Field(
        default=5,
        description="Seconds to wait between polling attempts."
    )

    def run(self):
        """
        Creates an image generation task via KIE API and polls until completion.
        Returns the final image URL(s) and task metadata.
        """
        # Step 1: Get API configuration from environment
        api_key = os.getenv("KIE_API_KEY")
        api_base = os.getenv("KIE_API_BASE", "https://api.kie.ai/api/v1")
        
        if not api_key:
            return "Error: KIE_API_KEY environment variable is not set."
        
        # Step 2: Prepare task creation request
        create_task_url = f"{api_base}/playground/createTask"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": self.prompt,
            "aspect_ratio": self.aspect_ratio,
            "style": self.style
        }
        
        if self.negative_prompt:
            payload["negative_prompt"] = self.negative_prompt
        
        # Step 3: Submit task creation request with retries
        task_id = None
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    create_task_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                task_id = result.get("taskId") or result.get("task_id")
                
                if task_id:
                    break
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    return f"Error: Failed to create task after {max_retries} attempts: {str(e)}"
        
        if not task_id:
            return "Error: Task creation succeeded but no taskId was returned."
        
        # Step 4: Poll for task completion
        record_info_url = f"{api_base}/playground/recordInfo"
        
        for attempt in range(self.max_poll_attempts):
            try:
                response = requests.get(
                    record_info_url,
                    params={"taskId": task_id},
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                task_info = response.json()
                
                status = task_info.get("status", "").lower()
                
                if status == "completed":
                    # Extract image URL(s) from task result
                    image_url = self._extract_image_url(task_info)
                    seed = task_info.get("seed") or task_info.get("seed_value")
                    
                    return {
                        "status": "completed",
                        "task_id": task_id,
                        "image_url": image_url,
                        "seed": seed,
                        "prompt_used": self.prompt,
                        "aspect_ratio": self.aspect_ratio,
                        "task_info": task_info
                    }
                
                elif status in ["failed", "error", "cancelled"]:
                    error_msg = task_info.get("error") or task_info.get("message", "Unknown error")
                    return {
                        "status": "failed",
                        "task_id": task_id,
                        "error": error_msg
                    }
                
                # Status is pending or processing, continue polling
                time.sleep(self.poll_interval)
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_poll_attempts - 1:
                    time.sleep(self.poll_interval)
                    continue
                else:
                    return {
                        "status": "error",
                        "task_id": task_id,
                        "error": f"Polling failed after {self.max_poll_attempts} attempts: {str(e)}"
                    }
        
        # Timeout reached
        return {
            "status": "timeout",
            "task_id": task_id,
            "error": f"Task did not complete within {self.max_poll_attempts * self.poll_interval} seconds"
        }
    
    def _extract_image_url(self, task_info: Dict[str, Any]) -> str:
        """
        Extracts the image URL from task info response.
        Handles various possible response structures.
        """
        # Try different possible keys for image URL
        possible_keys = [
            "image_url",
            "imageUrl",
            "image",
            "url",
            "result_url",
            "resultUrl",
            "output_url",
            "outputUrl"
        ]
        
        # Check top level
        for key in possible_keys:
            if key in task_info and task_info[key]:
                url = task_info[key]
                if isinstance(url, str) and (url.startswith("http") or url.startswith("https")):
                    return url
        
        # Check nested structures
        if "result" in task_info:
            result = task_info["result"]
            if isinstance(result, dict):
                for key in possible_keys:
                    if key in result and result[key]:
                        url = result[key]
                        if isinstance(url, str) and (url.startswith("http") or url.startswith("https")):
                            return url
            elif isinstance(result, str) and (result.startswith("http") or result.startswith("https")):
                return result
        
        if "data" in task_info:
            data = task_info["data"]
            if isinstance(data, dict):
                for key in possible_keys:
                    if key in data and data[key]:
                        url = data[key]
                        if isinstance(url, str) and (url.startswith("http") or url.startswith("https")):
                            return url
        
        # If no URL found, return placeholder
        return "Image URL not found in response"


if __name__ == "__main__":
    # Test the tool
    tool = KienanoBanana(
        prompt="A cinematic minimalistic artwork inspired by Athar. Theme: peace. Mood: calm. --ar 16:9 --style cinematic-premium",
        aspect_ratio="16:9"
    )
    result = tool.run()
    print(result)
