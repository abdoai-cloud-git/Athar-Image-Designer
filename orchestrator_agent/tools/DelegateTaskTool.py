from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class DelegateTaskTool(BaseTool):
    """
    Delegates a specific task to a specialist agent in the workflow.
    Use this tool to assign work to agents based on the execution plan.
    """
    
    target_agent: str = Field(
        ..., 
        description="Name of the target agent to delegate to. Options: intake_agent, strategy_agent, creator_agent, coding_agent, technical_agent, reviewer_agent, delivery_agent"
    )
    
    task_description: str = Field(
        ..., 
        description="Clear description of the task to be performed by the target agent"
    )
    
    context_keys: list[str] = Field(
        default_factory=list,
        description="List of agency context keys the agent needs access to (e.g., ['brief', 'plan', 'content_draft'])"
    )
    
    priority: str = Field(
        default="normal",
        description="Priority level of the task. Options: low, normal, high, critical"
    )
    
    def run(self):
        """
        Delegates a task to a specialist agent.
        Stores task details in agency context for tracking.
        """
        # Step 1: Validate target agent
        valid_agents = [
            "intake_agent", "strategy_agent", "creator_agent", 
            "coding_agent", "technical_agent", "reviewer_agent", 
            "delivery_agent"
        ]
        
        if self.target_agent not in valid_agents:
            return f"Error: Invalid target agent '{self.target_agent}'. Must be one of: {', '.join(valid_agents)}"
        
        # Step 2: Create delegation record
        delegation = {
            "target_agent": self.target_agent,
            "task_description": self.task_description,
            "context_keys": self.context_keys,
            "priority": self.priority,
            "status": "delegated",
            "timestamp": "now"  # In production, use actual timestamp
        }
        
        # Step 3: Store delegation in agency context for tracking
        delegations = self._context.get("delegations", [])
        delegations.append(delegation)
        self._context.set("delegations", delegations)
        
        # Step 4: Provide context keys to target agent
        for key in self.context_keys:
            if not self._context.get(key):
                return f"Warning: Context key '{key}' not found. Task delegated but agent may be missing required context."
        
        # Step 5: Return delegation confirmation
        result = f"""
Task Delegated Successfully

Target Agent: {self.target_agent}
Task: {self.task_description}
Priority: {self.priority}
Context Provided: {', '.join(self.context_keys) if self.context_keys else 'None'}

Status: Ready for agent to begin work
"""
        
        return result


if __name__ == "__main__":
    # Test case
    tool = DelegateTaskTool(
        target_agent="intake_agent",
        task_description="Extract structured brief from user input",
        context_keys=["user_request"],
        priority="high"
    )
    print(tool.run())
