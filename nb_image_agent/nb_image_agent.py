from agents import ModelSettings
from openai.types.shared import Reasoning
from agency_swarm import Agent


nb_image_agent = Agent(
    name="NbImageAgent",
    description="Generates images using Nano Banana Pro via KIE API. Handles task submission, polling, and result extraction.",
    instructions="./instructions.md",
    tools_folder="./tools",
    files_folder="./files",
    model="gpt-5.1",
    model_settings=ModelSettings(
        max_tokens=25000,
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)
