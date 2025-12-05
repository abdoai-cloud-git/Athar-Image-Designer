"""
Pydantic schemas that define the JSON contracts passed between agents.

These contracts are enforced at runtime by the StructuredSendMessage tool to make
sure every hand-off is strict JSON and contains the fields downstream agents need.
"""

from __future__ import annotations

import json
from typing import Dict, Tuple, Type

from pydantic import BaseModel, Field, Literal, model_validator


class ErrorInfo(BaseModel):
    """Standard error payload shared by all agents."""

    type: str = Field(..., description="Machine-readable error category")
    details: str = Field(..., description="Human-readable explanation")


class HandoffInfo(BaseModel):
    """Metadata that indicates where the payload should be routed next."""

    target_agent: str = Field(..., description="Intended recipient agent name")
    action: str = Field(..., description="Action keyword describing what to do next")
    notes: str | None = Field(None, description="Optional extra guidance")


class BriefContent(BaseModel):
    theme: str
    mood: str
    tone: str
    palette: str
    visual_elements: str
    keywords: str
    aspect_ratio: str
    style: str
    custom_instructions: str = ""
    original_input: str


class BriefEnvelope(BaseModel):
    agent: Literal["brief_agent"]
    status: Literal["ok", "error"]
    brief: BriefContent | None = None
    handoff: HandoffInfo | None = None
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def _check_payload(cls, values: "BriefEnvelope") -> "BriefEnvelope":
        if values.status == "ok" and not values.brief:
            raise ValueError("brief is required when status='ok'")
        if values.status == "error" and not values.error:
            raise ValueError("error block is required when status='error'")
        return values


class PromptPackage(BaseModel):
    prompt: str
    negative_prompt: str
    aspect_ratio: str
    style: str
    quality: str
    theme: str
    palette: str


class PromptEnvelope(BaseModel):
    agent: Literal["art_direction_agent"]
    status: Literal["ok", "error"]
    prompt_package: PromptPackage | None = None
    handoff: HandoffInfo | None = None
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def _check_payload(cls, values: "PromptEnvelope") -> "PromptEnvelope":
        if values.status == "ok" and not values.prompt_package:
            raise ValueError("prompt_package is required when status='ok'")
        if values.status == "error" and not values.error:
            raise ValueError("error block is required when status='error'")
        return values


class ImageResult(BaseModel):
    task_id: str | None = None
    image_url: str
    all_image_urls: list[str]
    seed: str
    prompt_used: str
    aspect_ratio: str
    style: str | None = None
    poll_duration_seconds: float | None = None
    attempts: int | None = None


class ImageEnvelope(BaseModel):
    agent: Literal["nb_image_agent"]
    status: Literal["ok", "error"]
    image_result: ImageResult | None = None
    handoff: HandoffInfo | None = None
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def _check_payload(cls, values: "ImageEnvelope") -> "ImageEnvelope":
        if values.status == "ok" and not values.image_result:
            raise ValueError("image_result is required when status='ok'")
        if values.status == "error" and not values.error:
            raise ValueError("error block is required when status='error'")
        return values


class ValidationDetail(BaseModel):
    approved: bool
    status: Literal["pass", "pass_with_warnings", "retry", "error"]
    passed_checks: list[str]
    failed_checks: list[str]
    warnings: list[str]
    issues: list[str]
    recommendation: str
    image_info: dict


class QAEnvelope(BaseModel):
    agent: Literal["qa_agent"]
    status: Literal["pass", "pass_with_warnings", "retry", "error"]
    validation: ValidationDetail | None = None
    handoff: HandoffInfo | None = None
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def _check_payload(cls, values: "QAEnvelope") -> "QAEnvelope":
        if values.status in {"pass", "pass_with_warnings", "retry"} and not values.validation:
            raise ValueError("validation payload required for QA decisions")
        if values.status == "error" and not values.error:
            raise ValueError("error block is required when status='error'")
        return values


class DeliveryPackage(BaseModel):
    theme: str
    prompt_used: str
    image_url: str
    gdrive_view_url: str
    gdrive_download_url: str
    seed: str
    aspect_ratio: str
    filename: str
    file_id: str
    validation_status: Literal["pass", "pass_with_warnings"]


class DeliveryEnvelope(BaseModel):
    agent: Literal["export_agent"]
    status: Literal["delivered", "error"]
    delivery: DeliveryPackage | None = None
    error: ErrorInfo | None = None

    @model_validator(mode="after")
    def _check_payload(cls, values: "DeliveryEnvelope") -> "DeliveryEnvelope":
        if values.status == "delivered" and not values.delivery:
            raise ValueError("delivery payload required when status='delivered'")
        if values.status == "error" and not values.error:
            raise ValueError("error block is required when status='error'")
        return values


# Mapping of (sender_agent, recipient_agent) pairs to the schema that must be satisfied.
HANDOFF_SCHEMAS: Dict[Tuple[str, str], Type[BaseModel]] = {
    ("brief_agent", "art_direction_agent"): BriefEnvelope,
    ("art_direction_agent", "nb_image_agent"): PromptEnvelope,
    ("nb_image_agent", "qa_agent"): ImageEnvelope,
    ("qa_agent", "export_agent"): QAEnvelope,
    ("qa_agent", "nb_image_agent"): QAEnvelope,
}


def validate_payload(sender: str, recipient: str, raw_payload: str) -> None:
    """
    Validate a JSON payload for a specific agent handoff.

    Args:
        sender: Name of the sending agent.
        recipient: Name of the receiving agent.
        raw_payload: Raw JSON text that should match the schema.

    Raises:
        ValueError: If the payload is not JSON or does not match the schema.
    """
    schema = HANDOFF_SCHEMAS.get((sender, recipient))
    if schema is None:
        # Some communications (e.g., QA back to user) are not validated.
        return

    try:
        parsed = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Payload is not valid JSON: {exc}") from exc

    schema.model_validate(parsed)
