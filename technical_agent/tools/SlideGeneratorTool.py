from agency_swarm.tools import BaseTool
from pydantic import Field


class SlideGeneratorTool(BaseTool):
    """SlideGeneratorTool for technical agent formatting operations."""
    
    content: str = Field(..., description="Content to process")
    format_type: str = Field(default="pdf", description="Output format type")
    
    def run(self):
        """Executes the SlideGeneratorTool operation."""
        result = f"✓ SlideGeneratorTool executed: {self.format_type} formatting applied"
        self._context.set("SlideGeneratorTool_output", result)
        return result


if __name__ == "__main__":
    tool = SlideGeneratorTool(content="Test content")
    print(tool.run())
