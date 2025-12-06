from agency_swarm.tools import BaseTool
from pydantic import Field


class VariationGeneratorTool(BaseTool):
    """Generates multiple content variations."""
    
    base_content: str = Field(..., description="Base content to create variations from")
    variation_count: int = Field(default=3, description="Number of variations to generate")
    
    def run(self):
        """Creates content variations."""
        variations = []
        
        for i in range(self.variation_count):
            variation = f"Variation {i+1}: {self.base_content} [Modified for different angle/tone]"
            variations.append(variation)
        
        self._context.set("content_variations", variations)
        
        return f"✓ Generated {len(variations)} variations"


if __name__ == "__main__":
    tool = VariationGeneratorTool(base_content="AI is transforming business", variation_count=3)
    print(tool.run())
