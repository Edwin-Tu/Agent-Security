from elder_privacy_guard.data_masker import mask_email, mask_id, mask_phone, mask_text
from elder_privacy_guard.models import HealthCategory, HealthMatch, PIICategory, PIIMatch


def test_mask_phone_handles_standard_and_digits_only_formats():
    assert mask_phone('0912-345-678') == '0912****78'
    assert mask_phone('0912345678') == '0912****78'


def test_mask_phone_handles_country_code_and_short_inputs():
    assert mask_phone('+886 912 345 678') == '886****78'
    assert mask_phone('091234') == '****'


def test_mask_id_masks_standard_and_short_inputs():
    assert mask_id('A123456789') == 'A1****789'
    assert mask_id('A123') == '****'


def test_mask_email_masks_standard_short_and_invalid_inputs():
    assert mask_email('test@example.com') == 't***@example.com'
    assert mask_email('a@example.com') == 'a***@example.com'
    assert mask_email('not-an-email') == '***@***'


def test_mask_text_replaces_matches_from_end_without_leaking_original_values():
    text = 'Call 0912-345-678, email test@example.com, and note 糖尿病.'
    pii_matches = [
        PIIMatch(
            category=PIICategory.TAIWAN_PHONE,
            original='0912-345-678',
            masked='0912****78',
            start=text.index('0912-345-678'),
            end=text.index('0912-345-678') + len('0912-345-678'),
            context=text,
        ),
        PIIMatch(
            category=PIICategory.EMAIL,
            original='test@example.com',
            masked='t***@example.com',
            start=text.index('test@example.com'),
            end=text.index('test@example.com') + len('test@example.com'),
            context=text,
        ),
    ]
    health_matches = [
        HealthMatch(
            category=HealthCategory.CONDITION,
            original='糖尿病',
            masked='[健康狀況已遮蔽]',
            start=text.index('糖尿病'),
            end=text.index('糖尿病') + len('糖尿病'),
            context=text,
        ),
    ]

    sanitized = mask_text(text, pii_matches, health_matches)

    assert sanitized == 'Call 0912****78, email t***@example.com, and note [健康狀況已遮蔽].'
    assert '0912-345-678' not in sanitized
    assert 'test@example.com' not in sanitized
    assert '糖尿病' not in sanitized


def test_mask_text_returns_original_for_empty_matches_and_empty_text_for_empty_input():
    assert mask_text('hello world', [], []) == 'hello world'
    assert mask_text('', [], []) == ''


def test_mask_short_phone_id_and_email_boundaries():
    assert mask_phone('1234') == '****'
    assert mask_id('AB') == '****'
    assert mask_email('a@b.co') == 'a***@b.co'
    assert mask_email('invalid') == '***@***'


def test_mask_text_multiple_replacements_preserve_order_from_end():
    text = 'A123456789 and 0912345678'
    pii_matches = [
        PIIMatch(
            category=PIICategory.NATIONAL_ID,
            original='A123456789',
            masked='A1****789',
            start=0,
            end=len('A123456789'),
            context=text,
        ),
        PIIMatch(
            category=PIICategory.TAIWAN_PHONE,
            original='0912345678',
            masked='0912****78',
            start=text.index('0912345678'),
            end=len(text),
            context=text,
        ),
    ]

    assert mask_text(text, pii_matches, []) == 'A1****789 and 0912****78'
