from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


strategy_agent = Agent(
    name="strategy_agent",
    description="Plans execution workflow by converting briefs into step-by-step operational plans with risk analysis and quality standards",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
