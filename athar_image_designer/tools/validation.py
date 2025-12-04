"""Image validation heuristics and QA tool."""

from __future__ import annotations

import io
import logging
from typing import Any, Dict, Optional

import numpy as np
import requests
from agency_swarm.tools import BaseTool
from PIL import Image, ImageFilter, ImageOps
from pydantic import Field

LOGGER = logging.getLogger(__name__)


def _parse_ratio(ratio: str) -> float:
    width, height = ratio.split(":")
    return float(width) / float(height)


def _aspect_ratio_ok(image: Image.Image, expected_ratio: str, tolerance: float = 0.02) -> bool:
    img_ratio = image.width / image.height
    target = _parse_ratio(expected_ratio)
    delta = abs(img_ratio - target) / target
    return delta <= tolerance


def _clarity_score(image: Image.Image) -> float:
    gray = ImageOps.grayscale(image)
    arr = np.array(gray, dtype=np.float32)
    gy, gx = np.gradient(arr)
    variance = (np.var(gx) + np.var(gy)) / (255.0 ** 2)
    return float(np.clip(variance * 10, 0, 1))


def _artifact_score(image: Image.Image) -> float:
    edges = ImageOps.grayscale(image).filter(ImageFilter.FIND_EDGES)
    arr = np.array(edges, dtype=np.float32) / 255.0
    # High average edge intensity implies potential noise/artifacts.
    return float(np.clip(arr.mean(), 0, 1))


def _arabic_legibility_score(image: Image.Image) -> float:
    """A heuristic based on localized contrast around thin strokes."""
    gray = ImageOps.grayscale(image.resize((512, 512)))
    arr = np.array(gray, dtype=np.float32) / 255.0
    # Contrast between 25th and 75th percentile as a proxy for stroke readability.
    p75 = float(np.percentile(arr, 75))
    p25 = float(np.percentile(arr, 25))
    contrast = max(p75 - p25, 0)
    return float(np.clip(contrast * 2.5, 0, 1))


def validate_image_bytes(
    image_bytes: bytes,
    expected_aspect_ratio: str,
    clarity_floor: float = 0.25,
    artifact_ceiling: float = 0.65,
    legibility_floor: float = 0.3,
) -> Dict[str, Any]:
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        aspect_ok = _aspect_ratio_ok(img, expected_aspect_ratio)
        clarity = _clarity_score(img)
        artifact = _artifact_score(img)
        legibility = _arabic_legibility_score(img)

    status = "approved"
    notes = []
    if not aspect_ok:
        status = "retry"
        notes.append("Aspect ratio drift detected")
    if clarity < clarity_floor:
        status = "retry"
        notes.append("Image lacks clarity / appears blurry")
    if artifact > artifact_ceiling:
        status = "retry"
        notes.append("Artifacts/noise exceed threshold")
    if legibility < legibility_floor:
        status = "retry"
        notes.append("Arabic legibility too weak; boost contrast")

    return {
        "status": status,
        "aspect_ratio_ok": aspect_ok,
        "clarity_score": round(clarity, 3),
        "artifact_score": round(artifact, 3),
        "arabic_legibility_score": round(legibility, 3),
        "notes": notes,
    }


class ValidateImageTool(BaseTool):
    """Downloads an image and runs Athar QA heuristics."""

    image_url: str = Field(..., description="URL of the image to validate")
    expected_aspect_ratio: str = Field("3:2", description="Aspect ratio to enforce (W:H)")
    clarity_floor: float = Field(0.25, description="Minimum clarity score")
    artifact_ceiling: float = Field(0.65, description="Maximum acceptable artifact score")
    legibility_floor: float = Field(0.3, description="Minimum acceptable Arabic legibility score")

    def run(self) -> Dict[str, Any]:
        response = requests.get(self.image_url, timeout=60)
        response.raise_for_status()
        metrics = validate_image_bytes(
            response.content,
            expected_aspect_ratio=self.expected_aspect_ratio,
            clarity_floor=self.clarity_floor,
            artifact_ceiling=self.artifact_ceiling,
            legibility_floor=self.legibility_floor,
        )
        metrics["image_url"] = self.image_url
        LOGGER.info("QA validation completed", extra={"status": metrics["status"], "clarity": metrics["clarity_score"]})
        return metrics


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Validate an image URL for Athar quality gates")
    parser.add_argument("image_url")
    parser.add_argument("--ratio", default="3:2")
    args = parser.parse_args()

    tool = ValidateImageTool(image_url=args.image_url, expected_aspect_ratio=args.ratio)
    print(json.dumps(tool.run(), indent=2))
