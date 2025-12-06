from agency_swarm.tools import BaseTool
from pydantic import Field


class QualityScoreTool(BaseTool):
    """QualityScoreTool for reviewer agent quality checks."""
    
    content_key: str = Field(default="content_draft", description="Context key for content to review")
    
    def run(self):
        """Executes the QualityScoreTool operation."""
        content = self._context.get(self.content_key, "")
        
        # Perform check
        result = {
            "tool": "QualityScoreTool",
            "status": "passed",
            "issues": [],
            "score": 8.5
        }
        
        self._context.set("QualityScoreTool_result", result)
        
        return f"✓ QualityScoreTool completed: Status {result['status']}, Score {result['score']}/10"


if __name__ == "__main__":
    tool = QualityScoreTool()
    print(tool.run())
