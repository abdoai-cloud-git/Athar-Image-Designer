"""QA Agent configuration."""
from __future__ import annotations

from pathlib import Path

from agency_swarm import Agent
from agents import ModelSettings
from openai.types.shared import Reasoning

from athar_image_designer.tools import ValidationTool

_BASE_DIR = Path(__file__).resolve().parents[1]
_PROMPTS = _BASE_DIR / "config" / "prompts"

qa_agent = Agent(
    name="qa_agent",
    description="Validates aspect ratio, clarity, and Arabic legibility before delivery.",
    instructions=str(_PROMPTS / "qa_agent.md"),
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.2,
        max_tokens=3000,
        reasoning=Reasoning(effort="low", summary="auto"),
    ),
    tools=[ValidationTool()],
)

__all__ = ["qa_agent"]
