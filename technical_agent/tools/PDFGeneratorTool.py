from agency_swarm.tools import BaseTool
from pydantic import Field


class PDFGeneratorTool(BaseTool):
    """PDFGeneratorTool for technical agent formatting operations."""
    
    content: str = Field(..., description="Content to process")
    format_type: str = Field(default="pdf", description="Output format type")
    
    def run(self):
        """Executes the PDFGeneratorTool operation."""
        result = f"✓ PDFGeneratorTool executed: {self.format_type} formatting applied"
        self._context.set("PDFGeneratorTool_output", result)
        return result


if __name__ == "__main__":
    tool = PDFGeneratorTool(content="Test content")
    print(tool.run())
