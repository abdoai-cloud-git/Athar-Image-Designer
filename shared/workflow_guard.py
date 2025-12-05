"""Fail-fast workflow guard utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Type

from pydantic import BaseModel, ValidationError

from .schemas import model_to_dict


@dataclass
class WorkflowValidationError(Exception):
    agent: str
    code: str
    details: Any
    raw_output: str | None = None

    def to_response(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "agent": self.agent,
            "details": self.details,
            "raw_output_preview": (self.raw_output[:500] if self.raw_output else None),
        }


def guard_agent_output(agent_name: str, raw_output: str, schema: Type[BaseModel]) -> Dict[str, Any]:
    """Ensure tool output is valid JSON and matches the provided schema."""
    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as exc:  # pragma: no cover - logging path
        raise WorkflowValidationError(
            agent=agent_name,
            code="non_json_output",
            details={"message": str(exc)},
            raw_output=raw_output,
        ) from exc

    try:
        model = schema(**parsed)
        data = model.normalized() if hasattr(model, "normalized") else model_to_dict(model)
        return data
    except ValidationError as exc:  # pragma: no cover - logging path
        raise WorkflowValidationError(
            agent=agent_name,
            code="schema_validation_failed",
            details=exc.errors(),
            raw_output=raw_output,
        ) from exc


def fail_fast_payload(error: WorkflowValidationError) -> str:
    """Return a JSON payload that can be surfaced to clients."""
    return json.dumps(error.to_response(), indent=2)
