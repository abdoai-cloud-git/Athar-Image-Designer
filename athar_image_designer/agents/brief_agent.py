from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning

brief_agent = Agent(
    name="BriefAgent",
    description="Extracts Athar-ready briefs (theme, tone, palette, keywords, Arabic text) from any user input.",
    instructions="./instructions/brief_agent.md",
    tools=[],
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.2,
        max_tokens=6000,
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)
