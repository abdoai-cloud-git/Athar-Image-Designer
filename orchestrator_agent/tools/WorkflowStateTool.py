from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class WorkflowStateTool(BaseTool):
    """
    Tracks and manages the state of the workflow across all phases and agents.
    Use this tool to monitor progress, update status, and retrieve workflow information.
    """
    
    action: str = Field(
        ...,
        description="Action to perform. Options: get_status, update_status, get_history, get_current_phase"
    )
    
    phase: str = Field(
        default="",
        description="Current workflow phase (1_understanding, 2_execution, 3_evaluation, 4_delivery). Required for update_status action."
    )
    
    agent_status: dict = Field(
        default_factory=dict,
        description="Dictionary of agent statuses when updating. Format: {'agent_name': 'in_progress|completed|failed'}"
    )
    
    def run(self):
        """
        Manages workflow state tracking and reporting.
        """
        # Step 1: Handle different actions
        if self.action == "get_status":
            return self._get_status()
        
        elif self.action == "update_status":
            return self._update_status()
        
        elif self.action == "get_history":
            return self._get_history()
        
        elif self.action == "get_current_phase":
            return self._get_current_phase()
        
        else:
            return f"Error: Invalid action '{self.action}'. Options: get_status, update_status, get_history, get_current_phase"
    
    def _get_status(self):
        """Get current workflow status"""
        workflow_state = self._context.get("workflow_state", {
            "current_phase": "1_understanding",
            "agents": {},
            "start_time": "now",
            "history": []
        })
        
        status_report = f"""
=== Workflow Status ===

Current Phase: {workflow_state.get('current_phase', 'Not started')}
Started: {workflow_state.get('start_time', 'N/A')}

Agent Status:
"""
        
        agents = workflow_state.get("agents", {})
        if agents:
            for agent_name, status in agents.items():
                status_icon = "⏳" if status == "in_progress" else "✓" if status == "completed" else "✗" if status == "failed" else "○"
                status_report += f"  {status_icon} {agent_name}: {status}\n"
        else:
            status_report += "  No agents currently assigned\n"
        
        # Add delegation info
        delegations = self._context.get("delegations", [])
        active_delegations = [d for d in delegations if d.get("status") == "delegated"]
        
        if active_delegations:
            status_report += f"\nActive Delegations: {len(active_delegations)}"
        
        return status_report
    
    def _update_status(self):
        """Update workflow status"""
        if not self.phase:
            return "Error: phase parameter required for update_status action"
        
        workflow_state = self._context.get("workflow_state", {
            "current_phase": "1_understanding",
            "agents": {},
            "start_time": "now",
            "history": []
        })
        
        # Update phase
        old_phase = workflow_state.get("current_phase")
        workflow_state["current_phase"] = self.phase
        
        # Update agent statuses
        if self.agent_status:
            current_agents = workflow_state.get("agents", {})
            current_agents.update(self.agent_status)
            workflow_state["agents"] = current_agents
        
        # Add to history
        history = workflow_state.get("history", [])
        history.append({
            "phase_transition": f"{old_phase} -> {self.phase}" if old_phase != self.phase else f"updated {self.phase}",
            "agents_updated": self.agent_status,
            "timestamp": "now"
        })
        workflow_state["history"] = history
        
        # Save updated state
        self._context.set("workflow_state", workflow_state)
        
        return f"Workflow state updated: Now in phase {self.phase}"
    
    def _get_history(self):
        """Get workflow history"""
        workflow_state = self._context.get("workflow_state", {})
        history = workflow_state.get("history", [])
        
        if not history:
            return "No workflow history available yet"
        
        history_report = "=== Workflow History ===\n\n"
        for idx, event in enumerate(history, 1):
            history_report += f"{idx}. {event.get('phase_transition', 'Unknown event')}\n"
            if event.get("agents_updated"):
                history_report += f"   Agents: {event.get('agents_updated')}\n"
            history_report += f"   Time: {event.get('timestamp', 'N/A')}\n\n"
        
        return history_report
    
    def _get_current_phase(self):
        """Get current phase only"""
        workflow_state = self._context.get("workflow_state", {"current_phase": "1_understanding"})
        return f"Current Phase: {workflow_state.get('current_phase')}"


if __name__ == "__main__":
    # Test cases
    print("Test 1: Update status")
    tool1 = WorkflowStateTool(
        action="update_status",
        phase="2_execution",
        agent_status={"creator_agent": "in_progress"}
    )
    print(tool1.run())
    
    print("\nTest 2: Get status")
    tool2 = WorkflowStateTool(action="get_status")
    print(tool2.run())
    
    print("\nTest 3: Get current phase")
    tool3 = WorkflowStateTool(action="get_current_phase")
    print(tool3.run())
