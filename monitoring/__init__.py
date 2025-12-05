"""
Minimal monitoring helpers for emitting structured events.

The helpers currently log events locally but provide a single location to plug in
Sentry, Datadog, or any other alerting pipeline in the future.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger("athar.monitoring")

SENTRY_DSN = os.getenv("SENTRY_DSN")


def emit_event(event_name: str, level: str = "info", **payload: Any) -> None:
    """
    Emit a structured monitoring event.

    Args:
        event_name: Identifier for the event.
        level: Logging level ("info", "warning", "error").
        payload: Arbitrary JSON-serializable metadata.
    """
    log_line = json.dumps({"event": event_name, **payload})

    if level == "error":
        logger.error(log_line)
    elif level == "warning":
        logger.warning(log_line)
    else:
        logger.info(log_line)

    # Placeholder for real alerting (Sentry, etc.)
    if SENTRY_DSN:
        # Integration hook - extend when alerting service is available.
        logger.debug("SENTRY_DSN detected; integrate alerting pipeline as needed.")
