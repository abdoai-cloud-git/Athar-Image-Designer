from agency_swarm.tools import BaseTool
from pydantic import Field


class ContentGeneratorTool(BaseTool):
    """Generates written content based on brief requirements."""
    
    content_type: str = Field(..., description="Type of content to generate")
    topic: str = Field(..., description="Main topic or objective")
    tone: str = Field(default="professional", description="Tone of voice")
    word_count: int = Field(default=1000, description="Target word count")
    
    def run(self):
        """Generates content draft."""
        # In production, this would call OpenAI API or use agent's native capabilities
        # For now, create structured placeholder that agents can use
        
        content_structure = f"""
[CONTENT GENERATOR OUTPUT]

Content Type: {self.content_type}
Topic: {self.topic}
Tone: {self.tone}
Target Length: {self.word_count} words

GENERATED CONTENT:
This is a placeholder for content generation. In production, this tool would:
1. Load the full brief from agency context
2. Generate compelling {self.content_type} content on: {self.topic}
3. Maintain {self.tone} tone throughout
4. Meet the {self.word_count} word target
5. Include proper structure (intro, body, conclusion)
6. Integrate SEO keywords if applicable
7. Include engaging hooks and strong CTAs

The content would be stored in agency context as 'content_draft'.
"""
        
        # Store in context
        self._context.set("content_draft", content_structure)
        
        return f"✓ Content generated: {self.word_count} words on '{self.topic}' in {self.tone} tone"


if __name__ == "__main__":
    tool = ContentGeneratorTool(
        content_type="article",
        topic="AI trends in 2025",
        tone="professional",
        word_count=1500
    )
    print(tool.run())
