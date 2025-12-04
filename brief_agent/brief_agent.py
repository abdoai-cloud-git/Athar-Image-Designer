from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


brief_agent = Agent(
    name="brief_agent",
    description="Extracts theme, tone, palette, and keywords from user input or Athar text excerpts",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
