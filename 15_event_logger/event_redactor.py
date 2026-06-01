import re
from typing import Any


FLAG_PATTERN = r"[A-Za-z0-9]+CTF\{[^}]+\}"
API_KEY_PATTERN = r"sk-[A-Za-z0-9_-]{20,}"
PRIVATE_KEY_PATTERN = r"-----BEGIN\s+(RSA\s+|EC\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(RSA\s+|EC\s+)?PRIVATE\s+KEY-----"
PASSWORD_PATTERN = r"(?i)(password\s*[=:]\s*[A-Za-z0-9!@#$%^&*()_+]{4,})"
ASSIGNMENT_PATTERN = r"(?i)(api_key|apikey|api-key|secret_key|secretkey|token|access_token)\s*[=:]\s*\S{4,}"

FIELD_REDACTIONS = {
    "secret": "[REDACTED_SECRET]",
    "password": "[REDACTED_PASSWORD]",
    "api_key": "[REDACTED_API_KEY]",
    "private_key": "[REDACTED_PRIVATE_KEY]",
}

FIELD_PATTERN_MAP = {
    "secret": "[REDACTED_SECRET]",
    "password": "[REDACTED_PASSWORD]",
    "api_key": "[REDACTED_API_KEY]",
    "private_key": "[REDACTED_PRIVATE_KEY]",
    "leakage_evidence": "[REDACTED_PARTIAL]",
}

TEXT_PATTERNS = [
    (re.compile(FLAG_PATTERN, re.DOTALL), "[REDACTED_SECRET]"),
    (re.compile(API_KEY_PATTERN), "[REDACTED_API_KEY]"),
    (re.compile(PRIVATE_KEY_PATTERN, re.DOTALL), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(PASSWORD_PATTERN), "[REDACTED_PASSWORD]"),
]

PLACEHOLDERS = [
    "[REDACTED_SECRET]",
    "[REDACTED_API_KEY]",
    "[REDACTED_PRIVATE_KEY]",
    "[REDACTED_PASSWORD]",
    "[REDACTED_PARTIAL]",
]


class EventRedactor:
    def redact_text(self, text: str) -> str:
        result = text
        for pattern, replacement in TEXT_PATTERNS:
            result = pattern.sub(replacement, result)
        return result

    def _redact_value(self, value: Any, field_name: str | None = None) -> Any:
        if isinstance(value, dict):
            return self.redact_event(value)
        if isinstance(value, list):
            return [self._redact_value(v, field_name) for v in value]
        if isinstance(value, str):
            if field_name in FIELD_PATTERN_MAP:
                return FIELD_PATTERN_MAP[field_name]
            return self.redact_text(value)
        return value

    def redact_event(self, event: dict) -> dict:
        result = {}
        for key, value in event.items():
            if isinstance(value, str) and key in FIELD_REDACTIONS:
                result[key] = FIELD_REDACTIONS[key]
            elif isinstance(value, str) and key in FIELD_PATTERN_MAP:
                result[key] = FIELD_PATTERN_MAP[key]
            elif isinstance(value, str):
                redacted = self.redact_text(value)
                if redacted != value:
                    result[key] = redacted
                else:
                    result[key] = value
            elif isinstance(value, dict):
                result[key] = self.redact_event(value)
            elif isinstance(value, list):
                result[key] = [self._redact_value(v, key) for v in value]
            else:
                result[key] = value
        return result
