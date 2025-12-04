"""Utility entry point for running the Athar Image Designer workflow locally."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Any

from agency import create_agency

LOGGER = logging.getLogger(__name__)


async def run_generate_athar_image(user_prompt: str) -> Any:
    agency = create_agency()
    LOGGER.info("Dispatching workflow prompt")
    response = await agency.get_response(
        f"Run the generate_athar_image workflow for: {user_prompt}. Return only the final JSON payload."
    )
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Athar Image Designer workflow")
    parser.add_argument("prompt", help="User brief or Athar excerpt", nargs="?")
    args = parser.parse_args()
    prompt = args.prompt or input("Enter Athar request: ")

    result = asyncio.run(run_generate_athar_image(prompt))
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
