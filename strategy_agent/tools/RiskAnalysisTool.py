from agency_swarm.tools import BaseTool
from pydantic import Field


class RiskAnalysisTool(BaseTool):
    """
    Identifies potential risks in the content project and suggests mitigation strategies.
    Use this tool to proactively plan for potential issues.
    """
    
    brief_key: str = Field(default="brief", description="Context key for the brief")
    workflow_key: str = Field(default="work_breakdown", description="Context key for workflow")
    
    def run(self):
        """Analyzes project risks and creates mitigation plan."""
        brief = self._context.get(self.brief_key, {})
        workflow = self._context.get(self.workflow_key, {})
        
        if not brief:
            return "Error: No brief found for risk analysis"
        
        # Identify risks
        risks = []
        
        # Risk 1: Content complexity
        objective = brief.get("objective", "")
        if len(objective) > 200 or "complex" in objective.lower():
            risks.append({
                "risk": "Content complexity may require multiple revisions",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Build 2 revision cycles into timeline, ensure clear brief",
                "contingency": "Escalate to user if complexity exceeds expectations"
            })
        
        # Risk 2: Missing brand guidelines
        if not brief.get("brand_guidelines"):
            risks.append({
                "risk": "Lack of brand guidelines may lead to off-brand content",
                "probability": "high",
                "impact": "medium",
                "mitigation": "Use professional standards and request brand guidelines from user",
                "contingency": "Request brand review before final delivery"
            })
        
        # Risk 3: Vague requirements
        missing_info = brief.get("missing_info", [])
        if len(missing_info) > 2:
            risks.append({
                "risk": "Incomplete brief may lead to misaligned content",
                "probability": "high",
                "impact": "high",
                "mitigation": "Clarify all missing requirements before execution",
                "contingency": "Pause execution until requirements are complete"
            })
        
        # Risk 4: Technical requirements
        constraints = brief.get("constraints", {})
        if constraints.get("format") in ["html", "interactive"]:
            risks.append({
                "risk": "Technical implementation complexity",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Allocate extra time for coding agent, test thoroughly",
                "contingency": "Simplify technical requirements if needed"
            })
        
        # Risk 5: Tight timeline
        phases_count = workflow.get("phases_count", 4)
        if phases_count > 4:
            risks.append({
                "risk": "Complex workflow may exceed expected timeline",
                "probability": "medium",
                "impact": "low",
                "mitigation": "Use parallel execution where possible",
                "contingency": "Communicate adjusted timeline to user"
            })
        
        # Store risks
        self._context.set("risks", risks)
        
        # Format output
        result = "=== Risk Analysis ===\n\n"
        result += f"Total Risks Identified: {len(risks)}\n\n"
        
        for idx, risk in enumerate(risks, 1):
            result += f"{idx}. Risk: {risk['risk']}\n"
            result += f"   Probability: {risk['probability']} | Impact: {risk['impact']}\n"
            result += f"   Mitigation: {risk['mitigation']}\n"
            result += f"   Contingency: {risk['contingency']}\n\n"
        
        return result


if __name__ == "__main__":
    tool = RiskAnalysisTool()
    print(tool.run())
