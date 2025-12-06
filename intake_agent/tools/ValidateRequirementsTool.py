from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class ValidateRequirementsTool(BaseTool):
    """
    Validates that all critical requirements are present in the brief.
    Use this tool to identify missing or incomplete information before proceeding to execution.
    """
    
    brief_key: str = Field(
        default="brief",
        description="Agency context key where the brief to validate is stored"
    )
    
    strict_mode: bool = Field(
        default=False,
        description="If True, requires all optional fields. If False, only validates critical fields."
    )
    
    def run(self):
        """
        Validates brief completeness and identifies missing requirements.
        """
        # Step 1: Load brief from context
        brief = self._context.get(self.brief_key, {})
        
        if not brief:
            return f"Error: No brief found at context key '{self.brief_key}'"
        
        # Step 2: Define critical and optional requirements
        critical_fields = {
            "objective": "Clear statement of what needs to be created",
            "content_type": "Type of content (article, social post, etc.)",
            "tone": "Tone/voice for the content"
        }
        
        optional_fields = {
            "target_audience": "Who the content is for",
            "constraints": "Length, format, and other limitations",
            "brand_guidelines": "Brand voice and style rules",
            "success_definition": "How success will be measured",
            "style": "Writing style preferences"
        }
        
        # Step 3: Check critical fields
        missing_critical = []
        incomplete_critical = []
        
        for field, description in critical_fields.items():
            value = brief.get(field)
            if not value:
                missing_critical.append(f"{field}: {description}")
            elif isinstance(value, str) and len(value.strip()) < 5:
                incomplete_critical.append(f"{field}: Value too short or vague")
        
        # Step 4: Check optional fields (in strict mode)
        missing_optional = []
        incomplete_optional = []
        
        if self.strict_mode:
            for field, description in optional_fields.items():
                value = brief.get(field)
                if not value:
                    missing_optional.append(f"{field}: {description}")
                elif isinstance(value, (dict, list)) and not value:
                    incomplete_optional.append(f"{field}: Empty structure")
        
        # Step 5: Validate nested structures
        nested_issues = []
        
        # Check target_audience structure
        audience = brief.get("target_audience", {})
        if isinstance(audience, dict):
            if not audience.get("demographics") and not audience.get("psychographics"):
                nested_issues.append("target_audience: No demographics or psychographics specified")
        
        # Check constraints structure
        constraints = brief.get("constraints", {})
        if isinstance(constraints, dict) and constraints:
            if not constraints.get("word_count") and not constraints.get("format"):
                nested_issues.append("constraints: No specific constraints defined")
        
        # Step 6: Calculate completeness score
        total_fields = len(critical_fields) + (len(optional_fields) if self.strict_mode else 0)
        missing_count = len(missing_critical) + len(missing_optional)
        incomplete_count = len(incomplete_critical) + len(incomplete_optional) + len(nested_issues)
        
        completeness_score = ((total_fields - missing_count - incomplete_count) / total_fields) * 100
        completeness_score = max(0, completeness_score)
        
        # Step 7: Update brief with missing_info
        all_missing = missing_critical + incomplete_critical + missing_optional + incomplete_optional + nested_issues
        brief["missing_info"] = all_missing
        self._context.set(self.brief_key, brief)
        
        # Step 8: Generate validation report
        status = "✓ COMPLETE" if completeness_score >= 90 else "⚠ INCOMPLETE" if completeness_score >= 70 else "✗ NEEDS WORK"
        
        result = f"""
=== Requirements Validation Report ===

Status: {status}
Completeness Score: {completeness_score:.1f}%
Mode: {"Strict (all fields required)" if self.strict_mode else "Standard (critical fields only)"}

"""
        
        if missing_critical:
            result += "❌ Missing Critical Requirements:\n"
            for item in missing_critical:
                result += f"  - {item}\n"
            result += "\n"
        
        if incomplete_critical:
            result += "⚠ Incomplete Critical Fields:\n"
            for item in incomplete_critical:
                result += f"  - {item}\n"
            result += "\n"
        
        if missing_optional:
            result += "ℹ Missing Optional Requirements:\n"
            for item in missing_optional:
                result += f"  - {item}\n"
            result += "\n"
        
        if nested_issues:
            result += "⚠ Nested Structure Issues:\n"
            for item in nested_issues:
                result += f"  - {item}\n"
            result += "\n"
        
        # Step 9: Provide recommendation
        if completeness_score >= 90:
            result += "Recommendation: Brief is sufficiently complete. Proceed to strategy planning.\n"
        elif completeness_score >= 70:
            result += "Recommendation: Brief is mostly complete. Clarify highlighted items for best results.\n"
        else:
            result += "Recommendation: Brief needs more information. Use ClarifyQuestionTool to gather missing requirements.\n"
        
        return result


if __name__ == "__main__":
    # Test case 1: Standard mode
    print("Test 1: Standard validation")
    tool1 = ValidateRequirementsTool(
        brief_key="brief",
        strict_mode=False
    )
    print(tool1.run())
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Strict mode
    print("Test 2: Strict validation")
    tool2 = ValidateRequirementsTool(
        brief_key="brief",
        strict_mode=True
    )
    print(tool2.run())
