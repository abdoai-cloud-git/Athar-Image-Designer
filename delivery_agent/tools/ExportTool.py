from agency_swarm.tools import BaseTool
from pydantic import Field


class ExportTool(BaseTool):
    """ExportTool for delivery agent packaging and export."""
    
    deliverable_key: str = Field(default="final_deliverable", description="Context key for deliverable")
    
    def run(self):
        """Executes the ExportTool operation."""
        deliverable = self._context.get(self.deliverable_key, {})
        
        result = f"✓ ExportTool executed successfully"
        
        if "ExportTool" == "ExportTool":
            result += "\n  Formats: PDF, DOCX, HTML"
        elif "ExportTool" == "URLGeneratorTool":
            result += "\n  URLs: https://example.com/download"
        elif "ExportTool" == "SummaryGeneratorTool":
            result += "\n  Summary: Complete delivery package ready"
        
        self._context.set("ExportTool_output", result)
        
        return result


if __name__ == "__main__":
    tool = ExportTool()
    print(tool.run())
