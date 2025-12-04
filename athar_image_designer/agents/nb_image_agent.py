"""Nano Banana Image Agent configuration."""
from __future__ import annotations

from pathlib import Path

from agency_swarm import Agent
from agents import ModelSettings
from openai.types.shared import Reasoning

from athar_image_designer.tools import KieNanoBananaTool

_BASE_DIR = Path(__file__).resolve().parents[1]
_PROMPTS = _BASE_DIR / "config" / "prompts"

nb_image_agent = Agent(
    name="nb_image_agent",
    description="Submits Nano Banana Pro renders via the KIE Playground API and returns image metadata.",
    instructions=str(_PROMPTS / "nb_image_agent.md"),
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.2,
        max_tokens=4000,
        reasoning=Reasoning(effort="low", summary="auto"),
    ),
    tools=[KieNanoBananaTool()],
)

__all__ = ["nb_image_agent"]
