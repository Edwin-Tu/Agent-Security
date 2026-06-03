from dataclasses import dataclass, field


@dataclass
class IntentResult:
    intent: str
    operation: str
    scope: str
    disclosure_mode: str
    asset_reference_type: str
    asset_type: str | None = None
    risk_score: int = 0
    confidence: float = 0.0
    reasons: list[str] = field(default_factory=list)
    matched_features: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "operation": self.operation,
            "scope": self.scope,
            "disclosure_mode": self.disclosure_mode,
            "asset_reference_type": self.asset_reference_type,
            "asset_type": self.asset_type,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "matched_features": self.matched_features,
            "metadata": self.metadata,
        }
