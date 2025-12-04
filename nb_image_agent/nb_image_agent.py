from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


nb_image_agent = Agent(
    name="nb_image_agent",
    description="Generates images using Nano Banana Pro through KIE API integration",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="low", summary="auto"),
    ),
)
