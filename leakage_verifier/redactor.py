LEAK_PLACEHOLDER_MAP = {
    "full_leak": "[REDACTED_SECRET]",
    "partial_leak": "[REDACTED_PARTIAL]",
    "encoding_leak": "[REDACTED_ENCODED_SECRET]",
    "reconstruction_leak": "[REDACTED_RECONSTRUCTION]",
    "translation_leak": "[REDACTED_TRANSLATION]",
    "semantic_leak": "[REDACTED_SEMANTIC]",
}

ALL_PLACEHOLDERS = set(LEAK_PLACEHOLDER_MAP.values())


class Redactor:
    def redact(self, text: str, match_text: str, leak_type: str) -> str:
        if not match_text or match_text not in text:
            return text
        placeholder = LEAK_PLACEHOLDER_MAP.get(leak_type, "[REDACTED_SECRET]")
        if placeholder in text:
            return text
        return text.replace(match_text, placeholder, 1)
