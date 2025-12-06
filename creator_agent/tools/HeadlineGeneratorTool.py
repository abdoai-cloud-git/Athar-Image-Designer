from agency_swarm.tools import BaseTool
from pydantic import Field


class HeadlineGeneratorTool(BaseTool):
    """Generates compelling headlines."""
    
    topic: str = Field(..., description="Content topic")
    style: str = Field(default="benefit", description="Style: benefit, how-to, list, question")
    
    def run(self):
        """Generates headlines."""
        styles = {
            "benefit": f"Transform Your Business with {self.topic}",
            "how-to": f"How to Master {self.topic} in 2025",
            "list": f"7 Proven Strategies for {self.topic} Success",
            "question": f"Is {self.topic} the Future?"
        }
        
        headline = styles.get(self.style, styles["benefit"])
        
        self._context.set("generated_headline", headline)
        
        return f"✓ Headline: '{headline}'"


if __name__ == "__main__":
    tool = HeadlineGeneratorTool(topic="AI Content Marketing", style="how-to")
    print(tool.run())
