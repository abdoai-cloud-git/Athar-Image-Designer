from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class DefineCriteriaTool(BaseTool):
    """
    Establishes measurable success criteria for the content project.
    Use this tool to define clear quality standards and success metrics based on the brief.
    """
    
    content_type: str = Field(
        ...,
        description="Type of content (article, social_post, email, etc.)"
    )
    
    objective: str = Field(
        ...,
        description="Main objective of the content"
    )
    
    custom_kpis: list[str] = Field(
        default_factory=list,
        description="Custom KPIs or success metrics provided by user"
    )
    
    def run(self):
        """
        Defines success criteria and quality standards based on content type and objective.
        """
        # Step 1: Initialize success definition structure
        success_definition = {
            "primary_kpi": "",
            "quality_threshold": 8.0,  # Default minimum quality score
            "engagement_target": "",
            "acceptance_criteria": [],
            "measurement_methods": []
        }
        
        # Step 2: Define KPIs based on content type
        kpi_mapping = {
            "article": {
                "primary_kpi": "Content quality and reader engagement",
                "engagement_target": "High readability score, social shares, time on page",
                "acceptance_criteria": [
                    "Addresses all key points from brief",
                    "Clear structure with subheadings",
                    "Engaging introduction and conclusion",
                    "SEO optimized (if applicable)",
                    "No grammar or spelling errors"
                ]
            },
            "social_post": {
                "primary_kpi": "Engagement rate (likes, comments, shares)",
                "engagement_target": "High visibility and interaction",
                "acceptance_criteria": [
                    "Attention-grabbing hook in first sentence",
                    "Appropriate length for platform",
                    "Clear call-to-action",
                    "Platform-optimized formatting",
                    "Compelling visual concept (if applicable)"
                ]
            },
            "email": {
                "primary_kpi": "Open rate and click-through rate",
                "engagement_target": "Reader takes desired action",
                "acceptance_criteria": [
                    "Compelling subject line",
                    "Personalized opening",
                    "Clear single CTA",
                    "Scannable format with bullets",
                    "Mobile-friendly"
                ]
            },
            "video_script": {
                "primary_kpi": "Watch time and viewer retention",
                "engagement_target": "Viewers watch to completion",
                "acceptance_criteria": [
                    "Hook within first 10 seconds",
                    "Clear structure with segments",
                    "Natural speaking flow",
                    "Visual direction cues included",
                    "Strong closing CTA"
                ]
            },
            "landing_page": {
                "primary_kpi": "Conversion rate",
                "engagement_target": "Visitors complete desired action",
                "acceptance_criteria": [
                    "Clear value proposition above fold",
                    "Compelling headlines and copy",
                    "Strong CTAs throughout",
                    "Social proof elements",
                    "Mobile responsive"
                ]
            }
        }
        
        # Step 3: Get criteria for content type (or use generic)
        if self.content_type in kpi_mapping:
            criteria = kpi_mapping[self.content_type]
            success_definition.update(criteria)
        else:
            # Generic criteria
            success_definition["primary_kpi"] = "Content quality and objective achievement"
            success_definition["engagement_target"] = "Content meets stated objectives"
            success_definition["acceptance_criteria"] = [
                "Addresses all requirements from brief",
                "Appropriate for target audience",
                "Correct tone and style",
                "No errors",
                "Professionally formatted"
            ]
        
        # Step 4: Add custom KPIs if provided
        if self.custom_kpis:
            success_definition["custom_kpis"] = self.custom_kpis
            success_definition["measurement_methods"].extend([
                f"Track: {kpi}" for kpi in self.custom_kpis
            ])
        
        # Step 5: Define objective-specific criteria
        objective_lower = self.objective.lower()
        
        if "educate" in objective_lower or "teach" in objective_lower:
            success_definition["acceptance_criteria"].append("Content is clear and educational")
            success_definition["acceptance_criteria"].append("Includes examples or explanations")
        
        if "convert" in objective_lower or "sell" in objective_lower:
            success_definition["acceptance_criteria"].append("Includes persuasive elements")
            success_definition["acceptance_criteria"].append("Strong call-to-action present")
        
        if "brand" in objective_lower or "awareness" in objective_lower:
            success_definition["acceptance_criteria"].append("Consistent with brand voice")
            success_definition["acceptance_criteria"].append("Memorable and shareable")
        
        # Step 6: Define measurement methods
        success_definition["measurement_methods"] = [
            "Quality score from Reviewer Agent (minimum 8.0/10)",
            "Brand compliance validation",
            "Tone and style analysis",
            "Error detection and correction",
            "User satisfaction feedback"
        ]
        
        # Step 7: Store in brief
        brief = self._context.get("brief", {})
        brief["success_definition"] = success_definition
        self._context.set("brief", brief)
        
        # Step 8: Format and return results
        result = f"""
=== Success Criteria Defined ===

Content Type: {self.content_type.replace('_', ' ').title()}
Objective: {self.objective}

Primary KPI: {success_definition['primary_kpi']}
Quality Threshold: {success_definition['quality_threshold']}/10
Engagement Target: {success_definition['engagement_target']}

Acceptance Criteria:
"""
        
        for idx, criterion in enumerate(success_definition['acceptance_criteria'], 1):
            result += f"  {idx}. {criterion}\n"
        
        result += "\nMeasurement Methods:\n"
        for idx, method in enumerate(success_definition['measurement_methods'], 1):
            result += f"  {idx}. {method}\n"
        
        if self.custom_kpis:
            result += f"\nCustom KPIs:\n"
            for idx, kpi in enumerate(self.custom_kpis, 1):
                result += f"  {idx}. {kpi}\n"
        
        result += "\nSuccess criteria have been stored in the brief.\n"
        
        return result


if __name__ == "__main__":
    # Test case
    tool = DefineCriteriaTool(
        content_type="article",
        objective="Educate business executives about AI trends in 2025",
        custom_kpis=["Generate 50+ social shares", "Average read time > 5 minutes"]
    )
    print(tool.run())
