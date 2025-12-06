from agency_swarm.tools import BaseTool
from pydantic import Field


class TemplateInjectionTool(BaseTool):
    """TemplateInjectionTool for technical agent formatting operations."""
    
    content: str = Field(..., description="Content to process")
    format_type: str = Field(default="pdf", description="Output format type")
    
    def run(self):
        """Executes the TemplateInjectionTool operation."""
        result = f"✓ TemplateInjectionTool executed: {self.format_type} formatting applied"
        self._context.set("TemplateInjectionTool_output", result)
        return result


if __name__ == "__main__":
    tool = TemplateInjectionTool(content="Test content")
    print(tool.run())
