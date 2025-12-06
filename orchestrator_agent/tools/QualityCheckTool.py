from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class QualityCheckTool(BaseTool):
    """
    Validates final output against quality standards defined in the brief and execution plan.
    Use this tool before final delivery to ensure all requirements are met.
    """
    
    check_type: str = Field(
        ...,
        description="Type of quality check to perform. Options: completeness, standards, brief_alignment, final_validation"
    )
    
    deliverable_key: str = Field(
        default="final_deliverable",
        description="Agency context key where the deliverable to check is stored"
    )
    
    def run(self):
        """
        Performs quality validation checks on final deliverables.
        """
        # Step 1: Load required data from context
        brief = self._context.get("brief", {})
        execution_plan = self._context.get("execution_plan", {})
        deliverable = self._context.get(self.deliverable_key)
        review_report = self._context.get("review_report", {})
        
        if not deliverable:
            return f"Error: No deliverable found at context key '{self.deliverable_key}'"
        
        # Step 2: Perform requested check
        if self.check_type == "completeness":
            return self._check_completeness(brief, deliverable)
        
        elif self.check_type == "standards":
            return self._check_standards(execution_plan, review_report)
        
        elif self.check_type == "brief_alignment":
            return self._check_brief_alignment(brief, deliverable)
        
        elif self.check_type == "final_validation":
            return self._final_validation(brief, execution_plan, review_report, deliverable)
        
        else:
            return f"Error: Invalid check_type '{self.check_type}'. Options: completeness, standards, brief_alignment, final_validation"
    
    def _check_completeness(self, brief, deliverable):
        """Check if all required elements are present"""
        issues = []
        
        # Check if brief objectives are addressed
        objective = brief.get("objective", "")
        if not objective:
            issues.append("⚠ No objective defined in brief")
        
        # Check if deliverable has content
        if isinstance(deliverable, dict):
            if not deliverable.get("content") and not deliverable.get("deliverables"):
                issues.append("⚠ Deliverable appears to be empty")
        elif isinstance(deliverable, str):
            if len(deliverable) < 50:
                issues.append("⚠ Deliverable content is very short")
        
        # Check for required constraints
        constraints = brief.get("constraints", {})
        if constraints.get("must_include"):
            issues.append("ℹ Verify that must_include items are present (manual check needed)")
        
        if issues:
            return f"Completeness Check - Issues Found:\n" + "\n".join(issues)
        else:
            return "✓ Completeness Check Passed - All required elements appear to be present"
    
    def _check_standards(self, execution_plan, review_report):
        """Check if quality standards are met"""
        issues = []
        
        # Get quality standards from plan
        quality_standards = execution_plan.get("quality_standards", {})
        minimum_score = quality_standards.get("minimum_score", 8.0)
        
        # Check review report
        if not review_report:
            return "⚠ No review report available - standards cannot be verified"
        
        overall_score = review_report.get("overall_quality_score", 0)
        review_status = review_report.get("review_status", "")
        
        if overall_score < minimum_score:
            issues.append(f"⚠ Quality score {overall_score}/10 is below minimum {minimum_score}/10")
        
        if review_status != "APPROVED":
            issues.append(f"⚠ Review status is '{review_status}', expected 'APPROVED'")
        
        # Check brand compliance
        brand_compliance = review_report.get("brand_compliance", {})
        if not brand_compliance.get("passed", False):
            issues.append("⚠ Brand compliance check failed")
            if brand_compliance.get("violations"):
                issues.append(f"  Violations: {brand_compliance.get('violations')}")
        
        if issues:
            return f"Standards Check - Issues Found:\n" + "\n".join(issues)
        else:
            return f"✓ Standards Check Passed - Quality score: {overall_score}/10, Status: {review_status}"
    
    def _check_brief_alignment(self, brief, deliverable):
        """Check if deliverable aligns with brief requirements"""
        report = "Brief Alignment Check:\n\n"
        
        # Check objective
        objective = brief.get("objective", "N/A")
        report += f"Objective: {objective}\n"
        report += "→ Manual verification needed: Does deliverable achieve this objective?\n\n"
        
        # Check target audience
        audience = brief.get("target_audience", {})
        if isinstance(audience, dict):
            report += f"Target Audience: {audience.get('demographics', 'N/A')}\n"
        else:
            report += f"Target Audience: {audience}\n"
        report += "→ Manual verification needed: Is content appropriate for this audience?\n\n"
        
        # Check tone
        tone = brief.get("tone", "N/A")
        report += f"Required Tone: {tone}\n"
        report += "→ Verified by Reviewer Agent in review report\n\n"
        
        # Check constraints
        constraints = brief.get("constraints", {})
        if constraints:
            report += "Constraints:\n"
            for key, value in constraints.items():
                report += f"  - {key}: {value}\n"
            report += "→ Verify constraints are met\n"
        
        return report
    
    def _final_validation(self, brief, execution_plan, review_report, deliverable):
        """Comprehensive final validation"""
        report = "=== FINAL VALIDATION ===\n\n"
        
        # Run all checks
        completeness_result = self._check_completeness(brief, deliverable)
        standards_result = self._check_standards(execution_plan, review_report)
        
        report += "1. " + completeness_result + "\n\n"
        report += "2. " + standards_result + "\n\n"
        
        # Overall determination
        if "✓" in completeness_result and "✓" in standards_result:
            report += "\n=== VALIDATION RESULT: PASSED ===\n"
            report += "Deliverable is ready for final delivery to user.\n"
        else:
            report += "\n=== VALIDATION RESULT: ISSUES FOUND ===\n"
            report += "Address issues before proceeding to delivery.\n"
        
        return report


if __name__ == "__main__":
    # Test case
    tool = QualityCheckTool(
        check_type="final_validation",
        deliverable_key="final_deliverable"
    )
    print(tool.run())
