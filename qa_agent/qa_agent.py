from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


qa_agent = Agent(
    name="qa_agent",
    description="Validates generated images for quality, aspect ratio, and Arabic legibility",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="low", summary="auto"),
    ),
)
