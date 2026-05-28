import re

SYMBOL_SEPARATOR_PATTERN = re.compile(r"(?<=[A-Za-z0-9\u4e00-\u9fff])[-_./*\\]+(?=[A-Za-z0-9\u4e00-\u9fff])")
ZERO_WIDTH_PATTERN = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")


def strip_symbols_and_compact(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    cleaned = ZERO_WIDTH_PATTERN.sub("", text)
    cleaned = SYMBOL_SEPARATOR_PATTERN.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def detect_symbol_obfuscation(text: str, stripped: str) -> bool:
    if not isinstance(text, str):
        text = str(text)
    if not isinstance(stripped, str):
        stripped = str(stripped)

    return text != stripped and bool(re.search(r"[-_./*\\]", text))
