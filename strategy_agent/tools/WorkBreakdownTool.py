from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class WorkBreakdownTool(BaseTool):
    """
    Creates a detailed task breakdown structure from a brief.
    Use this tool to decompose content projects into specific, actionable tasks for each agent.
    """
    
    brief_key: str = Field(
        default="brief",
        description="Agency context key where the brief is stored"
    )
    
    def run(self):
        """
        Creates work breakdown structure with task assignments.
        """
        # Step 1: Load brief
        brief = self._context.get(self.brief_key, {})
        
        if not brief:
            return f"Error: No brief found at context key '{self.brief_key}'"
        
        # Step 2: Extract key information
        content_type = brief.get("content_type", "article")
        objective = brief.get("objective", "")
        constraints = brief.get("constraints", {})
        
        # Step 3: Create base workflow phases
        workflow = {
            "phase_1_creation": {
                "agent": "creator_agent",
                "task": f"Generate {content_type} content that achieves: {objective}",
                "deliverable": f"Raw {content_type} draft with all content elements",
                "dependencies": [],
                "time_estimate": "5-8 minutes"
            },
            "phase_4_review": {
                "agent": "reviewer_agent",
                "task": "Validate quality, brand compliance, accuracy, and tone",
                "deliverable": "Quality report with approval or revision requirements",
                "dependencies": [],  # Will be updated based on previous phases
                "time_estimate": "2-3 minutes"
            },
            "phase_5_delivery": {
                "agent": "delivery_agent",
                "task": "Package all deliverables and create final delivery package",
                "deliverable": "Complete delivery package with URLs and summary",
                "dependencies": ["phase_4_review"],
                "time_estimate": "2-3 minutes"
            }
        }
        
        # Step 4: Add technical phase if needed
        needs_technical = False
        
        if content_type in ["landing_page", "email"] or constraints.get("format") in ["html", "json"]:
            needs_technical = True
            workflow["phase_2_technical"] = {
                "agent": "coding_agent",
                "task": "Build technical components (schemas, scripts, or HTML/CSS)",
                "deliverable": "Functional technical components ready for integration",
                "dependencies": [],
                "time_estimate": "3-5 minutes"
            }
        
        # Step 5: Add formatting phase
        format_type = constraints.get("format", "markdown")
        
        if format_type in ["pdf", "docx", "pptx", "html"]:
            workflow["phase_3_formatting"] = {
                "agent": "technical_agent",
                "task": f"Format content as {format_type} with brand styling and layouts",
                "deliverable": f"Formatted {format_type} document ready for review",
                "dependencies": ["phase_1_creation"],
                "time_estimate": "3-4 minutes"
            }
            
            if needs_technical:
                workflow["phase_3_formatting"]["dependencies"].append("phase_2_technical")
            
            # Update review dependencies
            workflow["phase_4_review"]["dependencies"] = ["phase_3_formatting"]
        else:
            # Review depends directly on creation if no formatting
            workflow["phase_4_review"]["dependencies"] = ["phase_1_creation"]
            if needs_technical:
                workflow["phase_4_review"]["dependencies"].append("phase_2_technical")
        
        # Step 6: Determine parallel execution opportunities
        parallel_groups = []
        
        # Creator and Coding can often run in parallel
        if needs_technical:
            parallel_groups.append(["phase_1_creation", "phase_2_technical"])
        
        # Step 7: Calculate total time estimate
        time_values = []
        for phase in workflow.values():
            time_str = phase["time_estimate"].replace(" minutes", "")
            if "-" in time_str:
                avg_time = sum(map(int, time_str.split("-"))) / 2
            else:
                avg_time = int(time_str)
            time_values.append(avg_time)
        
        # Account for parallel execution
        if parallel_groups:
            # Subtract time saved by parallelization (estimate 30% savings)
            total_time = sum(time_values) * 0.7
        else:
            total_time = sum(time_values)
        
        # Add buffer for revisions (1 iteration assumed)
        total_time_with_buffer = total_time * 1.3
        
        # Step 8: Store workflow in context
        work_breakdown = {
            "workflow_plan": workflow,
            "parallel_execution": {
                "enabled": len(parallel_groups) > 0,
                "groups": parallel_groups
            },
            "estimated_time": f"{int(total_time_with_buffer)} minutes",
            "phases_count": len(workflow)
        }
        
        self._context.set("work_breakdown", work_breakdown)
        
        # Step 9: Format and return result
        result = f"""
=== Work Breakdown Structure ===

Total Phases: {len(workflow)}
Estimated Time: {int(total_time_with_buffer)} minutes (with buffer)
Parallel Execution: {"Yes" if parallel_groups else "No"}

Workflow Phases:
"""
        
        for phase_name, phase_details in workflow.items():
            result += f"\n{phase_name.replace('_', ' ').title()}:\n"
            result += f"  Agent: {phase_details['agent']}\n"
            result += f"  Task: {phase_details['task']}\n"
            result += f"  Deliverable: {phase_details['deliverable']}\n"
            result += f"  Dependencies: {', '.join(phase_details['dependencies']) if phase_details['dependencies'] else 'None'}\n"
            result += f"  Time Estimate: {phase_details['time_estimate']}\n"
        
        if parallel_groups:
            result += f"\nParallel Execution Groups:\n"
            for idx, group in enumerate(parallel_groups, 1):
                result += f"  {idx}. {', '.join(group)}\n"
        
        result += "\nWork breakdown has been stored in agency context.\n"
        
        return result


if __name__ == "__main__":
    # Test case
    tool = WorkBreakdownTool(brief_key="brief")
    print(tool.run())
