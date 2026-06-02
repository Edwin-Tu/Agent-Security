from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PolicyContext:
    normalized_prompt: str
    attack_category: Optional[str]
    risk_score: int
    risk_level: str
    matched_assets: List[dict]
    user_role: str
    is_authorized: bool
    session_risk_score: int
    input_guard_flags: List[str]
    classifier_confidence: float
    history_flags: List[str]
