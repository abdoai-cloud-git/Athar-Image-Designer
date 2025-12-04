from agents import ModelSettings
from openai.types.shared import Reasoning
from agency_swarm import Agent


qa_agent = Agent(
    name="QaAgent",
    description="Validates generated images for quality, aspect ratio correctness, clarity, and Arabic text legibility. Returns retry status with correction notes if validation fails.",
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
