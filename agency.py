from dotenv import load_dotenv
from agency_swarm import Agency

from orchestrator_agent import orchestrator_agent
from intake_agent import intake_agent
from strategy_agent import strategy_agent
from creator_agent import creator_agent
from coding_agent import coding_agent
from technical_agent import technical_agent
from reviewer_agent import reviewer_agent
from delivery_agent import delivery_agent

import asyncio

load_dotenv()


def create_agency(load_threads_callback=None):
    """
    Create the Content Automation Studio agency.
    
    This is a 7-agent orchestrated system for end-to-end content creation:
    
    Workflow (4-Phase Agencii.ai Pattern):
    1. UNDERSTANDING: User → Orchestrator → Intake → Strategy
    2. EXECUTION: Strategy → Creator/Coding/Technical (parallel where possible)
    3. EVALUATION: All outputs → Reviewer → (revision loop if needed)
    4. DELIVERY: Approved content → Delivery → User
    
    Communication Pattern: Orchestrator-Workers with Sequential Pipeline
    """
    agency = Agency(
        orchestrator_agent,  # Entry point for all user requests
        communication_flows=[
            # Orchestrator as central hub (can communicate with all agents)
            (orchestrator_agent, intake_agent),
            (orchestrator_agent, strategy_agent),
            (orchestrator_agent, creator_agent),
            (orchestrator_agent, coding_agent),
            (orchestrator_agent, technical_agent),
            (orchestrator_agent, reviewer_agent),
            (orchestrator_agent, delivery_agent),
            
            # Phase 1: Understanding
            (intake_agent, strategy_agent),
            
            # Phase 2: Execution (coordinated by orchestrator)
            (strategy_agent, creator_agent),
            (strategy_agent, coding_agent),
            (strategy_agent, technical_agent),
            
            # Phase 3: Evaluation (quality loops)
            (creator_agent, reviewer_agent),
            (coding_agent, reviewer_agent),
            (technical_agent, reviewer_agent),
            (reviewer_agent, creator_agent),   # Revision loop
            (reviewer_agent, coding_agent),    # Revision loop
            (reviewer_agent, technical_agent), # Revision loop
            
            # Phase 4: Delivery
            (reviewer_agent, delivery_agent),
        ],
        name="ContentAutomationStudio",
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )

    return agency


if __name__ == "__main__":
    agency = create_agency()

    # Test with single message (uncomment to use)
    # async def main():
    #     response = await agency.get_response(
    #         "Create a professional 1500-word article about AI trends in 2025 for business executives"
    #     )
    #     print(response)
    # asyncio.run(main())

    # Run in terminal
    agency.terminal_demo()
