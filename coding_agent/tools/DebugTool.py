from agency_swarm.tools import BaseTool
from pydantic import Field


class DebugTool(BaseTool):
    """DebugTool for coding agent operations."""
    
    task_description: str = Field(..., description="Description of the technical task")
    parameters: dict = Field(default_factory=dict, description="Additional parameters")
    
    def run(self):
        """Executes the DebugTool operation."""
        result = f"✓ DebugTool executed: {self.task_description}"
        self._context.set("DebugTool_output", result)
        return result


if __name__ == "__main__":
    tool = DebugTool(task_description="Test task")
    print(tool.run())
