from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning

art_direction_agent = Agent(
    name="ArtDirectionAgent",
    description="Transforms structured briefs into Nano Banana-ready Athar prompts and controls.",
    instructions="./instructions/art_direction_agent.md",
    tools=[],
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.25,
        max_tokens=7000,
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)
