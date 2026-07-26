"""Data masking helpers."""

from __future__ import annotations

import re

from elder_privacy_guard.models import HealthMatch, PIIMatch


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def mask_phone(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) < 10:
        return "****"
    if digits.startswith("886") and len(digits) >= 12:
        return f"{digits[:3]}****{digits[-2:]}"
    return f"{digits[:4]}****{digits[-2:]}"


def mask_id(value: str) -> str:
    if len(value) < 10:
        return "****"
    return f"{value[:2]}****{value[-3:]}"


def mask_email(value: str) -> str:
    if not _EMAIL_PATTERN.match(value):
        return "***@***"
    local_part, domain = value.split("@", 1)
    return f"{local_part[:1]}***@{domain}"


def mask_text(text: str, pii_matches: list[PIIMatch], health_matches: list[HealthMatch]) -> str:
    if not text:
        return ""
    if not pii_matches and not health_matches:
        return text

    sanitized = text
    for match in sorted((*pii_matches, *health_matches), key=lambda item: (item.start, item.end), reverse=True):
        sanitized = f"{sanitized[:match.start]}{match.masked}{sanitized[match.end:]}"
    return sanitized
