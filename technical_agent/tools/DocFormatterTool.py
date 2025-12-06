from agency_swarm.tools import BaseTool
from pydantic import Field


class DocFormatterTool(BaseTool):
    """DocFormatterTool for technical agent formatting operations."""
    
    content: str = Field(..., description="Content to process")
    format_type: str = Field(default="pdf", description="Output format type")
    
    def run(self):
        """Executes the DocFormatterTool operation."""
        result = f"✓ DocFormatterTool executed: {self.format_type} formatting applied"
        self._context.set("DocFormatterTool_output", result)
        return result


if __name__ == "__main__":
    tool = DocFormatterTool(content="Test content")
    print(tool.run())
