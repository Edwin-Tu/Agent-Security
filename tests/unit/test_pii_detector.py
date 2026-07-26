import pytest

from elder_privacy_guard.data_masker import mask_text
from elder_privacy_guard.models import PIICategory, PIIMatch
from elder_privacy_guard.pii_detector import detect_pii


def test_detects_phone_id_and_email_with_masker_values_and_spans():
    text = "電話0912-345-678，身分證A123456789，信箱test@example.com"

    matches = detect_pii(text)

    assert matches == [
        PIIMatch(
            category=PIICategory.TAIWAN_PHONE,
            original="0912-345-678",
            masked="0912****78",
            start=text.index("0912-345-678"),
            end=text.index("0912-345-678") + len("0912-345-678"),
            context="電話0912-345-678，身分證A",
        ),
        PIIMatch(
            category=PIICategory.NATIONAL_ID,
            original="A123456789",
            masked="A1****789",
            start=text.index("A123456789"),
            end=text.index("A123456789") + len("A123456789"),
            context="8，身分證A123456789，信箱te",
        ),
        PIIMatch(
            category=PIICategory.EMAIL,
            original="test@example.com",
            masked="t***@example.com",
            start=text.index("test@example.com"),
            end=text.index("test@example.com") + len("test@example.com"),
            context="89，信箱test@example.com",
        ),
    ]


def test_detects_taiwan_mobile_variants():
    text = "手機0912345678，海外格式+886 912 345 678"

    matches = detect_pii(text)

    assert [match.original for match in matches] == ["0912345678", "+886 912 345 678"]
    assert [match.masked for match in matches] == ["0912****78", "886****78"]
    assert all(match.category is PIICategory.TAIWAN_PHONE for match in matches)
    assert mask_text(text, matches, []) == "手機0912****78，海外格式886****78"


def test_detects_names_only_from_required_contexts():
    text = "我是王小明。我的名字是林美玲。請告訴我陳大華的資料。張先生沒有上下文"

    matches = detect_pii(text)

    assert [(match.original, match.start, match.end) for match in matches] == [
        ("王小明", text.index("王小明"), text.index("王小明") + len("王小明")),
        ("林美玲", text.index("林美玲"), text.index("林美玲") + len("林美玲")),
        ("陳大華", text.index("陳大華"), text.index("陳大華") + len("陳大華")),
    ]
    assert all(match.category is PIICategory.NAME for match in matches)
    assert all(match.masked == "[姓名已遮蔽]" for match in matches)


def test_detects_address_without_unrelated_trailing_clause():
    text = "地址是台北市大安區和平東路二段100號3樓，請明天提醒我。"


    matches = detect_pii(text)

    address = "台北市大安區和平東路二段100號3樓"
    assert matches == [
        PIIMatch(
            category=PIICategory.ADDRESS,
            original=address,
            masked="[地址已遮蔽]",
            start=text.index(address),
            end=text.index(address) + len(address),
            context="地址是台北市大安區和平東路二段100號3樓，請明天提",
        )
    ]
    assert "請明天提醒我" not in matches[0].original


def test_detects_birth_dates_in_chinese_iso_and_slash_formats():
    text = "生日1940年1月2日，另一個出生日期1940-01-02，備註1940/01/02"

    matches = detect_pii(text)

    assert [(match.original, match.masked) for match in matches] == [
        ("1940年1月2日", "[出生日期已遮蔽]"),
        ("1940-01-02", "[出生日期已遮蔽]"),
        ("1940/01/02", "[出生日期已遮蔽]"),
    ]
    assert all(match.category is PIICategory.DATE_OF_BIRTH for match in matches)
    assert mask_text(text, matches, []) == "生日[出生日期已遮蔽]，另一個出生日期[出生日期已遮蔽]，備註[出生日期已遮蔽]"


def test_sorts_matches_by_start_end_and_category_value():
    text = "我是王小明，電話0912345678，生日1940/01/02"


    matches = detect_pii(text)


    assert matches == sorted(matches, key=lambda match: (match.start, match.end, match.category.value))
    assert mask_text(text, matches, []) == "我是[姓名已遮蔽]，電話0912****78，生日[出生日期已遮蔽]"


@pytest.mark.parametrize("text", ["", "   ", "hello world"])
def test_returns_empty_list_for_non_pii_boundary_inputs(text: str):
    assert detect_pii(text) == []


@pytest.mark.parametrize("phone", ["+886-912-345-678", "+886912345678"])
def test_detects_international_phone_variants_with_hyphens_or_no_spaces(phone: str):
    text = f"電話卡號碼是{phone}"

    matches = detect_pii(text)

    assert [(match.category, match.original, match.masked) for match in matches] == [
        (PIICategory.TAIWAN_PHONE, phone, "886****78")
    ]


@pytest.mark.parametrize("text", ["a123456789", "1234567890"])
def test_does_not_detect_lowercase_id_or_pure_numeric_id(text: str):
    assert detect_pii(text) == []


@pytest.mark.parametrize("email", ["user@domain", "user@@domain.com"])
def test_does_not_detect_invalid_email_addresses(email: str):
    assert detect_pii(f"信箱是{email}") == []


def test_detects_pii_inside_long_text():
    text = f"{'長照提醒' * 200}聯絡電話0912345678{'請回覆' * 200}"

    matches = detect_pii(text)

    assert [(match.category, match.original) for match in matches] == [
        (PIICategory.TAIWAN_PHONE, "0912345678")
    ]


def test_reports_correct_spans_for_pii_at_beginning_and_end():
    text = "0912345678需要回電給test@example.com"

    matches = detect_pii(text)

    phone, email = matches

    assert (phone.original, phone.start, phone.end) == ("0912345678", 0, len("0912345678"))
    assert (email.original, email.start, email.end) == (
        "test@example.com",
        text.index("test@example.com"),
        len(text),
    )


def test_does_not_detect_already_masked_phone():
    assert detect_pii("我的電話是0912****78") == []


def test_detects_phone_card_scenario():
    text = "我有三隻0912-345-678的電話卡"

    matches = detect_pii(text)

    assert [(match.category, match.original) for match in matches] == [
        (PIICategory.TAIWAN_PHONE, "0912-345-678")
    ]
