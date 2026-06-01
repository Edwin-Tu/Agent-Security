from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class GuardEvent:
    event_id: str | None = None
    timestamp: str | None = None
    session_id: str = "default"
    request_id: str | None = None
    conversation_turn: int = 1
    user_role: str = "guest"
    authorization_status: str = "unknown"
    attack_type: str = "unknown"
    attack_category: str = "unknown"
    matched_patterns: list[str] = field(default_factory=list)
    risk_score: int = 0
    risk_level: str = "low"
    risk_factors: list[str] = field(default_factory=list)
    session_risk_score: int = 0
    policy_action: str = "ALLOW"
    policy_reason: str = ""
    policy_rule_id: str | None = None
    enabled_skills: list[str] = field(default_factory=list)
    skill_results: list[dict[str, Any]] = field(default_factory=list)
    blocked: bool = False
    leakage_detected: bool = False
    leakage_type: str | None = None
    leakage_level: int = 0
    matched_asset_ids: list[str] = field(default_factory=list)
    input_summary: str = ""
    output_summary: str = ""
    final_response_type: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.risk_score < 0:
            self.risk_score = 0
        if self.risk_score > 100:
            self.risk_score = 100

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "conversation_turn": self.conversation_turn,
            "user_role": self.user_role,
            "authorization_status": self.authorization_status,
            "attack_type": self.attack_type,
            "attack_category": self.attack_category,
            "matched_patterns": self.matched_patterns,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "session_risk_score": self.session_risk_score,
            "policy_action": self.policy_action,
            "policy_reason": self.policy_reason,
            "policy_rule_id": self.policy_rule_id,
            "enabled_skills": self.enabled_skills,
            "skill_results": self.skill_results,
            "blocked": self.blocked,
            "leakage_detected": self.leakage_detected,
            "leakage_type": self.leakage_type,
            "leakage_level": self.leakage_level,
            "matched_asset_ids": self.matched_asset_ids,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "final_response_type": self.final_response_type,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GuardEvent":
        return cls(
            event_id=data.get("event_id"),
            timestamp=data.get("timestamp"),
            session_id=data.get("session_id", "default"),
            request_id=data.get("request_id"),
            conversation_turn=data.get("conversation_turn", 1),
            user_role=data.get("user_role", "guest"),
            authorization_status=data.get("authorization_status", "unknown"),
            attack_type=data.get("attack_type", "unknown"),
            attack_category=data.get("attack_category", "unknown"),
            matched_patterns=data.get("matched_patterns", []),
            risk_score=data.get("risk_score", 0),
            risk_level=data.get("risk_level", "low"),
            risk_factors=data.get("risk_factors", []),
            session_risk_score=data.get("session_risk_score", 0),
            policy_action=data.get("policy_action", "ALLOW"),
            policy_reason=data.get("policy_reason", ""),
            policy_rule_id=data.get("policy_rule_id"),
            enabled_skills=data.get("enabled_skills", []),
            skill_results=data.get("skill_results", []),
            blocked=data.get("blocked", False),
            leakage_detected=data.get("leakage_detected", False),
            leakage_type=data.get("leakage_type"),
            leakage_level=data.get("leakage_level", 0),
            matched_asset_ids=data.get("matched_asset_ids", []),
            input_summary=data.get("input_summary", ""),
            output_summary=data.get("output_summary", ""),
            final_response_type=data.get("final_response_type", "unknown"),
            metadata=data.get("metadata", {}),
        )
