"""Pydantic schemas shared across agents for runtime validation."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

ASPECT_RATIOS = {
    "1:1",
    "4:5",
    "5:4",
    "3:4",
    "4:3",
    "9:16",
    "16:9",
    "21:9",
    "9:21",
}


def normalize_aspect_ratio(value: Optional[str], default: str = "4:5") -> str:
    """Normalize aspect ratio to a supported value."""
    if not value:
        return default
    clean = value.strip()
    if clean in ASPECT_RATIOS:
        return clean
    # Some agents pass ratio like "4x5" – convert common typos
    cleaned_alt = clean.replace("x", ":")
    return cleaned_alt if cleaned_alt in ASPECT_RATIOS else default


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Compatibility helper for pydantic v1/v2."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()  # type: ignore[no-any-return]


class CreativeBriefSchema(BaseModel):
    theme: str = Field(default="introspective self-reflection")
    mood: str = Field(default="serene, contemplative")
    tone: str = Field(default="poetic, cinematic, meditative")
    palette: str = Field(default="warm earth tones, soft golden light")
    visual_elements: str = Field(default="")
    keywords: str = Field(default="")
    aspect_ratio: str = Field(default="4:5")
    style: str = Field(default="cinematic-premium")
    original_input: str = Field(..., description="Original user text that produced the brief")

    def normalized(self) -> Dict[str, Any]:
        data = model_to_dict(self)
        data["aspect_ratio"] = normalize_aspect_ratio(data.get("aspect_ratio"))
        data["style"] = data.get("style") or "cinematic-premium"
        return data


class PromptPayloadSchema(BaseModel):
    prompt: str = Field(..., min_length=10)
    negative_prompt: str = Field(default="messy textures, chaotic shapes, distorted Arabic text, low quality, blurry")
    aspect_ratio: str = Field(default="4:5")
    style: str = Field(default="cinematic-premium")
    quality: str = Field(default="premium")
    theme: str = Field(default="")
    palette: str = Field(default="")
    num_images: int = Field(default=1, ge=1, le=4)

    def normalized(self) -> Dict[str, Any]:
        data = model_to_dict(self)
        data["aspect_ratio"] = normalize_aspect_ratio(data.get("aspect_ratio"))
        data["style"] = data.get("style") or "cinematic-premium"
        data["quality"] = data.get("quality") or "premium"
        return data


class ImageGenerationResultSchema(BaseModel):
    success: bool = Field(default=True)
    image_url: str = Field(default="")
    seed: str = Field(default="N/A")
    prompt_used: str = Field(default="")
    aspect_ratio: str = Field(default="4:5")
    num_images: int = Field(default=1)
    all_image_urls: List[str] = Field(default_factory=list)
    error: Optional[str] = Field(default=None)
    retryable: bool = Field(default=False)

    def normalized(self) -> Dict[str, Any]:
        data = model_to_dict(self)
        data["aspect_ratio"] = normalize_aspect_ratio(data.get("aspect_ratio"))
        data["all_image_urls"] = [url for url in data.get("all_image_urls", []) if url]
        if data.get("success") and not data.get("image_url") and data["all_image_urls"]:
            data["image_url"] = data["all_image_urls"][0]
        return data
