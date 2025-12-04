"""Brief Agent configuration."""
from __future__ import annotations

from pathlib import Path

from agency_swarm import Agent
from agents import ModelSettings
from openai.types.shared import Reasoning

_BASE_DIR = Path(__file__).resolve().parents[1]
_PROMPTS = _BASE_DIR / "config" / "prompts"

brief_agent = Agent(
    name="brief_agent",
    description="Extracts Athar creative briefs (theme, mood, palette, keywords) from user input.",
    instructions=str(_PROMPTS / "brief_agent.md"),
    model="gpt-5.1",
    model_settings=ModelSettings(
        temperature=0.4,
        max_tokens=6000,
        reasoning=Reasoning(effort="medium", summary="auto"),
    ),
)

__all__ = ["brief_agent"]
