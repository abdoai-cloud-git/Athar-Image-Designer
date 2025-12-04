from agency_swarm import Agent, ModelSettings
from openai.types.shared import Reasoning

from athar_image_designer.tools.gdrive_upload import GoogleDriveUploadTool

export_agent = Agent(
    name="ExportAgent",
    description="Delivers approved renders by uploading to Google Drive and emitting the final response JSON.",
    instructions="./instructions/export_agent.md",
    tools=[GoogleDriveUploadTool],
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.2,
        max_tokens=4000,
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)
