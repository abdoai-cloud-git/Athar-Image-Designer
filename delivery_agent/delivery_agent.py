from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


delivery_agent = Agent(
    name="delivery_agent",
    description="Packages and exports final deliverables with summaries, shareable URLs, and webhook notifications",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
