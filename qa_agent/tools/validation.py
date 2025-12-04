"""
Validation tools for image quality assurance.
Checks aspect ratio, clarity, distortion, and Arabic text legibility.
"""
from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
from typing import Optional, Dict, Any
from PIL import Image
import io
import math

class Validation(BaseTool):
    """
    Tool for validating generated images against quality criteria.
    Checks aspect ratio, clarity, distortion, and Arabic text legibility.
    """
    
    image_url: str = Field(
        ...,
        description="URL of the image to validate."
    )
    
    expected_aspect_ratio: str = Field(
        ...,
        description="Expected aspect ratio in format 'width:height' (e.g., '16:9', '1:1')."
    )
    
    check_arabic_legibility: bool = Field(
        default=True,
        description="Whether to check for Arabic text legibility in the image."
    )

    def run(self):
        """
        Validates the image against quality criteria.
        Returns validation status and detailed results.
        """
        # Step 1: Download image
        try:
            response = requests.get(self.image_url, timeout=30)
            response.raise_for_status()
            image_bytes = io.BytesIO(response.content)
            image = Image.open(image_bytes)
            image.load()  # Load image data
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to download or open image: {str(e)}"
            }
        
        # Step 2: Check aspect ratio
        aspect_ratio_result = self._check_aspect_ratio(image, self.expected_aspect_ratio)
        
        # Step 3: Check clarity and distortion
        clarity_result = self._check_clarity(image)
        
        # Step 4: Check Arabic legibility (if enabled)
        arabic_result = None
        if self.check_arabic_legibility:
            arabic_result = self._check_arabic_legibility(image)
        
        # Step 5: Determine overall status
        all_passed = (
            aspect_ratio_result["passed"] and
            clarity_result["passed"] and
            (not self.check_arabic_legibility or arabic_result["passed"])
        )
        
        status = "passed" if all_passed else "retry"
        
        # Step 6: Compile correction notes if failed
        correction_notes = []
        if not aspect_ratio_result["passed"]:
            correction_notes.append(aspect_ratio_result["note"])
        if not clarity_result["passed"]:
            correction_notes.append(clarity_result["note"])
        if self.check_arabic_legibility and arabic_result and not arabic_result["passed"]:
            correction_notes.append(arabic_result["note"])
        
        return {
            "status": status,
            "image_url": self.image_url,
            "aspect_ratio_check": aspect_ratio_result,
            "clarity_check": clarity_result,
            "arabic_legibility_check": arabic_result if self.check_arabic_legibility else None,
            "correction_notes": correction_notes if correction_notes else None,
            "all_checks_passed": all_passed
        }
    
    def _check_aspect_ratio(self, image: Image.Image, expected: str) -> Dict[str, Any]:
        """
        Checks if image aspect ratio matches expected ratio.
        Allows 5% tolerance.
        """
        width, height = image.size
        
        # Parse expected aspect ratio
        try:
            parts = expected.split(":")
            expected_width = float(parts[0])
            expected_height = float(parts[1])
            expected_ratio = expected_width / expected_height
        except Exception:
            return {
                "passed": False,
                "note": f"Invalid expected aspect ratio format: {expected}"
            }
        
        actual_ratio = width / height
        tolerance = 0.05  # 5% tolerance
        
        ratio_diff = abs(actual_ratio - expected_ratio) / expected_ratio
        
        passed = ratio_diff <= tolerance
        
        return {
            "passed": passed,
            "expected_ratio": expected,
            "expected_value": expected_ratio,
            "actual_ratio": f"{width}:{height}",
            "actual_value": actual_ratio,
            "difference": ratio_diff,
            "note": f"Aspect ratio mismatch: expected {expected} ({expected_ratio:.3f}), got {width}:{height} ({actual_ratio:.3f})" if not passed else None
        }
    
    def _check_clarity(self, image: Image.Image) -> Dict[str, Any]:
        """
        Checks image clarity and detects potential distortion.
        Uses basic heuristics: resolution check and edge detection.
        """
        width, height = image.size
        
        # Check minimum resolution
        min_resolution = 512  # Minimum dimension
        resolution_passed = width >= min_resolution and height >= min_resolution
        
        # Basic sharpness check using Laplacian variance approximation
        # Convert to grayscale for analysis
        gray = image.convert("L")
        
        # Calculate variance of pixel differences (simple sharpness metric)
        import numpy as np
        img_array = np.array(gray)
        
        # Calculate gradient magnitude
        grad_x = np.abs(np.diff(img_array, axis=1))
        grad_y = np.abs(np.diff(img_array, axis=0))
        
        # Average gradient magnitude as sharpness indicator
        sharpness = np.mean(grad_x) + np.mean(grad_y)
        
        # Threshold for acceptable sharpness (adjustable)
        min_sharpness = 10.0  # Empirical threshold
        
        sharpness_passed = sharpness >= min_sharpness
        
        # Check for obvious distortion (extreme aspect ratios or very small images)
        distortion_passed = width > 100 and height > 100
        
        passed = resolution_passed and sharpness_passed and distortion_passed
        
        notes = []
        if not resolution_passed:
            notes.append(f"Resolution too low: {width}x{height} (minimum {min_resolution}x{min_resolution})")
        if not sharpness_passed:
            notes.append(f"Image appears blurry or lacks detail (sharpness: {sharpness:.2f})")
        if not distortion_passed:
            notes.append("Image dimensions suggest possible distortion")
        
        return {
            "passed": passed,
            "resolution": f"{width}x{height}",
            "sharpness_score": float(sharpness),
            "note": "; ".join(notes) if notes else None
        }
    
    def _check_arabic_legibility(self, image: Image.Image) -> Dict[str, Any]:
        """
        Heuristic check for Arabic text legibility.
        Checks for text-like regions and basic readability indicators.
        This is a simplified check - full OCR would require additional libraries.
        """
        # Convert to grayscale
        gray = image.convert("L")
        
        # Basic heuristic: Check for high-contrast regions that might be text
        # Arabic text typically has distinct edges and contrast
        
        import numpy as np
        img_array = np.array(gray)
        
        # Calculate local variance (text regions have higher variance)
        # Simple approach: check for regions with high edge density
        grad_x = np.abs(np.diff(img_array, axis=1))
        grad_y = np.abs(np.diff(img_array, axis=0))
        
        edge_density = np.mean(grad_x) + np.mean(grad_y)
        
        # Check contrast (text needs good contrast)
        contrast = np.std(img_array)
        
        # Heuristic thresholds
        min_edge_density = 15.0
        min_contrast = 30.0
        
        edge_passed = edge_density >= min_edge_density
        contrast_passed = contrast >= min_contrast
        
        # Check for potential text regions (high variance areas)
        # Divide image into blocks and check variance
        block_size = 32
        blocks_high_variance = 0
        total_blocks = 0
        
        for y in range(0, img_array.shape[0] - block_size, block_size):
            for x in range(0, img_array.shape[1] - block_size, block_size):
                block = img_array[y:y+block_size, x:x+block_size]
                block_variance = np.var(block)
                total_blocks += 1
                if block_variance > 500:  # Threshold for text-like regions
                    blocks_high_variance += 1
        
        text_region_ratio = blocks_high_variance / total_blocks if total_blocks > 0 else 0
        text_region_passed = text_region_ratio > 0.05  # At least 5% of image has text-like regions
        
        passed = edge_passed and contrast_passed and text_region_passed
        
        notes = []
        if not edge_passed:
            notes.append(f"Low edge density suggests text may be blurry (edge density: {edge_density:.2f})")
        if not contrast_passed:
            notes.append(f"Low contrast may affect Arabic text legibility (contrast: {contrast:.2f})")
        if not text_region_passed:
            notes.append("No clear text-like regions detected in image")
        
        return {
            "passed": passed,
            "edge_density": float(edge_density),
            "contrast": float(contrast),
            "text_region_ratio": float(text_region_ratio),
            "note": "; ".join(notes) if notes else "Arabic text appears legible" if passed else None
        }


if __name__ == "__main__":
    # Test the tool
    tool = Validation(
        image_url="https://example.com/test.jpg",
        expected_aspect_ratio="16:9"
    )
    result = tool.run()
    print(result)
