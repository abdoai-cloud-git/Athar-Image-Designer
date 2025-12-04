from agents import ModelSettings
from openai.types.shared import Reasoning
from agency_swarm import Agent


brief_agent = Agent(
    name="BriefAgent",
    description="Extracts theme, tone, palette, and keywords from user input or Athar text excerpts. Outputs structured JSON for art direction.",
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
