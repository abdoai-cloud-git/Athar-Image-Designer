from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning

from athar_image_designer.tools.validation import ValidateImageTool

qa_agent = Agent(
    name="QAAuditAgent",
    description="Validates renders for aspect ratio accuracy, clarity, and Arabic legibility before release.",
    instructions="./instructions/qa_agent.md",
    tools=[ValidateImageTool],
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.15,
        max_tokens=4000,
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)
