import re
from . import severity as sev


PLACEHOLDER_MAP = {
    "api_key": "[REDACTED_API_KEY]",
    "token": "[REDACTED_TOKEN]",
    "password": "[REDACTED_SECRET]",
    "private_key": "[REDACTED_PRIVATE_KEY]",
    "flag": "[REDACTED_FLAG]",
    "jwt": "[REDACTED_TOKEN]",
    "custom": "[REDACTED_SECRET]",
}

DEFAULT_PLACEHOLDER = "[REDACTED_SECRET]"
PARTIAL_PLACEHOLDER = "[REDACTED_PARTIAL]"


def _is_nested(text: str) -> bool:
    placeholders = [
        "[REDACTED_SECRET]",
        "[REDACTED_API_KEY]",
        "[REDACTED_PRIVATE_KEY]",
        "[REDACTED_FLAG]",
        "[REDACTED_TOKEN]",
        "[REDACTED_PARTIAL]",
    ]
    for ph in placeholders:
        if ph in text:
            return True
    return False


class Redactor:
    def redact_patterns(self, text: str, findings: list[dict]) -> str:
        result = text
        replacements = []
        for f in sorted(findings, key=lambda x: x["start"], reverse=True):
            matched = f["matched_text"]
            placeholder = f.get("placeholder", DEFAULT_PLACEHOLDER)
            action = f.get("action", sev.REDACT)
            start = f["start"]
            end = f["end"]

            if action == sev.BLOCK:
                placeholder = f.get("placeholder", DEFAULT_PLACEHOLDER)

            if _is_nested(result[start:end]):
                continue

            result = result[:start] + placeholder + result[end:]
        return result

    def redact_asset(self, text: str, value: str, placeholder: str = DEFAULT_PLACEHOLDER) -> str:
        if not value:
            return text
        idx = text.lower().find(value.lower())
        if idx == -1:
            return text
        end = idx + len(value)
        if _is_nested(text[idx:end]):
            return text
        return text[:idx] + placeholder + text[end:]

    def redact_asset_partial(self, text: str, value: str, min_length: int = 4) -> str:
        if not value or len(value) < min_length:
            return text
        result = text
        for i in range(len(value) - min_length + 1):
            fragment = value[i:i + min_length]
            idx = result.lower().find(fragment.lower())
            while idx != -1:
                end = idx + len(fragment)
                if _is_nested(result[idx:end]):
                    idx = result.lower().find(fragment.lower(), idx + 1)
                    continue
                result = result[:idx] + PARTIAL_PLACEHOLDER + result[end:]
                idx = result.lower().find(fragment.lower(), idx + len(PARTIAL_PLACEHOLDER) - len(fragment) + 1)
        return result
