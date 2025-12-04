from agents import ModelSettings
from openai.types.shared import Reasoning
from agency_swarm import Agent


art_direction_agent = Agent(
    name="ArtDirectionAgent",
    description="Converts creative briefs into complete Nano Banana prompts with style parameters, aspect ratios, and negative prompts.",
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
