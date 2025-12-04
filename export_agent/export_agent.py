from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


export_agent = Agent(
    name="export_agent",
    description="Uploads final images to Google Drive and returns shareable URLs",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
