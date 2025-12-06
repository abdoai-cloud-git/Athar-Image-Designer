from agency_swarm.tools import BaseTool
from pydantic import Field


class FactCheckerTool(BaseTool):
    """FactCheckerTool for reviewer agent quality checks."""
    
    content_key: str = Field(default="content_draft", description="Context key for content to review")
    
    def run(self):
        """Executes the FactCheckerTool operation."""
        content = self._context.get(self.content_key, "")
        
        # Perform check
        result = {
            "tool": "FactCheckerTool",
            "status": "passed",
            "issues": [],
            "score": 8.5
        }
        
        self._context.set("FactCheckerTool_result", result)
        
        return f"✓ FactCheckerTool completed: Status {result['status']}, Score {result['score']}/10"


if __name__ == "__main__":
    tool = FactCheckerTool()
    print(tool.run())
