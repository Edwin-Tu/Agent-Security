from __future__ import annotations

from elder_privacy_guard.models import HealthCategory, HealthMatch

CONDITION_KEYWORDS = (
    "糖尿病",
    "關節炎",
    "失智",
    "高血壓",
    "心臟病",
    "失智症",
    "帕金森",
    "腎臟病",
    "肝病",
    "肺病",
    "氣喘",
    "骨質疏鬆",
    "白內障",
    "青光眼",
    "中風",
    "癌症",
)

MEDICATION_KEYWORDS = (
    "吃藥",
    "服藥",
    "用藥",
    "降血壓藥",
    "降血糖藥",
    "安眠藥",
    "阿斯匹靈",
    "維他命",
    "胰島素",
    "抗生素",
)

CONDITION_MASK = "[健康狀況已遮蔽]"
MEDICATION_MASK = "[用藥已遮蔽]"
CONTEXT_RADIUS = 5


def detect_health_data(text: str) -> list[HealthMatch]:
    if not text:
        return []

    matches: list[HealthMatch] = []

    for keyword in CONDITION_KEYWORDS:
        matches.extend(_find_matches(text, keyword, HealthCategory.CONDITION, CONDITION_MASK))

    for keyword in MEDICATION_KEYWORDS:
        matches.extend(_find_matches(text, keyword, HealthCategory.MEDICATION, MEDICATION_MASK))

    return sorted(matches, key=lambda match: (match.start, match.end, match.original))


def _find_matches(
    text: str,
    keyword: str,
    category: HealthCategory,
    masked: str,
) -> list[HealthMatch]:
    results: list[HealthMatch] = []
    start = 0

    while True:
        index = text.find(keyword, start)
        if index == -1:
            break

        end = index + len(keyword)
        context_start = max(0, index - CONTEXT_RADIUS)
        context_end = min(len(text), end + CONTEXT_RADIUS)

        results.append(
            HealthMatch(
                category=category,
                original=keyword,
                masked=masked,
                start=index,
                end=end,
                context=text[context_start:context_end],
            )
        )
        start = end

    return results
