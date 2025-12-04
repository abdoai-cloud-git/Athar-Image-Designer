from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


art_direction_agent = Agent(
    name="art_direction_agent",
    description="Converts creative brief into complete Nano Banana prompt with style parameters",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
