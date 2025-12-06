from agency_swarm.tools import BaseTool
from pydantic import Field


class HookGeneratorTool(BaseTool):
    """Generates attention-grabbing hooks for content."""
    
    topic: str = Field(..., description="Content topic")
    audience: str = Field(..., description="Target audience")
    hook_type: str = Field(default="question", description="Type: question, statistic, statement, story")
    
    def run(self):
        """Generates engaging hooks."""
        hooks = {
            "question": f"What if {self.topic} could transform your approach to {self.audience}?",
            "statistic": f"85% of {self.audience} are missing out on {self.topic} opportunities.",
            "statement": f"{self.topic} is revolutionizing how {self.audience} work.",
            "story": f"Meet Sarah, a {self.audience} who discovered {self.topic}..."
        }
        
        hook = hooks.get(self.hook_type, hooks["question"])
        
        self._context.set("generated_hook", hook)
        
        return f"✓ Hook generated: '{hook}'"


if __name__ == "__main__":
    tool = HookGeneratorTool(topic="AI automation", audience="business leaders", hook_type="question")
    print(tool.run())
