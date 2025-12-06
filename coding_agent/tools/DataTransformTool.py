from agency_swarm.tools import BaseTool
from pydantic import Field


class DataTransformTool(BaseTool):
    """DataTransformTool for coding agent operations."""
    
    task_description: str = Field(..., description="Description of the technical task")
    parameters: dict = Field(default_factory=dict, description="Additional parameters")
    
    def run(self):
        """Executes the DataTransformTool operation."""
        result = f"✓ DataTransformTool executed: {self.task_description}"
        self._context.set("DataTransformTool_output", result)
        return result


if __name__ == "__main__":
    tool = DataTransformTool(task_description="Test task")
    print(tool.run())
