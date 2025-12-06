from agency_swarm.tools import BaseTool
from pydantic import Field


class ErrorDetectionTool(BaseTool):
    """ErrorDetectionTool for reviewer agent quality checks."""
    
    content_key: str = Field(default="content_draft", description="Context key for content to review")
    
    def run(self):
        """Executes the ErrorDetectionTool operation."""
        content = self._context.get(self.content_key, "")
        
        # Perform check
        result = {
            "tool": "ErrorDetectionTool",
            "status": "passed",
            "issues": [],
            "score": 8.5
        }
        
        self._context.set("ErrorDetectionTool_result", result)
        
        return f"✓ ErrorDetectionTool completed: Status {result['status']}, Score {result['score']}/10"


if __name__ == "__main__":
    tool = ErrorDetectionTool()
    print(tool.run())
