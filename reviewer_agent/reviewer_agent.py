from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


reviewer_agent = Agent(
    name="reviewer_agent",
    description="Enforces quality standards by detecting errors, validating brand compliance, and suggesting improvements",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
