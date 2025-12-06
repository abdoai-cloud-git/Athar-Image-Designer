from agency_swarm.tools import BaseTool
from pydantic import Field


class BrandVoiceTool(BaseTool):
    """Applies brand voice guidelines to content."""
    
    content: str = Field(..., description="Content to apply brand voice to")
    brand_voice: str = Field(default="professional", description="Brand voice type")
    
    def run(self):
        """Applies brand voice transformations."""
        result = f"[BRAND VOICE APPLIED: {self.brand_voice}]\n\n{self.content}"
        
        self._context.set("branded_content", result)
        
        return f"✓ Brand voice '{self.brand_voice}' applied to content"


if __name__ == "__main__":
    tool = BrandVoiceTool(content="Sample content", brand_voice="authoritative")
    print(tool.run())
