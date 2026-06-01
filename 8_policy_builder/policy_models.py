from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyBuildInput:
    request_id: str
    original_prompt: str
    normalized_prompt: str
    user_role: str
    attack_category: str
    risk_score: int
    policy_action: str
    matched_assets: list
    enabled_skills: list
    skill_defense_results: list
    session_risk: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class RequestProtectionPolicy:
    request_id: str
    action: str
    risk_score: int
    risk_level: str
    user_role: str
    attack_category: str

    protected_asset_ids: list = field(default_factory=list)
    protected_asset_names: list = field(default_factory=list)
    protected_asset_types: list = field(default_factory=list)
    protection_modes: list = field(default_factory=list)

    allowed_response_scope: list = field(default_factory=list)
    denied_response_scope: list = field(default_factory=list)
    blocked_disclosure_types: list = field(default_factory=list)

    enabled_skills: list = field(default_factory=list)
    restricted_tokens: list = field(default_factory=list)
    blocked_transformations: list = field(default_factory=list)

    require_authorization: bool = False
    runtime_monitoring_enabled: bool = True
    runtime_monitoring_mode: str = "normal"
    interrupt_on_match: bool = False

    output_verification_enabled: bool = True
    verify_exact: bool = True
    verify_partial: bool = False
    verify_encoding: bool = False
    verify_translation: bool = False
    verify_reconstruction: bool = False

    refusal_strategy: str = "safe_refusal"
    safe_alternatives: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
