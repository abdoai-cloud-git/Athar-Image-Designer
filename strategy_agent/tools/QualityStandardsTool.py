from agency_swarm.tools import BaseTool
from pydantic import Field


class QualityStandardsTool(BaseTool):
    """
    Defines quality standards and acceptance criteria for the project.
    """
    
    brief_key: str = Field(default="brief", description="Context key for the brief")
    
    def run(self):
        """Defines project quality standards."""
        brief = self._context.get(self.brief_key, {})
        
        if not brief:
            return "Error: No brief found"
        
        # Define standards
        standards = {
            "minimum_score": 8.0,
            "brand_compliance": "required",
            "accuracy_check": "required",
            "tone_validation": "required",
            "acceptance_criteria": [
                "Content addresses all brief objectives",
                "Tone matches target audience",
                "No grammar or spelling errors",
                "Brand guidelines followed",
                "Success criteria met",
                "Professional formatting"
            ]
        }
        
        # Add content-type specific criteria
        content_type = brief.get("content_type", "")
        
        if content_type == "article":
            standards["acceptance_criteria"].extend([
                "Clear structure with subheadings",
                "SEO optimized if applicable"
            ])
        elif content_type == "social_post":
            standards["acceptance_criteria"].extend([
                "Platform-optimized length",
                "Strong hook and CTA"
            ])
        
        # Store standards
        self._context.set("quality_standards", standards)
        
        # Format output
        result = "=== Quality Standards ===\n\n"
        result += f"Minimum Quality Score: {standards['minimum_score']}/10\n"
        result += f"Brand Compliance: {standards['brand_compliance']}\n"
        result += f"Accuracy Check: {standards['accuracy_check']}\n\n"
        result += "Acceptance Criteria:\n"
        
        for idx, criterion in enumerate(standards['acceptance_criteria'], 1):
            result += f"  {idx}. {criterion}\n"
        
        return result


if __name__ == "__main__":
    tool = QualityStandardsTool()
    print(tool.run())
