"""Validation helpers for Athar QA checks."""
from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import requests
from agency_swarm.tools import BaseTool
from PIL import Image
from pydantic import Field

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class AspectRatioResult:
    matches: bool
    expected_ratio: float
    actual_ratio: float
    tolerance: float


def _parse_aspect_ratio(ratio: str) -> float:
    if ":" in ratio:
        width, height = ratio.split(":", 1)
        return float(width) / float(height)
    return float(ratio)


def aspect_ratio_within_tolerance(image: Image.Image, expected_ratio: str, tolerance: float = 0.02) -> AspectRatioResult:
    width, height = image.size
    actual_ratio = width / height
    target_ratio = _parse_aspect_ratio(expected_ratio)
    matches = abs(actual_ratio - target_ratio) <= (target_ratio * tolerance)
    return AspectRatioResult(matches, target_ratio, actual_ratio, tolerance)


def _compute_laplacian_variance(gray_array: np.ndarray) -> float:
    laplacian = (
        -4 * gray_array
        + np.roll(gray_array, 1, axis=0)
        + np.roll(gray_array, -1, axis=0)
        + np.roll(gray_array, 1, axis=1)
        + np.roll(gray_array, -1, axis=1)
    )
    return float(np.var(laplacian))


def artifact_score(image: Image.Image) -> float:
    gray = image.convert("L")
    arr = np.array(gray, dtype=np.float32)
    variance = _compute_laplacian_variance(arr)
    normalized = variance / (arr.mean() + 1e-9)
    return normalized


def detect_artifacts(image: Image.Image, min_threshold: float = 10.0, max_threshold: float = 250.0) -> Tuple[bool, float]:
    score = artifact_score(image)
    has_artifacts = score < min_threshold or score > max_threshold
    return has_artifacts, score


def arabic_legibility_heuristic(image: Image.Image) -> Dict[str, float | bool]:
    width, height = image.size
    central_band = image.crop((width * 0.1, height * 0.25, width * 0.9, height * 0.75)).convert("L")
    arr = np.array(central_band, dtype=np.float32) / 255.0
    if arr.size == 0:
        return {"score": 0.0, "legible": False}
    horizontal_grad = np.abs(np.diff(arr, axis=1))
    vertical_grad = np.abs(np.diff(arr, axis=0))
    curvature_grad = np.abs(arr[1:, 1:] - arr[:-1, :-1])
    contrast = float(arr.std())
    horizontal_density = float((horizontal_grad > 0.15).mean())
    vertical_density = float((vertical_grad > 0.15).mean())
    curvature_density = float((curvature_grad > 0.12).mean())
    score = 0.4 * contrast + 0.35 * horizontal_density + 0.25 * curvature_density
    return {"score": score, "legible": score >= 0.2}


def _fetch_image(image_url: str) -> Image.Image:
    response = requests.get(image_url, timeout=60)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGB")


class ValidationTool(BaseTool):
    """Agency Swarm tool that evaluates Athar renders for fidelity."""

    image_url: Optional[str] = Field(None, description="URL of the rendered Athar image")
    expected_aspect_ratio: str = Field("3:4", description="Expected aspect ratio string (e.g., '3:4')")
    aspect_ratio_tolerance: float = Field(0.02, gt=0, le=0.1, description="Allowed deviation as a percentage")
    clarity_range: Tuple[float, float] = Field((10.0, 250.0), description="Min/max acceptable artifact score")

    def run(self) -> Dict[str, object]:
        if not self.image_url:
            raise ValueError("ValidationTool requires image_url")
        image = _fetch_image(self.image_url)
        ratio_result = aspect_ratio_within_tolerance(image, self.expected_aspect_ratio, self.aspect_ratio_tolerance)
        has_artifacts, score = detect_artifacts(
            image, min_threshold=self.clarity_range[0], max_threshold=self.clarity_range[1]
        )
        legibility = arabic_legibility_heuristic(image)
        passed = ratio_result.matches and not has_artifacts and bool(legibility["legible"])
        return {
            "aspect_ratio_ok": ratio_result.matches,
            "aspect_ratio_actual": round(ratio_result.actual_ratio, 4),
            "aspect_ratio_expected": round(ratio_result.expected_ratio, 4),
            "artifact_score": round(score, 2),
            "artifacts_detected": has_artifacts,
            "arabic_legibility_score": round(float(legibility["score"]), 3),
            "arabic_legible": bool(legibility["legible"]),
            "status": "pass" if passed else "fail",
        }


__all__ = [
    "ValidationTool",
    "aspect_ratio_within_tolerance",
    "detect_artifacts",
    "arabic_legibility_heuristic",
]


if __name__ == "__main__":
    print("Use ValidationTool within the QA agent; a standalone smoke test is not available without an image URL.")
