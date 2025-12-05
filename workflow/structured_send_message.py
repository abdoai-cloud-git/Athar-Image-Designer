"""
Custom SendMessage tool that enforces JSON contracts between agents.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from agency_swarm.tools.send_message import SendMessage

from .contracts import validate_payload

logger = logging.getLogger(__name__)


class StructuredSendMessage(SendMessage):
    """
    Subclass of the default SendMessage tool that validates the message payload
    before forwarding it to the recipient agent.
    """

    async def on_invoke_tool(self, wrapper, arguments_json_string: str) -> str:  # type: ignore[override]
        sender = getattr(self.sender_agent, "name", "").lower()

        try:
            args: dict[str, Any] = json.loads(arguments_json_string)
        except json.JSONDecodeError as exc:
            logger.error("SendMessage invoked with non-JSON arguments | error=%s", exc)
            return json.dumps(
                {
                    "error": "invalid_send_message_arguments",
                    "details": f"Arguments must be JSON: {exc}",
                }
            )

        recipient = str(args.get("recipient_agent", "")).lower()
        message_content = args.get("message", "")

        if sender and recipient and message_content:
            try:
                validate_payload(sender, recipient, message_content)
            except ValueError as exc:
                logger.error(
                    "JSON handoff validation failed | sender=%s | recipient=%s | error=%s",
                    sender,
                    recipient,
                    exc,
                )
                return json.dumps(
                    {
                        "error": "schema_validation_failed",
                        "agent": sender,
                        "target_agent": recipient,
                        "details": str(exc),
                    }
                )

        return await super().on_invoke_tool(wrapper, arguments_json_string)
