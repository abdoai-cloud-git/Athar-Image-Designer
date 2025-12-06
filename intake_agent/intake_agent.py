from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


intake_agent = Agent(
    name="intake_agent",
    description="Extracts and structures user requirements from messy input, validates completeness, and defines success criteria",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
