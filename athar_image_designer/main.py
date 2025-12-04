"""Utility script for running the Athar Image Designer workflow locally."""
from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from agency import create_agency

logging.basicConfig(level=logging.INFO)


async def _run(prompt: str) -> None:
    agency = create_agency()
    response = await agency.get_response(prompt)
    print(response)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Athar Athar Image Designer workflow once")
    parser.add_argument("prompt", help="User brief or Athar excerpt")
    args = parser.parse_args()
    asyncio.run(_run(args.prompt))


if __name__ == "__main__":
    main()
