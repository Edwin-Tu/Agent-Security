from dataclasses import dataclass, field


@dataclass
class LeakageMatch:
    asset_id: str
    asset_name: str
    leak_type: str
    match_type: str
    severity: str
    confidence: float
    matched_text: str | None = None
    matched_fragments: list[str] = field(default_factory=list)


@dataclass
class LeakageResult:
    is_leak: bool
    highest_severity: str
    leak_types: list[str]
    matches: list[LeakageMatch]
    recommended_action: str
    redacted_output: str
