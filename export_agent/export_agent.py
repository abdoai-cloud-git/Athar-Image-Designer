from agents import ModelSettings
from openai.types.shared import Reasoning
from agency_swarm import Agent


export_agent = Agent(
    name="ExportAgent",
    description="Uploads validated images to Google Drive using Service Account authentication. Returns sharing URLs for view and download.",
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
