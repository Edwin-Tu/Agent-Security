from __future__ import annotations

import re
from collections.abc import Callable, Iterable

from elder_privacy_guard.data_masker import mask_email, mask_id, mask_phone
from elder_privacy_guard.models import PIICategory, PIIMatch

CONTEXT_RADIUS = 5
NAME_MASK = "[姓名已遮蔽]"
ADDRESS_MASK = "[地址已遮蔽]"
BIRTH_DATE_MASK = "[出生日期已遮蔽]"

PHONE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9+])(?:\+886[\s-]?9\d{2}[\s-]?\d{3}[\s-]?\d{3}|09\d{2}-?\d{3}-?\d{3})(?![A-Za-z0-9])"
)
NATIONAL_ID_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Z][0-9]{9}(?![A-Za-z0-9])")
EMAIL_PATTERN = re.compile(r"(?<![A-Za-z0-9.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])")
CHINESE_BIRTH_DATE_PATTERN = re.compile(r"(?<!\d)(?:19|20)\d{2}年(?:0?[1-9]|1[0-2])月(?:0?[1-9]|[12]\d|3[01])日")
NUMERIC_BIRTH_DATE_PATTERN = re.compile(r"(?<!\d)(?:19|20)\d{2}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])(?!\d)")
NAME_PATTERNS = (
    re.compile(r"我是([\u4e00-\u9fff]{2,4})(?=[，。,.!?！？；;\s]|$)"),
    re.compile(r"我的名字是([\u4e00-\u9fff]{2,4})(?=[，。,.!?！？；;\s]|$)"),
    re.compile(r"請告訴我([\u4e00-\u9fff]{2,4})的資料"),
)
ADDRESS_MARKERS = ("路", "街", "巷", "弄", "號", "樓")
ADDRESS_PREFIXES = ("地址是", "住址是", "地址：", "住址：", "地址:", "住址:", "我住在", "住在")
ADDRESS_SEGMENT_PATTERN = re.compile(r"[^，。,.!?！？；;\n]+")


def detect_pii(text: str) -> list[PIIMatch]:
    if not text:
        return []

    matches: list[PIIMatch] = []
    matches.extend(_regex_matches(text, PHONE_PATTERN, PIICategory.TAIWAN_PHONE, mask_phone))
    matches.extend(_regex_matches(text, NATIONAL_ID_PATTERN, PIICategory.NATIONAL_ID, mask_id))
    matches.extend(_regex_matches(text, EMAIL_PATTERN, PIICategory.EMAIL, mask_email))
    matches.extend(_name_matches(text))
    matches.extend(_address_matches(text))
    matches.extend(_birth_date_matches(text))

    return sorted(_deduplicate(matches), key=lambda match: (match.start, match.end, match.category.value))


def _regex_matches(
    text: str,
    pattern: re.Pattern[str],
    category: PIICategory,
    masker: Callable[[str], str],
) -> list[PIIMatch]:
    return [
        _build_match(text, category, match.group(0), masker(match.group(0)), match.start(), match.end())
        for match in pattern.finditer(text)
    ]


def _name_matches(text: str) -> list[PIIMatch]:
    matches: list[PIIMatch] = []
    for pattern in NAME_PATTERNS:
        for match in pattern.finditer(text):
            name = match.group(1)
            matches.append(_build_match(text, PIICategory.NAME, name, NAME_MASK, match.start(1), match.end(1)))
    return matches


def _address_matches(text: str) -> list[PIIMatch]:
    matches: list[PIIMatch] = []
    for segment in ADDRESS_SEGMENT_PATTERN.finditer(text):
        value = segment.group(0).strip()
        if not value:
            continue

        start = segment.start() + (len(segment.group(0)) - len(segment.group(0).lstrip()))
        has_address_prefix = False
        for prefix in ADDRESS_PREFIXES:
            if value.startswith(prefix):
                has_address_prefix = True
                start += len(prefix)
                value = value[len(prefix) :]
                break

        value = value.strip()
        if has_address_prefix and value and any(marker in value for marker in ADDRESS_MARKERS):
            matches.append(_build_match(text, PIICategory.ADDRESS, value, ADDRESS_MASK, start, start + len(value)))
    return matches


def _birth_date_matches(text: str) -> list[PIIMatch]:
    return [
        _build_match(text, PIICategory.DATE_OF_BIRTH, match.group(0), BIRTH_DATE_MASK, match.start(), match.end())
        for pattern in (CHINESE_BIRTH_DATE_PATTERN, NUMERIC_BIRTH_DATE_PATTERN)
        for match in pattern.finditer(text)
    ]


def _build_match(
    text: str,
    category: PIICategory,
    original: str,
    masked: str,
    start: int,
    end: int,
) -> PIIMatch:
    return PIIMatch(
        category=category,
        original=original,
        masked=masked,
        start=start,
        end=end,
        context=_context(text, start, end),
    )


def _context(text: str, start: int, end: int) -> str:
    return text[max(0, start - CONTEXT_RADIUS) : min(len(text), end + CONTEXT_RADIUS)]


def _deduplicate(matches: Iterable[PIIMatch]) -> list[PIIMatch]:
    seen: set[tuple[PIICategory, int, int, str]] = set()
    unique: list[PIIMatch] = []
    for match in matches:
        key = (match.category, match.start, match.end, match.original)
        if key in seen:
            continue
        seen.add(key)
        unique.append(match)
    return unique
