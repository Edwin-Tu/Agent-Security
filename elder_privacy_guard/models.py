from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Decision(str, Enum):
    PASS = "PASS"
    SANITIZE = "SANITIZE"
    REJECT = "REJECT"


class PIICategory(str, Enum):
    TAIWAN_PHONE = "taiwan_phone"
    NATIONAL_ID = "national_id"
    EMAIL = "email"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"


class HealthCategory(str, Enum):
    CONDITION = "condition"
    MEDICATION = "medication"


@dataclass(frozen=True, slots=True)
class PIIMatch:
    category: PIICategory
    original: str
    masked: str
    start: int
    end: int
    context: str | None = None


@dataclass(frozen=True, slots=True)
class HealthMatch:
    category: HealthCategory
    original: str
    masked: str
    start: int
    end: int
    context: str | None = None


@dataclass(frozen=True, slots=True)
class PIISummary:
    category: PIICategory
    masked: str


@dataclass(frozen=True, slots=True)
class HealthSummary:
    category: HealthCategory
    masked: str


@dataclass(slots=True)
class PrivacyDecision:
    decision: Decision
    sanitized_text: str
    reasons: list[str] = field(default_factory=list)
    pii_summaries: list[PIISummary] = field(default_factory=list)
    health_summaries: list[HealthSummary] = field(default_factory=list)
    agent_security_used: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
    policy_action: str = "ALLOW"
    owasp_risks: list[str] = field(default_factory=list)
    model_called: bool = True
    _pii_matches: list[PIIMatch] = field(default_factory=list, repr=False)
    _health_matches: list[HealthMatch] = field(default_factory=list, repr=False)
