import pytest

from elder_privacy_guard.health_data_detector import detect_health_data
from elder_privacy_guard.models import HealthCategory, HealthMatch


def test_detects_condition_keyword():
    matches = detect_health_data("我有糖尿病")

    assert matches == [
        HealthMatch(
            category=HealthCategory.CONDITION,
            original="糖尿病",
            masked="[健康狀況已遮蔽]",
            start=2,
            end=5,
            context="我有糖尿病",
        )
    ]


def test_detects_medication_keyword():
    matches = detect_health_data("我在吃降血壓藥")

    assert matches == [
        HealthMatch(
            category=HealthCategory.MEDICATION,
            original="降血壓藥",
            masked="[用藥已遮蔽]",
            start=3,
            end=7,
            context="我在吃降血壓藥",
        )
    ]


def test_returns_empty_list_for_non_health_text():
    assert detect_health_data("你好") == []


@pytest.mark.parametrize(
    ("text", "keyword"),
    [
        ("我有糖尿病", "糖尿病"),
        ("我有關節炎", "關節炎"),
        ("我有失智", "失智"),
        ("我有帕金森", "帕金森"),
        ("我有腎臟病", "腎臟病"),
        ("我有肝病", "肝病"),
        ("我有肺病", "肺病"),
        ("我有氣喘", "氣喘"),
        ("我有骨質疏鬆", "骨質疏鬆"),
        ("我有白內障", "白內障"),
        ("我有青光眼", "青光眼"),
    ],
)
def test_detects_planned_condition_keywords(text: str, keyword: str):
    matches = detect_health_data(text)
    start: int = text.index(keyword)

    assert matches == [
        HealthMatch(
            category=HealthCategory.CONDITION,
            original=keyword,
            masked="[健康狀況已遮蔽]",
            start=start,
            end=start + len(keyword),
            context=text,
        )
    ]


@pytest.mark.parametrize(
    ("text", "keyword"),
    [
        ("我在吃降血壓藥", "降血壓藥"),
        ("我有吃藥", "吃藥"),
        ("我有服藥", "服藥"),
        ("我有用藥", "用藥"),
        ("我在吃阿斯匹靈", "阿斯匹靈"),
        ("我在補充維他命", "維他命"),
    ],
)
def test_detects_planned_medication_keywords(text: str, keyword: str):
    matches = detect_health_data(text)
    start: int = text.index(keyword)

    assert matches == [
        HealthMatch(
            category=HealthCategory.MEDICATION,
            original=keyword,
            masked="[用藥已遮蔽]",
            start=start,
            end=start + len(keyword),
            context=text,
        )
    ]


def test_boundary_cases_and_multiple_matches():
    assert detect_health_data("") == []
    assert detect_health_data("我沒有糖尿病") == [
        HealthMatch(
            category=HealthCategory.CONDITION,
            original="糖尿病",
            masked="[健康狀況已遮蔽]",
            start="我沒有糖尿病".index("糖尿病"),
            end="我沒有糖尿病".index("糖尿病") + len("糖尿病"),
            context="我沒有糖尿病",
        )
    ]
    assert detect_health_data("吃飯") == []
    assert detect_health_data("藥") == []

    text = "糖尿病和高血壓都要吃降血壓藥，末尾提到維他命"
    matches = detect_health_data(text)

    assert [match.original for match in matches] == ["糖尿病", "高血壓", "降血壓藥", "維他命"]
    assert [match.category for match in matches] == [
        HealthCategory.CONDITION,
        HealthCategory.CONDITION,
        HealthCategory.MEDICATION,
        HealthCategory.MEDICATION,
    ]
    assert matches[0].start == 0
    assert matches[0].end == 3
    assert matches[-1].end == len(text)
    assert all(match.context and match.original in match.context for match in matches)
