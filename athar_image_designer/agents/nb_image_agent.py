from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning

from athar_image_designer.tools.kie_nano_banana import NanoBananaTaskTool

nb_image_agent = Agent(
    name="NanoBananaAgent",
    description="Submits prompts to Nano Banana Pro exclusively through the KIE playground endpoints and tracks completion.",
    instructions="./instructions/nb_image_agent.md",
    tools=[NanoBananaTaskTool],
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.1,
        max_tokens=3500,
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)
