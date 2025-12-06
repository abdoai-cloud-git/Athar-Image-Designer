from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


orchestrator_agent = Agent(
    name="orchestrator_agent",
    description="Central manager that orchestrates the entire content automation workflow, delegates tasks, tracks progress, and ensures quality",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
