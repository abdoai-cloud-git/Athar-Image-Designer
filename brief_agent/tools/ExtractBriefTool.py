from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re


class ExtractBriefTool(BaseTool):
    """
    Extract creative brief elements from user input or Athar text excerpts.
    Identifies theme, tone, mood, palette, visual metaphors, and keywords for image generation.
    """
    
    user_input: str = Field(
        ...,
        description="The user's text input, description, or Athar excerpt to analyze"
    )
    
    additional_context: str = Field(
        default="",
        description="Additional context about the Athar brand, style, or project requirements"
    )

    def run(self):
        """
        Analyze the input text and extract creative brief components.
        Returns a structured JSON brief with all extracted elements.
        """
        
        # Step 1: Extract core elements
        theme = self._extract_theme()
        mood = self._extract_mood()
        tone = self._extract_tone()
        palette = self._extract_palette()
        visual_elements = self._extract_visual_elements()
        keywords = self._extract_keywords()
        
        # Step 2: Build brief dictionary
        brief = {
            "theme": theme,
            "mood": mood,
            "tone": tone,
            "palette": palette,
            "visual_elements": visual_elements,
            "keywords": keywords,
            "original_input": self.user_input[:200] + "..." if len(self.user_input) > 200 else self.user_input
        }
        
        # Step 3: Format output
        return self._format_brief(brief)
    
    def _extract_theme(self):
        """
        Extract the main theme or subject matter from the input.
        """
        input_lower = self.user_input.lower()
        
        # Theme patterns to look for
        theme_patterns = {
            "solitude": ["solitude", "alone", "isolation", "lonely", "solitary"],
            "contemplation": ["contemplate", "reflection", "thinking", "meditation", "mindful"],
            "journey": ["journey", "travel", "path", "voyage", "expedition"],
            "nature": ["nature", "natural", "landscape", "wilderness", "outdoors"],
            "spirituality": ["spiritual", "divine", "sacred", "prayer", "faith"],
            "time": ["time", "moment", "ephemeral", "fleeting", "eternal"],
            "memory": ["memory", "nostalgia", "remembrance", "past", "forgotten"],
            "human_connection": ["connection", "relationship", "together", "unity", "bond"],
            "struggle": ["struggle", "challenge", "difficulty", "hardship", "adversity"],
            "hope": ["hope", "aspiration", "dream", "wish", "optimism"],
            "silence": ["silence", "quiet", "stillness", "peace", "calm"],
            "identity": ["identity", "self", "who am i", "belonging", "roots"]
        }
        
        detected_themes = []
        for theme, keywords in theme_patterns.items():
            if any(keyword in input_lower for keyword in keywords):
                detected_themes.append(theme.replace("_", " "))
        
        if detected_themes:
            return ", ".join(detected_themes[:2])  # Return top 2 themes
        
        # Default to analyzing sentence structure
        if len(self.user_input) > 50:
            return "abstract narrative"
        else:
            return "minimalist expression"
    
    def _extract_mood(self):
        """
        Extract the emotional mood from the input.
        """
        input_lower = self.user_input.lower()
        
        mood_patterns = {
            "melancholic": ["sad", "melancholy", "sorrow", "grief", "wistful", "longing"],
            "serene": ["calm", "peaceful", "tranquil", "serene", "gentle", "quiet"],
            "contemplative": ["thoughtful", "pensive", "reflective", "meditative"],
            "nostalgic": ["nostalgic", "reminiscent", "bygone", "memory", "remember"],
            "hopeful": ["hopeful", "optimistic", "bright", "uplifting", "positive"],
            "mysterious": ["mysterious", "enigmatic", "unknown", "shadowy", "obscure"],
            "dramatic": ["dramatic", "intense", "powerful", "striking", "bold"],
            "intimate": ["intimate", "personal", "close", "private", "tender"]
        }
        
        for mood, keywords in mood_patterns.items():
            if any(keyword in input_lower for keyword in keywords):
                return mood
        
        # Default based on Athar style
        return "serene, contemplative"
    
    def _extract_tone(self):
        """
        Extract the artistic tone from the input.
        """
        # Athar is known for poetic, cinematic, and meditative tones
        input_lower = self.user_input.lower()
        
        tone_keywords = {
            "poetic": ["poetry", "poetic", "lyrical", "verse", "metaphor"],
            "cinematic": ["cinematic", "visual", "frame", "scene", "shot"],
            "meditative": ["meditative", "zen", "mindful", "still", "quiet"],
            "dramatic": ["dramatic", "intense", "powerful", "emotional"],
            "minimalist": ["minimal", "simple", "clean", "sparse", "essential"]
        }
        
        detected_tones = []
        for tone, keywords in tone_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                detected_tones.append(tone)
        
        if detected_tones:
            return ", ".join(detected_tones[:2])
        
        # Default Athar tone
        return "poetic, cinematic, meditative"
    
    def _extract_palette(self):
        """
        Extract or infer color palette from the input.
        """
        input_lower = self.user_input.lower()
        
        # Color keywords
        color_mentions = []
        color_keywords = {
            "warm earth tones": ["earth", "sand", "desert", "clay", "ochre", "terracotta"],
            "cool blues": ["blue", "azure", "cerulean", "navy", "indigo"],
            "golden light": ["gold", "golden", "amber", "honey", "sunlit"],
            "muted pastels": ["pastel", "soft", "muted", "pale", "gentle"],
            "deep shadows": ["shadow", "dark", "noir", "charcoal", "midnight"],
            "warm neutrals": ["beige", "cream", "ivory", "neutral", "taupe"],
            "sunset tones": ["sunset", "dusk", "twilight", "orange", "pink"],
            "monochromatic": ["monochrome", "black and white", "grayscale"]
        }
        
        for palette, keywords in color_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                color_mentions.append(palette)
        
        if color_mentions:
            return ", ".join(color_mentions[:2])
        
        # Default Athar palette
        return "warm earth tones, soft golden light"
    
    def _extract_visual_elements(self):
        """
        Extract visual elements or metaphors from the input.
        """
        input_lower = self.user_input.lower()
        
        element_patterns = {
            "lone figure": ["person", "figure", "silhouette", "man", "woman", "human"],
            "vast landscape": ["landscape", "horizon", "expanse", "vast", "endless"],
            "desert": ["desert", "dunes", "sand", "arid"],
            "water": ["water", "sea", "ocean", "river", "waves"],
            "mountains": ["mountain", "peak", "summit", "ridge"],
            "sky": ["sky", "clouds", "heavens", "firmament"],
            "light rays": ["light", "rays", "beam", "glow", "radiance"],
            "archway": ["arch", "door", "doorway", "gate", "portal"],
            "shadows": ["shadow", "shade", "silhouette", "darkness"],
            "texture": ["texture", "grain", "pattern", "surface"]
        }
        
        detected_elements = []
        for element, keywords in element_patterns.items():
            if any(keyword in input_lower for keyword in keywords):
                detected_elements.append(element)
        
        if detected_elements:
            return ", ".join(detected_elements[:3])
        
        # Default Athar visual elements
        return "atmospheric depth, soft focus, cinematic framing"
    
    def _extract_keywords(self):
        """
        Extract key descriptive words from the input.
        """
        # Remove common stopwords
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "can", "this",
            "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', self.user_input.lower())
        
        # Filter stopwords and get unique keywords
        keywords = [w for w in words if w not in stopwords]
        unique_keywords = list(dict.fromkeys(keywords))  # Preserve order
        
        return ", ".join(unique_keywords[:10])
    
    def _format_brief(self, brief):
        """
        Format the brief into a structured output.
        """
        output = f"""
=== CREATIVE BRIEF ===

Theme: {brief['theme']}
Mood: {brief['mood']}
Tone: {brief['tone']}
Palette: {brief['palette']}
Visual Elements: {brief['visual_elements']}
Keywords: {brief['keywords']}

Original Input:
{brief['original_input']}

=== BRIEF JSON ===
{json.dumps(brief, indent=2)}

The brief has been extracted and is ready for the Art Direction Agent.
"""
        return output.strip()


if __name__ == "__main__":
    # Test case
    tool = ExtractBriefTool(
        user_input="Create an image of solitude in the desert at sunset. A lone figure contemplates the vast expanse before them, bathed in golden light. The mood should be peaceful and meditative, with warm earth tones and soft shadows."
    )
    print(tool.run())
