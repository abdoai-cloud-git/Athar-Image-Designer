from agency_swarm.tools import BaseTool
from pydantic import Field


class TimelineGeneratorTool(BaseTool):
    """
    Generates execution timeline with milestones.
    """
    
    workflow_key: str = Field(default="work_breakdown", description="Context key for workflow")
    
    def run(self):
        """Creates project timeline."""
        workflow = self._context.get(self.workflow_key, {})
        
        if not workflow:
            return "Error: No workflow found"
        
        workflow_plan = workflow.get("workflow_plan", {})
        estimated_time = workflow.get("estimated_time", "15 minutes")
        
        # Create timeline
        timeline = {
            "start": "now",
            "milestones": [],
            "total_time": estimated_time
        }
        
        # Add milestones for each phase
        cumulative_time = 0
        
        for phase_name, phase_details in workflow_plan.items():
            time_str = phase_details.get("time_estimate", "5 minutes")
            
            # Parse time (take average if range)
            if "-" in time_str:
                times = [int(t) for t in time_str.replace(" minutes", "").split("-")]
                time_minutes = sum(times) / 2
            else:
                time_minutes = int(time_str.replace(" minutes", ""))
            
            cumulative_time += time_minutes
            
            timeline["milestones"].append({
                "phase": phase_name,
                "eta": f"{int(cumulative_time)} minutes",
                "agent": phase_details.get("agent")
            })
        
        # Store timeline
        self._context.set("timeline", timeline)
        
        # Format output
        result = "=== Project Timeline ===\n\n"
        result += f"Total Estimated Time: {timeline['total_time']}\n\n"
        result += "Milestones:\n"
        
        for idx, milestone in enumerate(timeline["milestones"], 1):
            result += f"  {idx}. {milestone['phase']} - ETA: {milestone['eta']}\n"
            result += f"     Agent: {milestone['agent']}\n"
        
        return result


if __name__ == "__main__":
    tool = TimelineGeneratorTool()
    print(tool.run())
