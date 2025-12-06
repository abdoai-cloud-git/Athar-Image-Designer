from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning


creator_agent = Agent(
    name="creator_agent",
    description="Executes creative content generation including copy, scripts, articles, posts, hooks, and headlines following brand voice",
    instructions="./instructions.md",
    files_folder="./files",
    tools_folder="./tools",
    model="gpt-5.1",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)
