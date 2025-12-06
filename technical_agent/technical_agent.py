from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


technical_agent = Agent(
    name="technical_agent",
    description="Applies templates and formatting to content for various platforms including PDF, slides, and documents with brand styling",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
