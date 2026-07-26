from dataclasses import asdict

from elder_privacy_guard.models import (
    Decision,
    HealthCategory,
    HealthMatch,
    HealthSummary,
    PIICategory,
    PIIMatch,
    PIISummary,
    PrivacyDecision,
)


def test_decision_enum_values():
    assert Decision.PASS.value == "PASS"
    assert Decision.SANITIZE.value == "SANITIZE"
    assert Decision.REJECT.value == "REJECT"


def test_pii_category_enum_values():
    assert PIICategory.TAIWAN_PHONE.value == "taiwan_phone"
    assert PIICategory.NATIONAL_ID.value == "national_id"
    assert PIICategory.EMAIL.value == "email"
    assert PIICategory.NAME.value == "name"
    assert PIICategory.ADDRESS.value == "address"
    assert PIICategory.DATE_OF_BIRTH.value == "date_of_birth"


def test_health_category_enum_values():
    assert HealthCategory.CONDITION.value == "condition"
    assert HealthCategory.MEDICATION.value == "medication"


def test_pii_match_keeps_raw_and_masked_details():
    match = PIIMatch(
        category=PIICategory.EMAIL,
        original="alice@example.com",
        masked="a***@example.com",
        start=5,
        end=22,
        context="Contact alice@example.com for follow up.",
    )

    assert match.category is PIICategory.EMAIL
    assert match.original == "alice@example.com"
    assert match.masked == "a***@example.com"
    assert match.start == 5
    assert match.end == 22
    assert match.context == "Contact alice@example.com for follow up."


def test_health_match_keeps_raw_and_masked_details():
    match = HealthMatch(
        category=HealthCategory.CONDITION,
        original="diabetes",
        masked="[condition]",
        start=0,
        end=8,
        context="Patient has diabetes.",
    )

    assert match.category is HealthCategory.CONDITION
    assert match.original == "diabetes"
    assert match.masked == "[condition]"
    assert match.start == 0
    assert match.end == 8
    assert match.context == "Patient has diabetes."


def test_public_summaries_expose_only_category_and_masked_values():
    pii_summary = PIISummary(
        category=PIICategory.NATIONAL_ID,
        masked="A123***789",
    )
    health_summary = HealthSummary(
        category=HealthCategory.MEDICATION,
        masked="[medication]",
    )

    assert asdict(pii_summary) == {
        "category": PIICategory.NATIONAL_ID,
        "masked": "A123***789",
    }
    assert asdict(health_summary) == {
        "category": HealthCategory.MEDICATION,
        "masked": "[medication]",
    }
    assert not hasattr(pii_summary, "original")
    assert not hasattr(health_summary, "original")


def test_privacy_decision_defaults_to_empty_lists_and_metadata():
    decision = PrivacyDecision(
        decision=Decision.PASS,
        sanitized_text="hello",
    )

    assert decision.decision is Decision.PASS
    assert decision.sanitized_text == "hello"
    assert decision.reasons == []
    assert decision.pii_summaries == []
    assert decision.health_summaries == []
    assert decision.agent_security_used is False
    assert decision.metadata == {}
    assert getattr(decision, "_pii_matches") == []
    assert getattr(decision, "_health_matches") == []
    assert "_pii_matches" not in repr(decision)
    assert "_health_matches" not in repr(decision)
