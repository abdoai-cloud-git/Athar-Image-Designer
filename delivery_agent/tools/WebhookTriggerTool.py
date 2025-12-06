from agency_swarm.tools import BaseTool
from pydantic import Field


class WebhookTriggerTool(BaseTool):
    """WebhookTriggerTool for delivery agent packaging and export."""
    
    deliverable_key: str = Field(default="final_deliverable", description="Context key for deliverable")
    
    def run(self):
        """Executes the WebhookTriggerTool operation."""
        deliverable = self._context.get(self.deliverable_key, {})
        
        result = f"✓ WebhookTriggerTool executed successfully"
        
        if "WebhookTriggerTool" == "ExportTool":
            result += "\n  Formats: PDF, DOCX, HTML"
        elif "WebhookTriggerTool" == "URLGeneratorTool":
            result += "\n  URLs: https://example.com/download"
        elif "WebhookTriggerTool" == "SummaryGeneratorTool":
            result += "\n  Summary: Complete delivery package ready"
        
        self._context.set("WebhookTriggerTool_output", result)
        
        return result


if __name__ == "__main__":
    tool = WebhookTriggerTool()
    print(tool.run())
