from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RiskScoreResult:
    risk_score: int
    risk_level: str
    recommended_action: str
    risk_factors: List[str]
    matched_assets: List[Dict[str, Any]]
    triggered_rules: List[str]
    attack_category: Optional[str] = None
    confidence: Optional[float] = None
    requires_authorization: bool = False
    enable_strict_runtime_monitor: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "recommended_action": self.recommended_action,
            "risk_factors": self.risk_factors,
            "matched_assets": self.matched_assets,
            "triggered_rules": self.triggered_rules,
            "attack_category": self.attack_category,
            "confidence": self.confidence,
            "requires_authorization": self.requires_authorization,
            "enable_strict_runtime_monitor": self.enable_strict_runtime_monitor,
        }
