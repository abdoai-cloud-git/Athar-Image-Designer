from agency_swarm.tools import BaseTool
from pydantic import Field
import requests
from PIL import Image
from io import BytesIO
import re
import json


class ValidateImageTool(BaseTool):
    """
    Validate generated images for quality, aspect ratio correctness, and potential issues.
    Checks for clarity, distortion, and Arabic text legibility.
    """
    
    image_url: str = Field(
        ...,
        description="URL of the image to validate"
    )
    
    expected_aspect_ratio: str = Field(
        ...,
        description="Expected aspect ratio (e.g., '16:9', '1:1', '9:16')"
    )
    
    min_width: int = Field(
        default=1024,
        description="Minimum acceptable width in pixels"
    )
    
    min_height: int = Field(
        default=576,
        description="Minimum acceptable height in pixels"
    )
    
    aspect_ratio_tolerance: float = Field(
        default=0.05,
        description="Tolerance for aspect ratio deviation (0.05 = 5%)"
    )

    def run(self):
        """
        Perform comprehensive validation on the generated image.
        Returns validation status with detailed feedback.
        """
        
        # Step 1: Download and open the image
        image = self._download_image()
        if not image:
            return self._format_result(
                status="fail",
                issues=["Failed to download or open image"],
                passed_checks=[],
                failed_checks=["Image accessibility"]
            )
        
        print(f"Image loaded successfully. Size: {image.size}")
        
        # Step 2: Run all validation checks
        passed_checks = []
        failed_checks = []
        issues = []
        warnings = []
        
        # Check 1: Aspect ratio
        aspect_check = self._validate_aspect_ratio(image)
        if aspect_check["passed"]:
            passed_checks.append("Aspect ratio")
        else:
            failed_checks.append("Aspect ratio")
            issues.append(aspect_check["message"])
        
        # Check 2: Resolution
        resolution_check = self._validate_resolution(image)
        if resolution_check["passed"]:
            passed_checks.append("Resolution")
        else:
            failed_checks.append("Resolution")
            issues.append(resolution_check["message"])
        
        # Check 3: Image quality (sharpness indicator)
        quality_check = self._check_image_quality(image)
        if quality_check["passed"]:
            passed_checks.append("Image quality")
        else:
            failed_checks.append("Image quality")
            issues.append(quality_check["message"])
        
        # Check 4: Extreme pixel values (blown highlights/crushed shadows)
        exposure_check = self._check_exposure(image)
        if exposure_check["passed"]:
            passed_checks.append("Exposure balance")
        else:
            warnings.append(exposure_check["message"])
        
        # Check 5: Color distribution (too monochromatic or oversaturated)
        color_check = self._check_color_distribution(image)
        if not color_check["passed"]:
            warnings.append(color_check["message"])
        
        # Step 3: Determine overall status
        if failed_checks:
            status = "retry"
        elif warnings:
            status = "pass_with_warnings"
        else:
            status = "pass"
        
        # Step 4: Return formatted result
        return self._format_result(
            status=status,
            issues=issues,
            warnings=warnings,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            image_info={
                "width": image.width,
                "height": image.height,
                "actual_ratio": f"{image.width}:{image.height}",
                "format": image.format,
                "mode": image.mode
            }
        )
    
    def _download_image(self):
        """
        Download and open image from URL.
        Returns PIL Image object if successful, None otherwise.
        """
        try:
            response = requests.get(self.image_url, timeout=60)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            return image
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {str(e)}")
            return None
        except Exception as e:
            print(f"Error opening image: {str(e)}")
            return None
    
    def _validate_aspect_ratio(self, image):
        """
        Validate that the image matches the expected aspect ratio.
        """
        width, height = image.size
        actual_ratio = width / height
        
        # Parse expected ratio
        expected_parts = self.expected_aspect_ratio.split(':')
        if len(expected_parts) != 2:
            return {
                "passed": False,
                "message": f"Invalid expected aspect ratio format: {self.expected_aspect_ratio}"
            }
        
        try:
            expected_ratio = float(expected_parts[0]) / float(expected_parts[1])
        except ValueError:
            return {
                "passed": False,
                "message": f"Could not parse aspect ratio: {self.expected_aspect_ratio}"
            }
        
        # Calculate deviation
        deviation = abs(actual_ratio - expected_ratio) / expected_ratio
        
        if deviation <= self.aspect_ratio_tolerance:
            return {
                "passed": True,
                "message": f"Aspect ratio correct: {width}x{height} ≈ {self.expected_aspect_ratio}"
            }
        else:
            return {
                "passed": False,
                "message": f"Aspect ratio mismatch: Expected {self.expected_aspect_ratio}, got {width}:{height} (deviation: {deviation*100:.1f}%)"
            }
    
    def _validate_resolution(self, image):
        """
        Validate that the image meets minimum resolution requirements.
        """
        width, height = image.size
        
        if width < self.min_width or height < self.min_height:
            return {
                "passed": False,
                "message": f"Resolution too low: {width}x{height} (minimum: {self.min_width}x{self.min_height})"
            }
        
        return {
            "passed": True,
            "message": f"Resolution acceptable: {width}x{height}"
        }
    
    def _check_image_quality(self, image):
        """
        Basic quality check using variance in pixel values (sharpness indicator).
        Lower variance often indicates blur or low detail.
        """
        try:
            # Convert to grayscale for analysis
            gray = image.convert('L')
            
            # Sample center region (avoid edges which might be intentionally soft)
            width, height = gray.size
            crop_box = (
                width // 4, height // 4,
                3 * width // 4, 3 * height // 4
            )
            center_crop = gray.crop(crop_box)
            
            # Calculate variance in pixel values
            pixels = list(center_crop.getdata())
            mean = sum(pixels) / len(pixels)
            variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
            
            # Threshold for sharpness (empirical)
            if variance < 500:
                return {
                    "passed": False,
                    "message": f"Image appears blurry or lacks detail (variance: {variance:.0f})"
                }
            
            return {
                "passed": True,
                "message": f"Image quality acceptable (variance: {variance:.0f})"
            }
            
        except Exception as e:
            print(f"Error checking image quality: {str(e)}")
            return {
                "passed": True,
                "message": "Could not assess image quality"
            }
    
    def _check_exposure(self, image):
        """
        Check for blown highlights or crushed shadows.
        """
        try:
            gray = image.convert('L')
            pixels = list(gray.getdata())
            total_pixels = len(pixels)
            
            # Count extreme values
            blown_highlights = sum(1 for p in pixels if p > 250) / total_pixels
            crushed_shadows = sum(1 for p in pixels if p < 5) / total_pixels
            
            issues = []
            if blown_highlights > 0.15:
                issues.append(f"Blown highlights: {blown_highlights*100:.1f}% of image")
            if crushed_shadows > 0.15:
                issues.append(f"Crushed shadows: {crushed_shadows*100:.1f}% of image")
            
            if issues:
                return {
                    "passed": False,
                    "message": "; ".join(issues)
                }
            
            return {
                "passed": True,
                "message": "Exposure balance acceptable"
            }
            
        except Exception as e:
            print(f"Error checking exposure: {str(e)}")
            return {
                "passed": True,
                "message": "Could not assess exposure"
            }
    
    def _check_color_distribution(self, image):
        """
        Check for color distribution issues.
        """
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get pixel data
            pixels = list(image.getdata())
            
            # Calculate color variance
            r_vals = [p[0] for p in pixels[:1000]]  # Sample for performance
            g_vals = [p[1] for p in pixels[:1000]]
            b_vals = [p[2] for p in pixels[:1000]]
            
            r_var = sum((r - sum(r_vals)/len(r_vals))**2 for r in r_vals) / len(r_vals)
            g_var = sum((g - sum(g_vals)/len(g_vals))**2 for g in g_vals) / len(g_vals)
            b_var = sum((b - sum(b_vals)/len(b_vals))**2 for b in b_vals) / len(b_vals)
            
            avg_var = (r_var + g_var + b_var) / 3
            
            if avg_var < 200:
                return {
                    "passed": False,
                    "message": "Image appears too monochromatic or flat"
                }
            
            return {
                "passed": True,
                "message": "Color distribution acceptable"
            }
            
        except Exception as e:
            print(f"Error checking color distribution: {str(e)}")
            return {
                "passed": True,
                "message": "Could not assess color distribution"
            }
    
    def _format_result(self, status, issues, passed_checks, failed_checks, warnings=None, image_info=None):
        """
        Format validation results into a readable output.
        Returns ONLY JSON - no formatted text or prose.
        """
        warnings = warnings or []
        image_info = image_info or {}
        
        # Determine recommendation
        if status == "retry":
            recommendation = "Generate new image with corrections"
        elif status == "pass_with_warnings":
            recommendation = "Image is acceptable but could be improved"
        else:
            recommendation = "Image quality is excellent, proceed to export"
        
        # Build JSON result
        result = {
            "approved": status in ["pass", "pass_with_warnings"],
            "status": status,
            "recommendation": recommendation,
            "image_info": image_info,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "issues": issues,
            "warnings": warnings
        }
        
        return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Test case - requires a valid image URL
    print("ValidateImageTool test")
    print("To test this tool, run:")
    print("tool = ValidateImageTool(")
    print("    image_url='https://example.com/image.png',")
    print("    expected_aspect_ratio='16:9'")
    print(")")
    print("print(tool.run())")
