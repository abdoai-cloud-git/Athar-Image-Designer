from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


coding_agent = Agent(
    name="coding_agent",
    description="Handles technical automation tasks including building schemas, scripts, API integrations, and data transformations",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
