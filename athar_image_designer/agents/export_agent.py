"""Export Agent configuration."""
from __future__ import annotations

from pathlib import Path

from agency_swarm import Agent
from agents import ModelSettings
from openai.types.shared import Reasoning

from athar_image_designer.tools import GDriveUploadTool

_BASE_DIR = Path(__file__).resolve().parents[1]
_PROMPTS = _BASE_DIR / "config" / "prompts"

export_agent = Agent(
    name="export_agent",
    description="Uploads approved Athar renders to Google Drive and publishes shareable URLs.",
    instructions=str(_PROMPTS / "export_agent.md"),
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.25,
        max_tokens=3000,
        reasoning=Reasoning(effort="low", summary="auto"),
    ),
    tools=[GDriveUploadTool()],
)

__all__ = ["export_agent"]
