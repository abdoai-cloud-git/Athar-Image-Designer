from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

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
        description="Maximum number of polling attempts before timeout"
    )
    
    poll_interval: int = Field(
        default=5,
        description="Seconds to wait between polling attempts"
    )

    def run(self):
        """
        Execute the image generation workflow through KIE API.
        Returns the image URL, seed, and generation parameters.
        """
        
        if not KIE_API_KEY:
            return json.dumps({"success": False, "error": "KIE_API_KEY not found in environment variables"})
        
        # Step 1: Create the image generation task
        task_id = self._create_task()
        if not task_id:
            return json.dumps({"success": False, "error": "Failed to create image generation task"})
        
        print(f"Task created successfully. Task ID: {task_id}")
        
        # Step 2: Poll for task completion
        result = self._poll_task(task_id)
        if not result:
            return json.dumps({"success": False, "error": f"Task {task_id} failed or timed out"})
        
        # Step 3: Extract and return image information
        return self._format_result(result)
    
    def _create_task(self):
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
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success") and data.get("data", {}).get("taskId"):
                return data["data"]["taskId"]
            else:
                print(f"Task creation failed: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.Timeout:
            print("Error: Request timed out while creating task")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error creating task: {str(e)}")
            return None
    
    def _poll_task(self, task_id):
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
        
        for attempt in range(self.max_poll_attempts):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get("success"):
                    print(f"Error polling task: {data.get('message', 'Unknown error')}")
                    return None
                
                task_data = data.get("data", {})
                status = task_data.get("status", "")
                
                print(f"Attempt {attempt + 1}/{self.max_poll_attempts}: Status = {status}")
                
                if status == "completed":
                    return task_data
                elif status == "failed":
                    print(f"Task failed: {task_data.get('error', 'Unknown error')}")
                    return None
                elif status in ["pending", "processing", "queued"]:
                    # Wait before next poll with exponential backoff
                    wait_time = min(self.poll_interval * (1.5 ** (attempt // 10)), 30)
                    time.sleep(wait_time)
                else:
                    print(f"Unknown status: {status}")
                    time.sleep(self.poll_interval)
                    
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}")
                time.sleep(self.poll_interval)
            except requests.exceptions.RequestException as e:
                print(f"Error polling task: {str(e)}")
                time.sleep(self.poll_interval)
        
        print(f"Task timed out after {self.max_poll_attempts} attempts")
        return None
    
    def _format_result(self, task_data):
        """
        Format the task result into a readable output.
        Returns ONLY JSON - no formatted text or prose.
        """
        images = task_data.get("images", [])
        
        if not images:
            return json.dumps({"success": False, "error": "No images generated"})
        
        # Extract primary image information
        primary_image = images[0]
        
        result = {
            "success": True,
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
