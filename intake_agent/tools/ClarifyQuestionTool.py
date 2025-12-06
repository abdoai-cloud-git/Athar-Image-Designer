from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class ClarifyQuestionTool(BaseTool):
    """
    Generates clarifying questions for missing or incomplete information in the brief.
    Use this tool to create user-friendly questions that gather required details.
    """
    
    missing_field: str = Field(
        ...,
        description="The field that needs clarification (e.g., 'target_audience', 'constraints', 'brand_guidelines')"
    )
    
    context_info: str = Field(
        default="",
        description="Additional context about what's already known, to frame the question better"
    )
    
    question_style: str = Field(
        default="conversational",
        description="Style of question. Options: conversational, direct, multiple_choice"
    )
    
    def run(self):
        """
        Generates appropriate clarifying questions based on missing field.
        """
        # Step 1: Define question templates for each field type
        question_templates = {
            "target_audience": {
                "conversational": "To create content that really resonates, could you tell me more about your target audience? For example, who are they (demographics), what challenges do they face, and what are their goals?",
                "direct": "Who is your target audience? Please provide demographics, pain points, and goals.",
                "multiple_choice": "Who is your primary target audience?\na) Business executives\nb) Technical professionals\nc) General consumers\nd) Small business owners\ne) Other (please specify)"
            },
            "tone": {
                "conversational": "What tone would you like for this content? Would you prefer something formal and professional, or more casual and conversational? Or perhaps something in between?",
                "direct": "What tone should the content have? (e.g., professional, casual, technical, friendly, authoritative)",
                "multiple_choice": "What tone should the content have?\na) Professional and formal\nb) Casual and friendly\nc) Technical and detailed\nd) Authoritative and confident\ne) Conversational and approachable"
            },
            "constraints": {
                "conversational": "Are there any specific constraints I should be aware of? For example, desired length (word count), specific format requirements, or platforms where this will be published?",
                "direct": "What constraints apply? Specify word count, format, platform, deadline, must-include items, and must-avoid topics.",
                "multiple_choice": "What's the desired length for this content?\na) Short (300-500 words)\nb) Medium (500-1000 words)\nc) Long (1000-2000 words)\nd) Very long (2000+ words)\ne) No preference"
            },
            "brand_guidelines": {
                "conversational": "Do you have any brand guidelines I should follow? This could include your brand voice, specific vocabulary to use or avoid, style preferences, or examples of content you love.",
                "direct": "What are your brand guidelines? Include brand voice, vocabulary rules, style preferences, and prohibited elements.",
                "multiple_choice": "Do you have existing brand guidelines?\na) Yes, I'll provide a document\nb) Yes, but informal (I'll describe them)\nc) No, but I have preferences\nd) No, please use best practices\ne) Not sure"
            },
            "style": {
                "conversational": "What writing style works best for your needs? Should it be data-driven with lots of facts, storytelling-focused, conversational, or something else?",
                "direct": "What writing style should be used? (e.g., data-driven, storytelling, conversational, formal, technical)",
                "multiple_choice": "What writing style do you prefer?\na) Data-driven with statistics\nb) Storytelling with examples\nc) Conversational and engaging\nd) Formal and structured\ne) Technical and detailed"
            },
            "success_definition": {
                "conversational": "How will we know this content is successful? What metrics or outcomes are you hoping to achieve?",
                "direct": "How do you define success for this content? Specify KPIs, quality thresholds, and desired outcomes.",
                "multiple_choice": "What's the primary goal for this content?\na) Drive engagement (likes, shares)\nb) Generate leads or conversions\nc) Educate audience\nd) Build brand awareness\ne) Establish thought leadership"
            },
            "objective": {
                "conversational": "I'd like to make sure I understand exactly what you need. Could you describe the main goal of this content in a bit more detail?",
                "direct": "What is the specific objective of this content? Be as detailed as possible about what you want to achieve.",
                "multiple_choice": "What's the main purpose of this content?\na) Promote a product/service\nb) Educate the audience\nc) Build brand authority\nd) Generate leads\ne) Other (please specify)"
            },
            "content_type": {
                "conversational": "What type of content are you looking for? For example, a blog article, social media post, email, video script, or something else?",
                "direct": "What content type do you need? (e.g., article, social post, email, video script, landing page)",
                "multiple_choice": "What type of content do you need?\na) Blog article or long-form post\nb) Social media post\nc) Email or newsletter\nd) Video script\ne) Landing page\nf) Other (please specify)"
            }
        }
        
        # Step 2: Get question template for missing field
        if self.missing_field not in question_templates:
            # Generic question for unknown fields
            question = f"Could you provide more information about {self.missing_field.replace('_', ' ')}?"
        else:
            question = question_templates[self.missing_field].get(
                self.question_style, 
                question_templates[self.missing_field]["conversational"]
            )
        
        # Step 3: Add context if provided
        if self.context_info:
            question = f"{self.context_info}\n\n{question}"
        
        # Step 4: Add helpful tips for certain fields
        tips = {
            "target_audience": "\n\nTip: The more specific you are about your audience, the better we can tailor the content to resonate with them.",
            "brand_guidelines": "\n\nTip: If you have a brand style guide or examples of content you love, sharing those would be very helpful!",
            "constraints": "\n\nTip: Being specific about constraints helps us deliver exactly what you need on the first try."
        }
        
        if self.missing_field in tips:
            question += tips[self.missing_field]
        
        # Step 5: Log the question for tracking
        questions_asked = self._context.get("questions_asked", [])
        questions_asked.append({
            "field": self.missing_field,
            "question": question,
            "style": self.question_style,
            "timestamp": "now"
        })
        self._context.set("questions_asked", questions_asked)
        
        # Step 6: Format and return the question
        result = f"""
=== Clarification Needed ===

Field: {self.missing_field.replace('_', ' ').title()}

Question:
{question}

---
[Awaiting user response to continue]
"""
        return result


if __name__ == "__main__":
    # Test cases
    print("Test 1: Conversational style")
    tool1 = ClarifyQuestionTool(
        missing_field="target_audience",
        question_style="conversational"
    )
    print(tool1.run())
    
    print("\n" + "="*60 + "\n")
    
    print("Test 2: Multiple choice style")
    tool2 = ClarifyQuestionTool(
        missing_field="tone",
        question_style="multiple_choice",
        context_info="You mentioned this is for business executives."
    )
    print(tool2.run())
    
    print("\n" + "="*60 + "\n")
    
    print("Test 3: Direct style")
    tool3 = ClarifyQuestionTool(
        missing_field="constraints",
        question_style="direct"
    )
    print(tool3.run())
