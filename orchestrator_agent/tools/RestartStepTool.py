from agency_swarm.tools import BaseTool
from pydantic import Field


class RestartStepTool(BaseTool):
    """
    Restarts a failed workflow step with corrections.
    Use this tool when a step fails and needs to be retried with updated parameters or context.
    """
    
    step_name: str = Field(
        ...,
        description="Name of the step to restart (e.g., 'content_creation', 'review', 'formatting')"
    )
    
    agent: str = Field(
        ...,
        description="Agent responsible for this step"
    )
    
    corrections: str = Field(
        ...,
        description="Description of corrections made before restart (what changed to fix the issue)"
    )
    
    context_updates: dict = Field(
        default_factory=dict,
        description="Any context updates to apply before restarting (e.g., {'brief': {...}, 'parameters': {...}})"
    )
    
    def run(self):
        """
        Restarts a failed workflow step with corrections.
        """
        # Step 1: Validate inputs
        if not self.step_name or not self.agent:
            return "Error: step_name and agent parameters are required"
        
        # Step 2: Apply context updates if provided
        if self.context_updates:
            for key, value in self.context_updates.items():
                self._context.set(key, value)
            context_msg = f"Applied {len(self.context_updates)} context updates"
        else:
            context_msg = "No context updates applied"
        
        # Step 3: Log the restart
        restarts = self._context.get("restarts", [])
        restart_record = {
            "step_name": self.step_name,
            "agent": self.agent,
            "corrections": self.corrections,
            "context_updates": list(self.context_updates.keys()) if self.context_updates else [],
            "timestamp": "now",
            "restart_number": len([r for r in restarts if r.get("step_name") == self.step_name]) + 1
        }
        restarts.append(restart_record)
        self._context.set("restarts", restarts)
        
        # Step 4: Update workflow state to reflect restart
        workflow_state = self._context.get("workflow_state", {})
        agents = workflow_state.get("agents", {})
        
        # Reset agent status from failed to in_progress
        if self.agent in agents and agents[self.agent] == "failed":
            agents[self.agent] = "in_progress"
            workflow_state["agents"] = agents
            self._context.set("workflow_state", workflow_state)
        
        # Step 5: Clear any previous error for this step
        errors = self._context.get("errors", [])
        # Keep errors for logging but mark this step as retrying
        for error in errors:
            if error.get("agent") == self.agent:
                error["status"] = "retrying"
        self._context.set("errors", errors)
        
        # Step 6: Return restart confirmation
        restart_number = restart_record["restart_number"]
        
        result = f"""
=== Step Restart Initiated ===

Step: {self.step_name}
Agent: {self.agent}
Restart Number: {restart_number}

Corrections Applied:
{self.corrections}

Context Updates:
{context_msg}

Status: Ready to re-execute
Next Action: Delegate task to {self.agent} with updated parameters

Note: Maximum recommended restarts per step is 2. Current: {restart_number}
"""
        
        if restart_number >= 3:
            result += "\n⚠ WARNING: This step has been restarted 3+ times. Consider escalating to user for guidance."
        
        return result


if __name__ == "__main__":
    # Test case
    tool = RestartStepTool(
        step_name="content_creation",
        agent="creator_agent",
        corrections="Added missing brand guidelines to context and clarified tone requirements",
        context_updates={
            "brief": {"tone": "professional", "brand_voice": "authoritative"}
        }
    )
    print(tool.run())
