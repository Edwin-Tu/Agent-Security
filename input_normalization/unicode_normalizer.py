import re
import unicodedata

HOMOGLYPH_MAP = {
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "х": "x",
    "Α": "A",
    "Β": "B",
    "Ο": "O",
    "Ι": "I",
    "Ј": "J",
    "а": "a",
    "А": "A",
    "Е": "E",
    "О": "O",
    "Р": "P",
    "С": "C",
    "Х": "X",
    "і": "i",
    "І": "I",
    "ο": "o",
    "Ο": "O",
    "с": "c",
    "С": "C",
    "м": "m",
    "М": "M",
}
ZERO_WIDTH_PATTERN = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")


def remove_zero_width_chars(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return ZERO_WIDTH_PATTERN.sub("", text)


def fullwidth_to_halfwidth(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    result = []
    for ch in text:
        code = ord(ch)
        if code == 0x3000:
            result.append(" ")
        elif 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        else:
            result.append(ch)
    return "".join(result)


def replace_homoglyphs(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return "".join(HOMOGLYPH_MAP.get(ch, ch) for ch in text)


def normalize_unicode_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    normalized = unicodedata.normalize("NFKC", text)
    normalized = fullwidth_to_halfwidth(normalized)
    normalized = remove_zero_width_chars(normalized)
    normalized = replace_homoglyphs(normalized)
    return normalized.casefold()


def detect_confusable(text: str) -> tuple[list[str], list[dict]]:
    if not isinstance(text, str):
        text = str(text)

    normalized = unicodedata.normalize("NFKC", text)
    normalized = fullwidth_to_halfwidth(normalized)
    normalized = remove_zero_width_chars(normalized)
    replaced = replace_homoglyphs(normalized)

    flags: list[str] = []
    transformations: list[dict] = []

    if replaced != normalized:
        flags.append("unicode_confusable_detected")
        for original_char, mapped_char in zip(normalized, replaced):
            if original_char != mapped_char:
                transformations.append(
                    {
                        "type": "unicode_confusable",
                        "from": original_char,
                        "to": mapped_char,
                        "reason": f"{unicodedata.name(original_char, original_char)} mapped to {unicodedata.name(mapped_char, mapped_char)}",
                    }
                )

    return flags, transformations
