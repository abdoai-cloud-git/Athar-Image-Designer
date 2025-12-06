from agency_swarm.tools import BaseTool
from pydantic import Field


class BrandStyleTool(BaseTool):
    """BrandStyleTool for technical agent formatting operations."""
    
    content: str = Field(..., description="Content to process")
    format_type: str = Field(default="pdf", description="Output format type")
    
    def run(self):
        """Executes the BrandStyleTool operation."""
        result = f"✓ BrandStyleTool executed: {self.format_type} formatting applied"
        self._context.set("BrandStyleTool_output", result)
        return result


if __name__ == "__main__":
    tool = BrandStyleTool(content="Test content")
    print(tool.run())
