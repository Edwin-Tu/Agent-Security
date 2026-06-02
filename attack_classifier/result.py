from dataclasses import dataclass, field


@dataclass
class AttackClassificationResult:
    is_attack: bool
    primary_category: str
    matched_categories: list[str] = field(default_factory=list)
    confidence: float = 0.0
    severity_hint: str = "low"
    matched_rules: list[dict] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    recommended_skill: str | None = None
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "is_attack": self.is_attack,
            "primary_category": self.primary_category,
            "matched_categories": self.matched_categories,
            "confidence": self.confidence,
            "severity_hint": self.severity_hint,
            "matched_rules": self.matched_rules,
            "evidence": self.evidence,
            "recommended_skill": self.recommended_skill,
            "notes": self.notes,
        }
