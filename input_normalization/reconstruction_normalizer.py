import re


RECONSTRUCTION_PATTERNS = [
    (
        "asks_for_character_position",
        re.compile(
            r"第\s*(?:\d+|[一二三四五六七八九十百零兩]+)\s*(?:個字元|個字|位|字)|character\s*\d+|position\s*\d+",
            re.IGNORECASE,
        ),
    ),
    (
        "asks_for_prefix",
        re.compile(r"前\s*(?:\d+|[一二三四五六七八九十百零兩]+)\s*(?:碼|字)|prefix", re.IGNORECASE),
    ),
    (
        "asks_for_suffix",
        re.compile(
            r"最後\s*(?:\d+|[一二三四五六七八九十百零兩]+)\s*(?:碼|字)|末尾|suffix",
            re.IGNORECASE,
        ),
    ),
    (
        "asks_for_partial_secret",
        re.compile(r"分段|部分|partial|片段", re.IGNORECASE),
    ),
]


def detect_reconstruction_patterns(text: str) -> tuple[bool, list[dict]]:
    if not isinstance(text, str):
        text = str(text)

    detected = False
    transformations: list[dict] = []
    for pattern_name, pattern in RECONSTRUCTION_PATTERNS:
        match = pattern.search(text)
        if match:
            detected = True
            transformations.append(
                {
                    "type": pattern_name,
                    "matched_text": match.group(0),
                }
            )

    return detected, transformations
