from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re


class ExtractBriefTool(BaseTool):
    """
    Extracts structured information from raw user input and converts it into a standardized brief format.
    Use this tool to parse user requests into actionable, structured data.
    """
    
    user_input: str = Field(
        ...,
        description="Raw user input text describing what content they want created"
    )
    
    def run(self):
        """
        Parses user input and extracts key information into structured brief format.
        """
        # Step 1: Initialize brief structure
        brief = {
            "objective": "",
            "content_type": "",
            "target_audience": {},
            "tone": "",
            "style": "",
            "constraints": {},
            "assets_provided": [],
            "missing_info": [],
            "success_definition": {},
            "brand_guidelines": {}
        }
        
        # Step 2: Extract content type
        content_types = {
            "article": ["article", "blog", "post", "written content"],
            "social_post": ["social media", "facebook", "twitter", "linkedin", "instagram"],
            "video_script": ["video", "script", "youtube"],
            "email": ["email", "newsletter", "campaign"],
            "landing_page": ["landing page", "webpage", "website"],
            "presentation": ["presentation", "slides", "deck"]
        }
        
        detected_type = "article"  # default
        user_lower = self.user_input.lower()
        
        for content_type, keywords in content_types.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_type = content_type
                break
        
        brief["content_type"] = detected_type
        
        # Step 3: Extract objective (first meaningful sentence or explicit goal)
        sentences = self.user_input.split(".")
        for sentence in sentences:
            if len(sentence.strip()) > 20 and not sentence.strip().startswith("http"):
                brief["objective"] = sentence.strip()
                break
        
        if not brief["objective"]:
            brief["objective"] = self.user_input[:200].strip()
        
        # Step 4: Extract tone indicators
        tone_keywords = {
            "professional": ["professional", "business", "corporate", "formal"],
            "casual": ["casual", "friendly", "conversational", "relaxed"],
            "technical": ["technical", "detailed", "in-depth", "expert"],
            "authoritative": ["authoritative", "confident", "expert", "definitive"],
            "friendly": ["friendly", "warm", "welcoming", "approachable"]
        }
        
        detected_tones = []
        for tone, keywords in tone_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_tones.append(tone)
        
        brief["tone"] = detected_tones[0] if detected_tones else "professional"
        
        # Step 5: Extract audience information
        audience_patterns = [
            r"for ([\w\s]+) audience",
            r"targeting ([\w\s]+)",
            r"aimed at ([\w\s]+)"
        ]
        
        for pattern in audience_patterns:
            match = re.search(pattern, user_lower)
            if match:
                brief["target_audience"] = {"demographics": match.group(1).strip()}
                break
        
        # Step 6: Extract constraints (word count, length, format)
        word_count_match = re.search(r"(\d+)\s*word", user_lower)
        if word_count_match:
            brief["constraints"]["word_count"] = int(word_count_match.group(1))
        
        # Extract URLs as assets
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.user_input)
        if urls:
            brief["assets_provided"] = [{"type": "url", "url": url} for url in urls]
        
        # Step 7: Identify missing critical information
        missing = []
        
        if not brief.get("target_audience") or not brief["target_audience"]:
            missing.append("target_audience")
        
        if not brief.get("constraints"):
            missing.append("constraints")
        
        if not brief.get("brand_guidelines") or not brief["brand_guidelines"]:
            missing.append("brand_guidelines")
        
        brief["missing_info"] = missing
        
        # Step 8: Store brief in agency context
        self._context.set("brief", brief)
        
        # Step 9: Return formatted brief summary
        result = f"""
=== Brief Extraction Complete ===

Content Type: {brief['content_type']}
Objective: {brief['objective']}

Tone: {brief['tone']}
Target Audience: {brief.get('target_audience', {}).get('demographics', 'Not specified')}

Constraints:
{json.dumps(brief.get('constraints', {}), indent=2) if brief.get('constraints') else '  None specified'}

Assets Provided: {len(brief.get('assets_provided', []))}

Missing Information ({len(missing)} items):
{chr(10).join(['  - ' + item for item in missing]) if missing else '  None - brief is complete'}

The structured brief has been stored in agency context.

Next Step: {"Clarify missing information" if missing else "Proceed to strategy planning"}
"""
        return result


if __name__ == "__main__":
    # Test case
    tool = ExtractBriefTool(
        user_input="Create a professional article about AI trends for business executives. Should be around 1500 words. Here's a reference: https://example.com/ai-report"
    )
    print(tool.run())
