from dataclasses import dataclass, field


@dataclass
class GuardDecision:
    allowed: bool
    action: str
    risk_score: int
    attack_type: str | None = None
    reason: str | None = None
    matched_assets: list[dict] = field(default_factory=list)
    intent_result: dict | None = None
