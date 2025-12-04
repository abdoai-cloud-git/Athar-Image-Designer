from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class GeneratePromptTool(BaseTool):
    """
    Convert creative brief into a complete Nano Banana Pro prompt.
    Generates prompt, negative_prompt, and style parameters optimized for Athar-style imagery.
    """
    
    theme: str = Field(
        ...,
        description="The main theme or subject matter (e.g., 'solitude and contemplation')"
    )
    
    mood: str = Field(
        ...,
        description="The emotional mood (e.g., 'serene, contemplative')"
    )
    
    palette: str = Field(
        ...,
        description="Color palette description (e.g., 'warm earth tones, soft golden light')"
    )
    
    visual_elements: str = Field(
        default="",
        description="Specific visual elements or metaphors to include"
    )
    
    tone: str = Field(
        default="poetic, cinematic, meditative",
        description="Artistic tone for the image"
    )
    
    aspect_ratio: str = Field(
        default="16:9",
        description="Desired aspect ratio: '1:1', '16:9', '9:16', '4:3', '3:4', '21:9', '9:21'"
    )
    
    custom_instructions: str = Field(
        default="",
        description="Any additional custom instructions from the user"
    )

    def run(self):
        """
        Generate a complete image generation prompt based on the creative brief.
        Returns formatted prompt parameters ready for Nano Banana Pro.
        """
        
        # Step 1: Build the main prompt using Athar template
        prompt = self._build_main_prompt()
        
        # Step 2: Build the negative prompt
        negative_prompt = self._build_negative_prompt()
        
        # Step 3: Compile complete output
        output = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": self.aspect_ratio,
            "style": "cinematic-premium",
            "quality": "premium",
            "theme": self.theme,
            "palette": self.palette
        }
        
        # Step 4: Format for output
        return self._format_output(output)
    
    def _build_main_prompt(self):
        """
        Build the main prompt using the Athar-style template.
        """
        # Core Athar prompt structure
        prompt_parts = [
            "A cinematic minimalistic artwork inspired by Athar."
        ]
        
        # Add theme
        if self.theme:
            prompt_parts.append(f"Theme: {self.theme}.")
        
        # Add mood
        if self.mood:
            prompt_parts.append(f"Mood: {self.mood}.")
        
        # Add palette
        if self.palette:
            prompt_parts.append(f"Palette: {self.palette}.")
        
        # Add visual elements/metaphor
        if self.visual_elements:
            prompt_parts.append(f"Visual Metaphor: {self.visual_elements}.")
        
        # Add composition guidelines
        composition = [
            "Composition:",
            "  Soft foreground subject with gentle depth.",
            "  Background atmospheric texture with paper grain and cinematic lighting."
        ]
        prompt_parts.append("\n".join(composition))
        
        # Add tone
        if self.tone:
            prompt_parts.append(f"Tone: {self.tone}.")
        
        # Add technical directives
        prompt_parts.append("Avoid: messy textures, chaotic shapes, distorted Arabic text.")
        
        # Add aspect ratio directive
        prompt_parts.append(f"--ar {self.aspect_ratio}")
        
        # Add style directive
        prompt_parts.append("--style cinematic-premium")
        
        # Add custom instructions if provided
        if self.custom_instructions:
            prompt_parts.append(f"Additional: {self.custom_instructions}")
        
        # Join all parts
        return "\n".join(prompt_parts)
    
    def _build_negative_prompt(self):
        """
        Build comprehensive negative prompt to avoid common issues.
        """
        negative_elements = [
            # Quality issues
            "messy textures",
            "chaotic shapes",
            "low quality",
            "blurry",
            "pixelated",
            "distorted",
            
            # Text issues
            "distorted Arabic text",
            "illegible text",
            "wrong font",
            "text artifacts",
            
            # Style issues
            "oversaturated",
            "harsh lighting",
            "neon colors",
            "artificial",
            
            # Composition issues
            "cluttered",
            "busy composition",
            "multiple subjects",
            "distracting elements",
            
            # Technical issues
            "watermark",
            "signature",
            "frame",
            "border",
            "text overlay"
        ]
        
        return ", ".join(negative_elements)
    
    def _format_output(self, output):
        """
        Format the output as pure JSON for downstream agent consumption.
        CRITICAL: Returns ONLY JSON - no prose, no headers.
        """
        return json.dumps(output, indent=2)


if __name__ == "__main__":
    # Test case
    tool = GeneratePromptTool(
        theme="solitude and contemplation",
        mood="serene, contemplative",
        palette="warm earth tones, soft golden light",
        visual_elements="lone figure, vast landscape, atmospheric depth",
        tone="poetic, cinematic, meditative",
        aspect_ratio="16:9"
    )
    print(tool.run())
