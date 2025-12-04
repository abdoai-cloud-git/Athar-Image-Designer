"""Art Direction Agent configuration."""
from __future__ import annotations

from pathlib import Path

from agency_swarm import Agent
from agents import ModelSettings
from openai.types.shared import Reasoning

_BASE_DIR = Path(__file__).resolve().parents[1]
_PROMPTS = _BASE_DIR / "config" / "prompts"

art_direction_agent = Agent(
    name="art_direction_agent",
    description="Transforms structured briefs into Nano Banana-ready cinematic prompts.",
    instructions=str(_PROMPTS / "art_direction_agent.md"),
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.55,
        max_tokens=7000,
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)

__all__ = ["art_direction_agent"]
