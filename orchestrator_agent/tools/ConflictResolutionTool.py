from agency_swarm.tools import BaseTool
from pydantic import Field
import json


class ConflictResolutionTool(BaseTool):
    """
    Handles conflicts and errors that arise during workflow execution.
    Use this tool to analyze issues, determine solutions, and log resolutions.
    """
    
    action: str = Field(
        ...,
        description="Action to perform. Options: detect_conflicts, analyze_error, log_resolution, get_conflicts"
    )
    
    error_details: dict = Field(
        default_factory=dict,
        description="Details about the error or conflict. Should include 'agent', 'error_type', 'message'"
    )
    
    resolution: str = Field(
        default="",
        description="Description of the resolution applied (for log_resolution action)"
    )
    
    def run(self):
        """
        Manages conflict resolution and error handling in the workflow.
        """
        if self.action == "detect_conflicts":
            return self._detect_conflicts()
        
        elif self.action == "analyze_error":
            return self._analyze_error()
        
        elif self.action == "log_resolution":
            return self._log_resolution()
        
        elif self.action == "get_conflicts":
            return self._get_conflicts()
        
        else:
            return f"Error: Invalid action '{self.action}'. Options: detect_conflicts, analyze_error, log_resolution, get_conflicts"
    
    def _detect_conflicts(self):
        """Detect potential conflicts in current workflow state"""
        # Step 1: Load workflow state
        workflow_state = self._context.get("workflow_state", {})
        agents = workflow_state.get("agents", {})
        delegations = self._context.get("delegations", [])
        
        conflicts = []
        
        # Step 2: Check for failed agents
        failed_agents = [agent for agent, status in agents.items() if status == "failed"]
        if failed_agents:
            conflicts.append({
                "type": "agent_failure",
                "agents": failed_agents,
                "severity": "high"
            })
        
        # Step 3: Check for stalled delegations
        active_delegations = [d for d in delegations if d.get("status") == "delegated"]
        if len(active_delegations) > 3:
            conflicts.append({
                "type": "too_many_active_tasks",
                "count": len(active_delegations),
                "severity": "medium"
            })
        
        # Step 4: Check for missing critical context
        brief = self._context.get("brief")
        execution_plan = self._context.get("execution_plan")
        
        current_phase = workflow_state.get("current_phase", "")
        
        if current_phase == "2_execution" and not execution_plan:
            conflicts.append({
                "type": "missing_critical_context",
                "missing": "execution_plan",
                "severity": "high"
            })
        
        # Step 5: Return results
        if conflicts:
            result = "⚠ Conflicts Detected:\n\n"
            for idx, conflict in enumerate(conflicts, 1):
                result += f"{idx}. Type: {conflict['type']}\n"
                result += f"   Severity: {conflict['severity']}\n"
                result += f"   Details: {conflict}\n\n"
            return result
        else:
            return "✓ No conflicts detected - workflow is healthy"
    
    def _analyze_error(self):
        """Analyze an error and suggest resolution"""
        if not self.error_details:
            return "Error: error_details parameter required for analyze_error action"
        
        agent = self.error_details.get("agent", "unknown")
        error_type = self.error_details.get("error_type", "unknown")
        message = self.error_details.get("message", "")
        
        # Step 1: Categorize error
        analysis = {
            "agent": agent,
            "error_type": error_type,
            "severity": "unknown",
            "suggested_action": ""
        }
        
        # Step 2: Determine severity and action based on error type
        if error_type == "missing_context":
            analysis["severity"] = "high"
            analysis["suggested_action"] = "Ensure required context is set before delegating to agent. Re-run previous phase if needed."
        
        elif error_type == "tool_failure":
            analysis["severity"] = "medium"
            analysis["suggested_action"] = "Check tool parameters and retry. If persists, use alternative tool or escalate to user."
        
        elif error_type == "validation_failure":
            analysis["severity"] = "medium"
            analysis["suggested_action"] = "Review validation criteria and agent output. May need to adjust parameters or requirements."
        
        elif error_type == "timeout":
            analysis["severity"] = "low"
            analysis["suggested_action"] = "Retry the operation. If persists, increase timeout or split into smaller tasks."
        
        else:
            analysis["severity"] = "medium"
            analysis["suggested_action"] = "Review error message and agent logs. May require manual intervention."
        
        # Step 3: Log error for tracking
        errors = self._context.get("errors", [])
        errors.append({
            "agent": agent,
            "error_type": error_type,
            "message": message,
            "analysis": analysis,
            "timestamp": "now"
        })
        self._context.set("errors", errors)
        
        # Step 4: Return analysis
        result = f"""
=== Error Analysis ===

Agent: {agent}
Error Type: {error_type}
Severity: {analysis['severity']}

Message: {message}

Suggested Action:
{analysis['suggested_action']}

This error has been logged for tracking.
"""
        return result
    
    def _log_resolution(self):
        """Log a conflict resolution"""
        if not self.resolution:
            return "Error: resolution parameter required for log_resolution action"
        
        resolutions = self._context.get("resolutions", [])
        resolutions.append({
            "resolution": self.resolution,
            "error_details": self.error_details,
            "timestamp": "now"
        })
        self._context.set("resolutions", resolutions)
        
        return f"✓ Resolution logged: {self.resolution}"
    
    def _get_conflicts(self):
        """Get list of all logged conflicts and errors"""
        errors = self._context.get("errors", [])
        resolutions = self._context.get("resolutions", [])
        
        report = "=== Conflict and Error Log ===\n\n"
        
        if errors:
            report += f"Total Errors Logged: {len(errors)}\n\n"
            for idx, error in enumerate(errors[-5:], 1):  # Show last 5
                report += f"{idx}. [{error.get('error_type')}] {error.get('agent')}\n"
                report += f"   {error.get('message', 'No message')}\n\n"
        else:
            report += "No errors logged\n\n"
        
        if resolutions:
            report += f"Total Resolutions Applied: {len(resolutions)}\n\n"
            for idx, resolution in enumerate(resolutions[-3:], 1):  # Show last 3
                report += f"{idx}. {resolution.get('resolution')}\n\n"
        else:
            report += "No resolutions logged\n"
        
        return report


if __name__ == "__main__":
    # Test cases
    print("Test 1: Detect conflicts")
    tool1 = ConflictResolutionTool(action="detect_conflicts")
    print(tool1.run())
    
    print("\nTest 2: Analyze error")
    tool2 = ConflictResolutionTool(
        action="analyze_error",
        error_details={
            "agent": "creator_agent",
            "error_type": "missing_context",
            "message": "Brief not found in agency context"
        }
    )
    print(tool2.run())
    
    print("\nTest 3: Log resolution")
    tool3 = ConflictResolutionTool(
        action="log_resolution",
        resolution="Added missing brief to context and re-delegated task to creator_agent",
        error_details={"agent": "creator_agent"}
    )
    print(tool3.run())
