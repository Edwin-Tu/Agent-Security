import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from event_logger.event_logger import EventLogger
from event_logger.event_schema import GuardEvent

_default_logger = EventLogger()


def log_api_event(
    route: str,
    model: str | None = None,
    prompt: str | None = None,
    session_id: str = "default",
    action: str = "allow",
    allowed: bool = True,
    risk_score: int = 0,
    attack_type: str | None = None,
    blocked_reason: str | None = None,
    provider_called: bool = False,
    leakage_detected: bool = False,
    matched_assets: list[dict] | None = None,
    error: str | None = None,
    logger: EventLogger | None = None,
) -> str:
    logger = logger or _default_logger
    matched_asset_ids = [a.get("asset_id", "") for a in (matched_assets or [])]
    input_summary = (prompt or "")[:200]

    event = GuardEvent(
        session_id=session_id,
        attack_type=attack_type or "unknown",
        risk_score=risk_score,
        blocked=not allowed,
        leakage_detected=leakage_detected,
        matched_asset_ids=matched_asset_ids,
        input_summary=input_summary,
        policy_action=action.upper(),
        policy_reason=blocked_reason or "",
        metadata={
            "route": route,
            "model": model or "",
            "provider_called": provider_called,
            "error": error or "",
        },
    )

    try:
        logger.log_event(event)
    except Exception:
        traceback.print_exc()

    return event.event_id or ""
