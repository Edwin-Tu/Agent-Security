import re

ZERO_WIDTH_PATTERN = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")


def normalize_whitespace(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    cleaned = ZERO_WIDTH_PATTERN.sub("", text)
    cleaned = cleaned.replace("\u3000", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def compact_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    cleaned = ZERO_WIDTH_PATTERN.sub("", text)
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned


def detect_spacing_obfuscation(text: str) -> bool:
    normalized = normalize_whitespace(text)
    if re.search(r"(?:\b[a-zA-Z0-9]\b\s+){2,}\b[a-zA-Z0-9]\b", normalized):
        return True
    if re.search(r"(?:[\u4e00-\u9fff]\s+){2,}[\u4e00-\u9fff]", normalized):
        return True
    return False
