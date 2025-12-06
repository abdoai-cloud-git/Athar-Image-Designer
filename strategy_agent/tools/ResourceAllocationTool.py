from agency_swarm.tools import BaseTool
from pydantic import Field


class ResourceAllocationTool(BaseTool):
    """
    Assigns agents to tasks based on workflow requirements and agent capabilities.
    """
    
    workflow_key: str = Field(default="work_breakdown", description="Context key for workflow")
    
    def run(self):
        """Allocates agents to workflow tasks."""
        workflow = self._context.get(self.workflow_key, {})
        
        if not workflow:
            return "Error: No workflow found for resource allocation"
        
        workflow_plan = workflow.get("workflow_plan", {})
        
        # Create allocation map
        allocation = {}
        for agent in ["creator_agent", "coding_agent", "technical_agent", "reviewer_agent", "delivery_agent"]:
            allocation[agent] = []
        
        # Assign tasks to agents
        for phase_name, phase_details in workflow_plan.items():
            agent = phase_details.get("agent")
            if agent in allocation:
                allocation[agent].append({
                    "phase": phase_name,
                    "task": phase_details.get("task"),
                    "time": phase_details.get("time_estimate")
                })
        
        # Store allocation
        self._context.set("resource_allocation", allocation)
        
        # Format output
        result = "=== Resource Allocation ===\n\n"
        
        for agent, tasks in allocation.items():
            if tasks:
                result += f"{agent.replace('_', ' ').title()}:\n"
                for task in tasks:
                    result += f"  - {task['phase']}: {task['task'][:60]}...\n"
                    result += f"    Time: {task['time']}\n"
                result += "\n"
        
        return result


if __name__ == "__main__":
    tool = ResourceAllocationTool()
    print(tool.run())
