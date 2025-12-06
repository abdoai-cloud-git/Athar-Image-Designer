from agency_swarm.tools import BaseTool
from pydantic import Field


class PackagingTool(BaseTool):
    """PackagingTool for delivery agent packaging and export."""
    
    deliverable_key: str = Field(default="final_deliverable", description="Context key for deliverable")
    
    def run(self):
        """Executes the PackagingTool operation."""
        deliverable = self._context.get(self.deliverable_key, {})
        
        result = f"✓ PackagingTool executed successfully"
        
        if "PackagingTool" == "ExportTool":
            result += "\n  Formats: PDF, DOCX, HTML"
        elif "PackagingTool" == "URLGeneratorTool":
            result += "\n  URLs: https://example.com/download"
        elif "PackagingTool" == "SummaryGeneratorTool":
            result += "\n  Summary: Complete delivery package ready"
        
        self._context.set("PackagingTool_output", result)
        
        return result


if __name__ == "__main__":
    tool = PackagingTool()
    print(tool.run())
